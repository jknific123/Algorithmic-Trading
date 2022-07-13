import pandas as pd
import datetime as datetime
import numpy as np

from mixed_strategies.moja_tehnicna.moja_tehnicna import mixed_tehnical_strategy
from mixed_strategies.moja_tehnicna.moja_tehnicna_grafi import profit_graph
from utility import utils as util


pd.options.mode.chained_assignment = None  # default='warn'


def zacetniDf(data):
    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako
    # kreiramo nova stolpca za buy/sell signale
    data['Buy'] = np.nan
    data['Sell'] = np.nan
    data['Cash'] = 0
    data['Shares'] = 0
    data['Profit'] = 0
    data['Total'] = 0
    data['Ticker'] = ""
    data['Buy-Signal'] = np.nan
    data['Sell-Signal'] = np.nan
    data["Buy-date"] = ""
    data["Sell-date"] = ""

    return data


def setObdobja(startObdobja, endObdobja, dowTickersObdobja):
    # hardcodam za testno mnozico
    obdobja = []

    if startObdobja == "2017-02-02":
        obdobja.append(startObdobja)

    for x in dowTickersObdobja:

        if startObdobja <= x < endObdobja:  # zna bit da je tuki treba se = dat
            obdobja.append(x)

    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if endObdobja > zadnjeObdobje:
        obdobja.append(endObdobja)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    print("Obdobja: ", obdobja)
    return obdobja


def backtest(start, end, short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer, dowTickers, stockPricesDB, hold_obdobje):
    # nastavimo obdobja
    obdobja = setObdobja(startObdobja=start, endObdobja=end, dowTickersObdobja=dowTickers)

    portfolio = {}
    starting_companies = []

    for i in range(0, len(obdobja) - 1):  # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetnoObdobje = obdobja[i]
        koncnoObdobje = obdobja[i + 1]
        print(i, zacetnoObdobje, "+", koncnoObdobje)

        # zacetek
        if zacetnoObdobje == start:
            # hardcodam za zacetno od ucne in testne mnozice
            print("V zacetnem")

            if zacetnoObdobje == "2005-11-21":
                starting_companies = dowTickers[zacetnoObdobje]["all"]
            elif zacetnoObdobje == "2017-02-02":
                starting_companies = dowTickers["2015-03-19"]["all"]

            # trejdamo z all od zacetnegaObdobja
            for x in starting_companies:
                print("Company: ", x)

                # izjema za podjetje GM, za katerega nimam podatkov, zato samo naredim prazen dataframe
                if x == "GM":
                    # pridobim df od podjetja HD in zbrišem podatke tako da je potem prazen
                    prazen = stockPricesDB.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker="HD")
                    prazen = prazen[['Close', 'High', 'Low']].copy()
                    prazen = zacetniDf(prazen)
                    prazen["Close"] = 0
                    return_df = mixed_tehnical_strategy(short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer,
                                                        prazen, x, 0, 0, True, hold_obdobje)
                    portfolio[x] = return_df

                elif x != "GM":
                    data = stockPricesDB.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker=x)
                    data = data[['Close', 'High', 'Low']].copy()
                    data = zacetniDf(data)  # dodamo stolpce
                    return_df = mixed_tehnical_strategy(short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer,
                                                        data, x, 0, 0, True, hold_obdobje)
                    portfolio[x] = return_df

            print(portfolio.keys())
            print(starting_companies)
            print(dowTickers["2005-11-21"]["all"])
            print("LEN: ", len(portfolio))

        # ce nismo na zacetku gremo cez removed in added in naredimo menjave ter trejdamo za naslednje obdobje
        elif zacetnoObdobje != start:

            dodani = []
            # gremo najprej cez removed in opravimo zamenjave
            for odstranjenTicker in dowTickers[zacetnoObdobje]["removed"]:

                starting_companies = portfolio.keys()

                if odstranjenTicker in starting_companies:  # odstranjenTicker je v trenutnem portfoliu -> ga zamenjamo z isto ležečim tickerjem iz added

                    # zamenjamo odstranjenTicker z isto ležečim tickerjem iz added
                    nov_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    print(odstranjenTicker, "->", nov_ticker)
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = (real_start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # adding one day
                    modified_date = (datetime.datetime.strptime(plus_one_start_date, "%Y-%m-%d") - datetime.timedelta(days=(long_period * 2))).strftime(
                        "%Y-%m-%d")  # odstevamo long period, da dobimo dovolj podatkov
                    print('plus_one_start_date', plus_one_start_date)
                    print('modified_date', modified_date)
                    new_df = stockPricesDB.getCompanyStockDataInRange(date_from=modified_date, date_to=koncnoObdobje, companyTicker=nov_ticker)

                    new_df = new_df[['Close', 'High', 'Low']].copy()
                    new_df = zacetniDf(new_df)
                    ex_df = portfolio[odstranjenTicker]

                    if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].at[plus_one_start_date] = ex_df["Cash"][-1]

                    elif ex_df["Shares"][-1] > 0:  # moramo prodat delnice in jih investirat v podjetje, ki ga dodajamo

                        # prodaj vse delnic izracunaj profit in placaj davek
                        sellPrice = util.fees(ex_df['Shares'].to_numpy()[-1] * ex_df['Close'].to_numpy()[-1])  # delnice v denar, obracunamo fees
                        profitPredDavkom = util.profit(ex_df['Buy'].to_numpy()[-1], sellPrice)  # izracunamo profit pred davkom

                        # ce je dobicek pred davkom pozitiven zaracunamo davek na dobicek in ga odstejemo od sellPrice, da dobimo ostanek
                        if profitPredDavkom > 0:
                            sellPrice = sellPrice - util.taxes(profitPredDavkom)  # popravimo sellPrice, tako da obracunamo davek

                        ex_df['Sell'].to_numpy()[-1] = sellPrice  # zapisemo sell price
                        ex_df['Profit'].to_numpy()[-1] = util.profit(ex_df['Buy'].to_numpy()[-1], sellPrice)
                        # za graf trgovanja TODO -> nisem siguren da to sploh rabim tukaj
                        ex_df['Sell-Signal'].to_numpy()[-1] = ex_df["Close"].to_numpy()[-1]
                        ex_df["Sell-date"].to_numpy()[-1] = ex_df.index[-1]  # zapisem datum nakupa
                        ex_df['Buy'].to_numpy()[-1] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                        ex_df['Buy-date'].to_numpy()[-1] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell

                        ex_df['Cash'].to_numpy()[-1] = ex_df['Cash'].to_numpy()[-1] + sellPrice  # posodbi cash
                        ex_df['Shares'].to_numpy()[-1] = 0
                        # updejtamo total
                        ex_df['Total'].to_numpy()[-1] = ex_df['Cash'].to_numpy()[-1]

                        # prejsni df je posodobljen in delnice so prodane, samo prepisemo Cash v new_df
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].at[plus_one_start_date] = ex_df["Cash"][-1]

                    odvec = new_df[:plus_one_start_date]
                    starting_index = len(odvec) - 1

                    # startamo trading algo
                    # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje
                    new_returns = mixed_tehnical_strategy(short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer,
                                                          new_df, nov_ticker, starting_index, 0, True, hold_obdobje)

                    added_returns = new_returns[plus_one_start_date:]  # iz new_returns vzamemo del dataframa od plus_one_start_date do konca in ga nato prilepimo v df iz portfolia
                    concat_returns = pd.concat([ex_df, added_returns])
                    # naredimo nov slovar-portfolio iz prejsnjega s tem, da je key trenutnega df nov_ticker namesto odstranjenTicker
                    new_portfolio = {nov_ticker if k == odstranjenTicker else k: v for k, v in portfolio.items()}
                    new_portfolio[nov_ticker] = concat_returns  # shranimo nov podaljšan dataframe v nov portfolio
                    portfolio = new_portfolio
                    dodani.append(nov_ticker)
                    print("Po izlocanju: ", odstranjenTicker)
                    print(sorted(portfolio.keys()))

            # smo updejtali vse removed, zdej pa samo nadaljujemo trejdanej z usemi ostalimi

            ostali = set(portfolio.keys()) - set(dodani)
            ostali = sorted(list(ostali))
            print("Ostali tickerji: ", sorted(ostali))
            for ostaliTicker in ostali:

                real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                plus_one_start_date = (real_start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # adding one day

                ostaliTickerDataframe = portfolio[ostaliTicker]
                zadnji_signal = 0
                if ostaliTickerDataframe['Shares'].to_numpy()[-1] == 0:
                    zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                elif ostaliTickerDataframe['Shares'].to_numpy()[-1] > 0:
                    zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                print("Trenutni ostali ticker: ", ostaliTicker)
                company = ostaliTicker
                if ostaliTicker == "GM":
                    company = "HD"  # ce se prav spomnem se uzame HD samo zato, da se dobi ok velik df, ker za GM ne morem
                new_data = stockPricesDB.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=company)
                if ostaliTicker == "GM":
                    new_data["Close"] = 0
                new_data = new_data[['Close', 'High', 'Low']].copy()
                starting_index = len(ostaliTickerDataframe)

                concat_data = pd.concat([ostaliTickerDataframe, new_data])

                new_ostaliTickerDataframe = mixed_tehnical_strategy(short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer,
                                                                    concat_data, f"new{ostaliTicker}", starting_index, zadnji_signal, False, hold_obdobje)
                portfolio[ostaliTicker] = new_ostaliTickerDataframe

    totals = prikaziPodatkePortfolia(portfolio, startIzpis=start, endIzpis=end)

    return totals


