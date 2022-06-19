import pandas as pd
import datetime as datetime
import numpy as np

from technical_strategies.bollinger_bands.bollinger_bands import bollingerBands
from technical_strategies.bollinger_bands.bollinger_bands_grafi import profit_graph
from utility import utils as util


pd.options.mode.chained_assignment = None  # default='warn'


def zacetniDf(data, sma_period):

    # kreiramo nova stolpca za buy/sell signale
    #data[f'SMA-{sma_period}'] = np.nan
    data["Typical price"] = np.nan
    data["STD"] = np.nan
    data["TP SMA"] = np.nan
    data['Upper band'] = np.nan
    data['Lower band'] = np.nan
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


def backtest(start, end, sma_period, bands_multiplayer, dowTickers, stock_data, holdObdobje):

    obdobja = []
    for x in dowTickers:

        if x < end:
            obdobja.append(x)


    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if end > zadnjeObdobje:
        obdobja.append(end)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    print("Obdobja: ", obdobja)


    portfolio = {}
    izloceniTickerji = []
    starting_companies = []
    begining = "2005-11-21"

    # te imajo probleme pri koncnem obdobju 2008-2-19
    problematicni = ["MO", "HON"]

    for i in range(0, len(obdobja) - 1): # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetnoObdobje = obdobja[i]
        koncnoObdobje = obdobja[i + 1]
        print(i, zacetnoObdobje, "+", koncnoObdobje)

        # zacetek
        if zacetnoObdobje == begining:
            starting_companies = dowTickers[zacetnoObdobje]["all"]
            # starting_companies.remove("GM") # odstranimo časnovno linijo GM ker nimamo podatkov
            izloceniTickerji.append("GM") # dodamo GM pod izlocene

            for x in starting_companies:
                print("Company: ", x)

                if x in problematicni and koncnoObdobje == "2008-2-19": # to podjetje ima izjemo
                    print("Popravljam problematicne")
                    real_end_date = datetime.datetime.strptime(koncnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_end_date + datetime.timedelta(days=1)

                    data = getStocks.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=plus_one_start_date, companyTicker=x, allStockData=stock_data) # yf.download(x, start=zacetnoObdobje, end=plus_one_start_date, progress=False)
                    data = data[["High", "Low", "Close"]].copy()
                    data = zacetniDf(data, sma_period)  # dodamo stolpce
                    return_df = bollingerBands(sma_period, bands_multiplayer, data, x, 0, 0, True, holdObdobje)
                    portfolio[x] = return_df

                else:

                    # izjema za podjetje GM, za katerega nimam podatkov zato samo naredim prazen dataframe
                    if x == "GM":
                        index = pd.date_range(zacetnoObdobje, "2009-6-8", freq='D')
                        columns = ["Close"]
                        prazen = pd.DataFrame(index=index, columns=columns)
                        prazen = zacetniDf(prazen, sma_period)
                        prazen["Cash"] = prazen["Cash"].add(util.getMoney())
                        prazen["Total"] = prazen["Cash"]
                        portfolio[x] = prazen

                    elif x != "GM":
                        data = getStocks.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker=x, allStockData=stock_data) # yf.download(x, start=zacetnoObdobje, end=koncnoObdobje, progress=False)
                        data = data[["High", "Low", "Close"]].copy()
                        data = zacetniDf(data, sma_period)  # dodamo stolpce
                        return_df = bollingerBands(sma_period, bands_multiplayer, data, x, 0, 0, True, holdObdobje)
                        portfolio[x] = return_df


            print(portfolio.keys())
            print(starting_companies)
            print(dowTickers["2005-11-21"]["all"])
            print("LEN: ", len(portfolio))


        # ce nismo na zacetku gremo cez removed in added in naredimo menjave ter trejdamo za naslednje obdobje
        elif zacetnoObdobje != begining:

            dodani = []
            # gremo najprej cez removed in opravimo zamenjave
            for odstranjenTicker in dowTickers[zacetnoObdobje]["removed"]:

                starting_companies = portfolio.keys()

                if odstranjenTicker in starting_companies: # odstranjenTicker je v trenutnem portfoliu -> ga zamenjamo z isto ležečim tickerjem iz added


                    nov_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    print(odstranjenTicker, "->", nov_ticker)
                    # naslednje_obdobje = '2008, 2, 19'
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                    modified_date = plus_one_start_date - datetime.timedelta(
                        days=(sma_period * 2))  # odstevamo long period da dobimo dovolj podatkov
                    new_df = getStocks.getCompanyStockDataInRange(date_from=modified_date, date_to=koncnoObdobje, companyTicker=nov_ticker, allStockData=stock_data) # yf.download(nov_ticker, start=modified_date, end=koncnoObdobje, progress=False)

                    new_df = new_df[["High", "Low", "Close"]].copy()
                    new_df = zacetniDf(new_df, sma_period)
                    ex_df = portfolio[odstranjenTicker]
                    ex_data = ex_df.tail(1)


                    if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]

                    elif ex_df["Shares"][-1] > 0:  # moramo prodat delnice in jih investirat v podjetje ki ga dodajamo

                        prodano = (ex_df['Shares'].iat[-1] * ex_df['Close'].iat[-1])  # delnice v denar
                        prodanoFees = util.fees(prodano)  # ostanek denarja po fees
                        sellPrice = prodanoFees
                        ex_df['Sell'].iat[-1] = prodanoFees  # zapisemo sell price
                        ex_df['Profit'].iat[-1] = util.profit(ex_df['Buy'].iat[-1], sellPrice)

                        ex_df['Buy'].iat[-1] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell

                        # ce je dobicek pozitiven zaracunamo davek na dobicek in ga odstejemo od prodanoFees da dobimo ostanek
                        if (ex_df['Profit'].iat[-1] > 0):
                            prodanoFees = prodanoFees - util.taxes(ex_df['Profit'].iat[-1])

                        ex_df['Cash'].iat[-1] = np.nan_to_num(ex_df['Cash'].iat[-1]) + prodanoFees  # posodbi cash
                        ex_df['Shares'].iat[-1] = 0
                        ex_df['Total'].iat[-1] = ex_df["Cash"].iat[-1]

                        # prejsni df je posodobljen in delnice so prodane, samo prepisemo Cash v new_df
                        new_df["Cash"].at[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].at[plus_one_start_date] = ex_df["Cash"][-1]

                    odvec = new_df[:plus_one_start_date]
                    starting_index = len(odvec) - 1

                    # startamo trading algo
                    new_returns = bollingerBands(sma_period, bands_multiplayer, new_df, nov_ticker, starting_index, 0,
                                                True, holdObdobje)  # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

                    added_returns = new_returns[plus_one_start_date:]
                    concat_returns = pd.concat([ex_df, added_returns])
                    new_portfolio = {nov_ticker if k == odstranjenTicker else k: v for k, v in portfolio.items()}
                    new_portfolio[nov_ticker] = concat_returns
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
                plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                # modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov

                if ostaliTicker != "GM":

                    totals = portfolio[ostaliTicker]
                    zadnji_signal = 0

                    if totals['Shares'].iat[-1] == 0:
                        zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                    elif totals['Shares'].iat[-1] != 0:

                        zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                    print("Trenutni ostali ticker: ", ostaliTicker)
                    new_data = getStocks.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=ostaliTicker, allStockData=stock_data) # yf.download(ostaliTicker, start=plus_one_start_date, end=koncnoObdobje, progress=False)

                    new_data = new_data[["High", "Low", "Close"]].copy()
                    starting_index = len(totals)

                    concat_data = pd.concat([totals, new_data])

                    concat_totals = bollingerBands(sma_period, bands_multiplayer, concat_data, f"new{ostaliTicker}", starting_index,
                                                  zadnji_signal, False, holdObdobje)
                    portfolio[ostaliTicker] = concat_totals

    totals = prikaziPodatkePortfolia(portfolio, izloceniTickerji)

    return totals


