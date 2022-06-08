import math
import pandas as pd
import datetime as datetime
import numpy as np

from functools import cache

from technical_strategies.sma_crossover.sma_grafi import profit_graph, SMA_trading_graph, plotShares
from utility import utils as util

pd.options.mode.chained_assignment = None  # default='warn'


@cache
def days_between(d1, d2):
    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def sma_crossover(sPeriod, lPeriod, df, ticker, starting_index, status, odZacetkaAliNe, holdObdobje):

    # naredimo/napolnimo nova stolpca za oba SMA
    df[f'SMA-{sPeriod}'] = df['Close'].rolling(window=sPeriod, min_periods=1, center=False).mean()
    df[f'SMA-{lPeriod}'] = df['Close'].rolling(window=lPeriod, min_periods=1, center=False).mean()

    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo
    if starting_index == 0:  # before :   odZacetkaAliNe is True
        df = df[lPeriod:]

    # za racunanje davka na dobiček
    sellPrice = 0

    # check -> zato da nimamo dveh zapovrstnih buy/sell signalov: 2 = buy, 1 = sell
    # status = 0 -> zacnemo od zacetka

    # 1 -> zacenjamo od tam ko je bil zadnji signal sell
    # 2 -> zacenjamo od tam ko je bil zadnji signal buy
    check = status
    for x in range(starting_index, len(df)):

        # filing shares, cash, total
        if (x - 1) >= 0:  # preverimo ce smo znotraj tabele
            df['Shares'].to_numpy()[x] = np.nan_to_num(df['Shares'].to_numpy()[x - 1])  # prenesemo prejsnje st delnic naprej

            if x != starting_index:  # za izjeme ko dodamo nov ticker in ne smemo zbrisat starting cash
                df['Cash'].to_numpy()[x] = np.nan_to_num(df['Cash'].to_numpy()[x - 1])  # prenesemo prejsnji Cash naprej
            elif x == starting_index and odZacetkaAliNe is False:  # takrat ko je isto podjetje kot prej
                df['Cash'].to_numpy()[x] = np.nan_to_num(df['Cash'].to_numpy()[x - 1])  # prenesemo prejsnji Cash naprej

            df['Total'].to_numpy()[x] = (df['Cash'].to_numpy()[x] + util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x]))  # izracunamo total
            df['Ticker'].to_numpy()[x] = ticker
            df['Buy'].to_numpy()[x] = df['Buy'].to_numpy()[x - 1]
            df['Sell'].to_numpy()[x] = df['Sell'].to_numpy()[x - 1]
            df['Buy-date'].to_numpy()[x] = df['Buy-date'].to_numpy()[x - 1]
            df['Sell-date'].to_numpy()[x] = df['Sell-date'].to_numpy()[x - 1]


        else:  # zacetek tabele -> inicializacija vrednosti
            if df['Cash'].to_numpy()[x] == 0:  # nimamo se denarja
                df['Cash'].to_numpy()[x] = util.getMoney()
            df['Total'].to_numpy()[x] = (df['Cash'].to_numpy()[x] + util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x]))
            df['Ticker'].to_numpy()[x] = ticker

        pretekli_dnevi_buy = 0
        if df["Buy-date"].to_numpy()[x] != "":
            pretekli_dnevi_buy = days_between(df["Buy-date"].to_numpy()[x], df.index[x])

        # sSMA > lSMA -> buy signal
        if df[f'SMA-{sPeriod}'].to_numpy()[x] > df[f'SMA-{lPeriod}'].to_numpy()[x]:

            # preverimo ceno ene delnice in ce imamo dovolj denarja, da lahko kupimo delnice
            cena_ene_delnice = df['Close'].to_numpy()[x] + util.percentageFee(util.feePercentage, df['Close'].to_numpy()[x])
            stDelnic = math.floor(df['Cash'].to_numpy()[x] / cena_ene_delnice)  # stevilo delnic, ki jih lahko kupimo z nasim denarjem
            if check != 2 and stDelnic > 0:  # zadnji signal ni bil buy in imamo dovolj denarja za nakup
                # kupi kolikor je možno delnic glede na cash
                buyPrice = stDelnic * cena_ene_delnice  # stDelnic * njihova cena -> dejanski denar potreben za nakup
                df['Buy'].to_numpy()[x] = buyPrice  # zapisemo buy price
                df['Sell'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je bil zadnji signal buy
                df['Sell-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je bil zadnji signal buy

                # za graf trgovanja
                df['Buy-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Buy-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] - buyPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = stDelnic
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x] + buyPrice

                check = 2

        # sSMA < lSMA -> sell signal
        elif df[f'SMA-{sPeriod}'].to_numpy()[x] < df[f'SMA-{lPeriod}'].to_numpy()[x] and pretekli_dnevi_buy >= holdObdobje:

            if check != 1 and check != 0:  # zadnji signal ni bil sell in nismo na zacetku

                # prodaj vse delnic izracunaj profit in placaj davek
                sellPrice = util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x])  # delnice v denar, obracunamo fees
                profitPredDavkom = util.profit(df['Buy'].to_numpy()[x], sellPrice)  # izracunamo profit pred davkom

                # ce je dobicek pred davkom pozitiven zaracunamo davek na dobicek in ga odstejemo od sellPrice, da dobimo ostanek
                if profitPredDavkom > 0:
                    sellPrice = sellPrice - util.taxes(profitPredDavkom)  # popravimo sellPrice, tako da obracunamo davek

                df['Sell'].to_numpy()[x] = sellPrice  # zapisemo sell price
                df['Profit'].to_numpy()[x] = util.profit(df['Buy'].to_numpy()[x], sellPrice)
                # za graf trgovanja
                df['Sell-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Sell-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa


                df['Buy'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                df['Buy-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] + sellPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = 0
                # updejtamo total
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x]

                check = 1

    return df


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

    if startObdobja == "2016-05-21":
        obdobja.append(startObdobja)

    for x in dowTickersObdobja:

        if startObdobja <= x < endObdobja:  # zna bit da je tuki treba se = dat
            obdobja.append(x)

    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if endObdobja > zadnjeObdobje:
        obdobja.append(endObdobja)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    print("Obdobja: ", obdobja)
    return obdobja


# @jit
def backtest(start, end, sma_period_short, sma_period_long, dowTickers, stockPricesDB, hold_obdobje):
    # nastavimo obdobja
    obdobja = setObdobja(startObdobja=start, endObdobja=end, dowTickersObdobja=dowTickers)

    portfolio = {}
    izloceniTickerji = []
    starting_companies = []
    # begining = start  # "2005-11-21"
    sezIzlocenih = []

    # te imajo probleme pri koncnem obdobju 2008-2-19
    problematicni = ["MO", "HON"]

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
            elif zacetnoObdobje == "2016-05-21":
                starting_companies = dowTickers["2015-03-19"]["all"]

            izloceniTickerji.append("GM")  # dodamo GM pod izlocene

            # trejdamo z all od zacetnegaObdobja
            for x in starting_companies:
                print("Company: ", x)
                # if x != "GM" and x != "HWM":
                # TODO tukaj not se sploh ne pride več ???
                if x in problematicni and koncnoObdobje == "2008-2-19":  # to podjetje ima izjemo
                    print("Popravljam problematicne")
                    real_end_date = datetime.datetime.strptime(koncnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = (real_end_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

                    data = stockPricesDB.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=plus_one_start_date, companyTicker=x)
                    data = data[['Close']].copy()
                    data = zacetniDf(data)  # dodamo stolpce
                    return_df = sma_crossover(sma_period_short, sma_period_long, data, x, 0, 0, True, hold_obdobje)
                    portfolio[x] = return_df

                else:
                    # izjema za podjetje GM, za katerega nimam podatkov zato samo naredim prazen dataframe
                    if x == "GM":
                        # pridobim df od podjetja HD in zbrišem podatke tako da je potem prazen
                        prazen = stockPricesDB.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker="HD")
                        prazen = prazen[['Close']].copy()
                        prazen = zacetniDf(prazen)
                        prazen["Close"] = 0
                        return_df = sma_crossover(sma_period_short, sma_period_long, prazen, x, 0, 0, True, hold_obdobje)
                        portfolio[x] = return_df  # prazen

                    elif x != "GM":  # and x != 'AA'
                        data = stockPricesDB.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker=x)
                        data = data[['Close']].copy()
                        data = zacetniDf(data)  # dodamo stolpce
                        return_df = sma_crossover(sma_period_short, sma_period_long, data, x, 0, 0, True, hold_obdobje)
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
                """
                if odstranjenTicker in izloceniTickerji: # odstranjenTicker je v izlocenihTickerjih -> ga odstranim iz izlocenih in dodam gor isto lezecega addedTicker

                    print("Izlocujem: ")
                    print("Odstranjeni: ", odstranjenTicker)
                    added_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    izloceniTickerji.append(added_ticker)
                    # izloceniTickerji.remove(odstranjenTicker)
                    sezIzlocenih.append(added_ticker)
                    print("Added: ", added_ticker)
                """
                # if odstranjenTicker == "GM": # tuki se GM zamenja z TRV

                if odstranjenTicker in starting_companies:  # odstranjenTicker je v trenutnem portfoliu -> ga zamenjamo z isto ležečim tickerjem iz added

                    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
                    # print()
                    # print(index[x].tail(1))
                    # print()
                    # print(index[x].tail(1)["Shares"])
                    # print(index[x].tail(1)["Cash"])
                    # print(x, "->", dodaj["added"][odstrani["removed"].index(x)])
                    # nov_ticker = dodaj["added"][odstrani["removed"].index(x)]
                    nov_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    print(odstranjenTicker, "->", nov_ticker)
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")  # TODO mogoce tu preverit ce je sploh treba dodajat 1 dan (sepravi se poreveri v prejsnjem dfju ce je zadji dan isti)
                    plus_one_start_date = (real_start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # adding one day
                    modified_date = (datetime.datetime.strptime(plus_one_start_date, "%Y-%m-%d") - datetime.timedelta(days=(sma_period_long * 2))).strftime(
                        "%Y-%m-%d")  # odstevamo long period da dobimo dovolj podatkov
                    print('plus_one_start_date', plus_one_start_date)
                    print('modified_date', modified_date)
                    new_df = stockPricesDB.getCompanyStockDataInRange(date_from=modified_date, date_to=koncnoObdobje, companyTicker=nov_ticker)

                    new_df = new_df[['Close']].copy()
                    new_df = zacetniDf(new_df)
                    ex_df = portfolio[odstranjenTicker]

                    if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]

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
                        # print("Notri", ex_df.iloc[-1])
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].at[plus_one_start_date] = ex_df["Cash"][-1]

                    odvec = new_df[:plus_one_start_date]
                    starting_index = len(odvec) - 1
                    # concat_new = pd.concat([ex_df, new_df])
                    # starting_index = len(ex_df)
                    # concat_new["Ticker"].iloc[starting_index] = dodaj["added"][odstrani["removed"].index(x)] # zapisemo nov ticker
                    # concat_new["Total"].iloc[starting_index] = concat_new["Cash"].iloc[starting_index]

                    # startamo trading algo
                    new_returns = sma_crossover(sma_period_short, sma_period_long, new_df, nov_ticker, starting_index, 0, True,
                                                hold_obdobje)  # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

                    added_returns = new_returns[plus_one_start_date:]  # TODO kaj se tu dogaja??
                    concat_returns = pd.concat([ex_df, added_returns])  # TODO pri AA in najbrs se pri kaksnih je ex_df prekratek
                    # profit_graph(concat_returns, 1, f"Stolpec {nov_ticker}" , round(concat_returns['Total'].iloc[-1], 4))
                    new_portfolio = {nov_ticker if k == odstranjenTicker else k: v for k, v in portfolio.items()}
                    new_portfolio[nov_ticker] = concat_returns
                    # isOk = new_portfolio[nov_ticker]
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
                # modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov

                # if ostaliTicker != "GM":  # ostaliTicker != "GM" and ostaliTicker != "AA"

                totals = portfolio[ostaliTicker]
                zadnji_signal = 0
                # TODO tuki spet error -> popravljeno
                # print('BAC : ', portfolio['BAC'])
                # if ostaliTicker != 'AA':
                # print('printam debug')
                # print(totals[ostaliTicker])
                # print(totals['Shares'])
                if totals['Shares'].to_numpy()[-1] == 0:
                    zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                elif totals['Shares'].to_numpy()[-1] > 0:
                    zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                print("Trenutni ostali ticker: ", ostaliTicker)
                company = ostaliTicker
                if ostaliTicker == "GM":
                    company = "HD"  # ce se prav spomnem se uzame HD samo zato, da se dobi ok velik df, ker za GM ne morem
                new_data = stockPricesDB.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=company)
                if ostaliTicker == "GM":
                    new_data["Close"] = 0
                new_data = new_data[['Close']].copy()
                starting_index = len(totals)

                concat_data = pd.concat([totals, new_data])

                concat_totals = sma_crossover(sma_period_short, sma_period_long, concat_data, f"new{ostaliTicker}", starting_index, zadnji_signal, False, hold_obdobje)
                portfolio[ostaliTicker] = concat_totals

    totals = prikaziPodatkePortfolia(portfolio, sezIzlocenih, izloceniTickerji, startIzpis=start, endIzpis=end)

    return totals