def prikaziPodatkePortfolia(portfolio, startIzpis, endIzpis):
    # gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        tickerTotals = portfolio[ticker]

        # util.preveriPravilnostDatumov(ticker, portfolio)

        allShares[ticker] = tickerTotals['Shares'].to_numpy()[-1]

        if count == 0:
            allFunds = tickerTotals[['Total']].copy()
        else:
            allFunds['Total'] = allFunds['Total'].add(tickerTotals['Total'])  # , fill_value=1000

        count += 1

    # se izpis podatkov portfolia
    startFunds = len(portfolio) * util.getMoney()
    endFunds = allFunds['Total'].to_numpy()[-1]

    profit_graph(allFunds, 1, "Portfolio", round(endFunds, 4))

    print("Zacetna sredstva: ", startFunds, "$")
    print("Skupna sredstva portfolia: ", round(endFunds, 4), "$")
    print("Profit: ", round(endFunds - startFunds, 4), "$")
    print("Kumulativni donos v procentih: ", round((endFunds - startFunds) / startFunds, 4) * 100, "%")

    print("Delnice, ki jih še imamo v portfoliu:")
    for key, value in allShares.items():
        print(key, " : ", value)

    return allFunds


# MACD crossover + Stohastic oscilator + Bollinger bands strategy
# datetmie = leto, mesec, dan

# MACD
#short_period = 12
#long_period = 26
#signal_period = 9

# Stohastic oscilator
#high_low_period = 14
#d_sma_period = 3

# Bollinger bands
#sma_period = 20
#bands_multiplayer = 2