def prikaziPodatkePortfolia(portfolio, izloceniTickerji):
    # gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        print(ticker)
        tickerTotals = portfolio[ticker]
        allShares[ticker] = tickerTotals['Shares'].iat[-1]

        # nan = tickerTotals["Total"].loc["2008-2-19"]
        # print(nan)

        ## mogoce avg = tickerTotals["Total"].mean() in pol add(allFunds['Total'],tickerTotals['Total'], avg)

        if (count == 0):
            # tickerTotals["Total"] = tickerTotals["Total"].dropna()
            # tickerTotals = tickerTotals.dropna()
            allFunds = tickerTotals[['Total']].copy()
        else:
            # print(tickerTotals['Total'][tickerTotals['Total'].index.duplicated()])
            tickerTotals = tickerTotals[~tickerTotals.index.duplicated(keep='first')]
            # print(tickerTotals['Total'][tickerTotals['Total'].index.duplicated()])

            # tickerTotals = tickerTotals.dropna()
            allFunds['Total'] = allFunds['Total'] + tickerTotals['Total']

        count += 1

    # print(allFunds)
    # profit_graph(allFunds, 1, "Portfolio", round(allFunds['Total'].iat[-1], 4))

    # se izpis podatkov portfolia
    startFunds = len(portfolio) * util.getMoney()
    endFunds = allFunds['Total'].iat[-1]

    print("Zacetna sredstva: ", startFunds, "$")
    print("Skupna sredstva portfolia: ", round(allFunds['Total'].iat[-1], 4), "$")
    # print("Profit: ", round(allFunds['Total'].iat[-1] - (len(portfolio) * util.getMoney()), 4), "$")
    print("Profit: ", round(endFunds - startFunds, 4), "$")
    print("Kumulativni donos v procentih: ", round((endFunds - startFunds) / startFunds, 4) * 100, "%")

    print("Delnice, ki jih še imamo v portfoliu:")
    for key, value in allShares.items():
        print(key, " : ", value)

    print("Izloceni")
    #print(sezIzlocenih)
    print(izloceniTickerji)

    return allFunds

# Bollinger bands strategy
# datetmie = leto, mesec, dan

# sma_period = 20
# bands_multiplayer = 2

# testing date time
# start = "2005-11-21"
# #end = "2012-10-25"
# #end = "2008-4-1"
# #end = "2020-10-1"
# # end = "2008-2-19"
# #end = "2021-1-1"
#
# #end = "2012-1-1"
# end = "2016-5-21"
# holdObdobje = 365
#
# begin_time = datetime.datetime.now()
#
# dowTickers = dow.endTickers # podatki o sezona sprememb dow jones indexa
# stock_data = getStocks.getAllStockData(start_date=start, end_date=end)
#
# # backtest(start, end, sma_period, bands_multiplayer, dowTickers, stock_data, holdObdobje)
#
# testirajNaPortfoliu(dowTickers, stock_data, holdObdobje)
#
# print(datetime.datetime.now() - begin_time)