def prikaziPodatkePortfolia(portfolio, sezIzlocenih, izloceniTickerji, startIzpis, endIzpis):
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

    profit_graph(allFunds, 1, "Portfolio", round(allFunds['Total'].to_numpy()[-1], 4))

    # se izpis podatkov portfolia
    startFunds = len(portfolio) * util.getMoney()
    endFunds = allFunds['Total'].to_numpy()[-1]

    print("Zacetna sredstva: ", startFunds, "$")
    print("Skupna sredstva portfolia: ", round(allFunds['Total'].to_numpy()[-1], 4), "$")
    # print("Profit: ", round(allFunds['Total'].iat[-1] - (len(portfolio) * util.getMoney()), 4), "$")
    print("Profit: ", round(endFunds - startFunds, 4), "$")
    print("Kumulativni donos v procentih: ", round((endFunds - startFunds) / startFunds, 4) * 100, "%")

    print("Delnice, ki jih še imamo v portfoliu:")
    for key, value in allShares.items():
        print(key, " : ", value)

    print("Izloceni")
    print(sezIzlocenih)
    print(izloceniTickerji)

    return allFunds


# 70% = 11-21-2005 do 21-5-2016 UCNA

# 30% = 21-5-2016 do 1-1-2021 TESTNA

# SMA crossover strategy
# datetmie = leto, mesec, dan
# short_period = 85 #80
# long_period = 200 #180

# testing date time
# start = "2005-11-21"
# # start = "2016-5-21"
# # end = "2008-4-1"
# # end = "2020-10-1"
# # end = "2008-2-19"
# end = "2016-5-21"
# end = "2020-11-12"
# end = "2021-1-1"
# holdObdobje = 1

# begin_time = datetime.datetime.now()

# backtest(start, end, short_period, long_period, dowTickers, stockPricesDB, holdObdobje)


# print(datetime.datetime.now() - begin_time)


"""

vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS',  'GE', #'GM',
                'GS', 'HD', 'HON', 'HPQ', 'HWM', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',
                'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']

for x in vsi_tickerji:
    print("Testiram: ", x)
    test_data = yf.download(x, start=start, end=end, progress=False)
    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = sma_crossover(short_period, long_period, test_data, x, 0, 0, True)

print(datetime.datetime.now() - begin_time)


test_ticker = "HD"
test_data = yf.download(test_ticker, start=start, end=end, progress=False)
test_data = test_data[['Close']].copy()
test_data = zacetniDf(test_data)  # dodamo stolpce
return_df = sma_crossover(short_period, long_period, test_data, test_ticker, 0, 0, True)

#SMA_trading_graph(short_period, long_period, return_df, test_ticker)
#profit_graph(return_df, 0, test_ticker, return_df["Total"].iloc[-1])

print(datetime.datetime.now() - begin_time)
"""
