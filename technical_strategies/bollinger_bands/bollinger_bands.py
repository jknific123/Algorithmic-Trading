import math

import pandas as pd
import datetime as datetime

import numpy as np
import matplotlib.pyplot as plt
from utility import utils as util
from dow_index_data import dow_jones_companies_api as dow
from stock_ohlc_data import get_stock_data as getStocks


def days_between(d1, d2):

    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def bollingerBands(sma_period,bands_multiplayer, df, ticker, starting_index, status, odZacetkaAliNe, holdObdobje):
    # naredimo nove stolpce za EMA-e, MACD in signal line
    """
    df[f'SMA-{sma_period}'] = df['Close'].rolling(window=sma_period, min_periods=1, center=False).mean()
    df["STD"] = df['Close'].rolling(window=sma_period, min_periods=1, center=False).std()
    df['Upper band'] = df[f'SMA-{sma_period}'] + (df["STD"] * bands_multiplayer)
    df['Lower band'] = df[f'SMA-{sma_period}'] - (df["STD"] * bands_multiplayer)
    """

    df["Typical price"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["STD"] = df["Typical price"].rolling(window=sma_period, min_periods=1, center=False).std(ddof=0)
    df[f"TP SMA"] = df["Typical price"].rolling(sma_period).mean()
    df['Upper band'] = df[f"TP SMA"] + bands_multiplayer * df["STD"]
    df['Lower band'] = df[f"TP SMA"] - bands_multiplayer * df["STD"]


    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi EMA že na voljo
    if starting_index == 0:
        df = df[sma_period:]

    # za racunanje davka na dobiček
    sellPrice = 0

    # check -> zato da nimamo dveh zapovrstnih buy/sell signalov: 2 = buy, 1 = sell
    # status = 0 -> zacnemo od zacetka
    # 1 -> zacenjamo od tam ko je bil zadnji signal sell
    # 2 -> zacenjamo od tam ko je bil zadnji signal buy
    check = status
    for x in range(starting_index, len(df)):

        """
        print(df.index[x])

        if df.index[x] == datetime.datetime.strptime("2008-1-17", "%Y-%m-%d"): # datetime.datetime(2008-1-17)
            print("HURAAYYY")
        """

        # filing shares, cash, total
        if (x - 1) >= 0:  # preverimo ce smo znotraj tabele
            df['Shares'].iat[x] = np.nan_to_num(df['Shares'].iat[x - 1])  # prenesemo prejsnje st delnic naprej
            if x != starting_index: # za izjeme ko dodamo nov ticker in ne smemo zbrisat starting cash
                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x - 1])  # prenesemo prejsnji Cash naprej
            elif x == starting_index and odZacetkaAliNe is False: # takrat ko je isto podjetje kot prej
                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x - 1])  # prenesemo prejsnji Cash naprej
            df['Total'].iat[x] = (df['Cash'].iat[x] + df['Shares'].iat[x] * df['Close'].iat[x])  # izracunamo total TODO probably treba dodat fees
            df['Ticker'].iat[x] = ticker
            df['Buy'].iat[x] = df['Buy'].iat[x - 1]
            df['Sell'].iat[x] = df['Sell'].iat[x - 1]
            df['Buy-date'].iat[x] = df['Buy-date'].iat[x - 1]
            df['Sell-date'].iat[x] = df['Sell-date'].iat[x - 1]


        else:  # zacetek tabele -> inicializacija vrednosti
            df['Shares'].iat[x] = np.nan_to_num(df['Shares'].iat[x])
            if df['Cash'].iat[x] == 0: # nimamo se denarja
                df['Cash'].iat[x] = util.getMoney()
            df['Total'].iat[x] = (df['Cash'].iat[x] + (df['Shares'].iat[x] * df['Close'].iat[x]))
            df['Ticker'].iat[x] = ticker

        pretekli_dnevi_buy = 0
        if df["Buy-date"].iat[x] != "": #buy_date != "":
            pretekli_dnevi_buy = days_between(df["Buy-date"].iat[x], df.index[x].strftime("%Y-%m-%d"))

        # cena < Lower band -> buy signal
        if df["Close"].iat[x] < df[f'Lower band'].iat[x]: # x > 0 and df["Close"].iat[x - 1] < df[f'Lower band'].iat[x - 1] and


            can_buy = math.floor(df['Cash'].iat[x] / (df['Close'].iat[x] + util.percentageFee(util.feePercentage, df['Close'].iat[x]))) # to je biu poopravek, dalo je buy signal tudi ce ni bilo denarja za kupit delnico
            if check != 2 and can_buy > 0: # zadnji signal ni bil buy in imamo dovolj denarja za nakup

                # kupi kolikor je možno delnic glede na cash -> drugi del je cena delnice + fee na nakup delnice
                stDelnic = math.floor(df['Cash'].iat[x] / (df['Close'].iat[x] + util.percentageFee(util.feePercentage, df['Close'].iat[x])))
                buyPrice = stDelnic * df['Close'].iat[x]  # stDelnic * njihova cena -> dejanski denar potreben za nakup TODO tudi tuki dodaj fees
                df['Buy'].iat[x] = buyPrice  # zapisemo buy price
                df['Sell'].iat[x] = 0  # zapisemo 0 da oznacimo da je bil zadnji signal buy
                df['Sell-date'].iat[x] = ""  # zapisemo "" da oznacimo da je bil zadnji signal buy

                # za graf trgovanja
                df['Buy-Signal'].iat[x] = df["Close"].iat[x]
                df["Buy-date"].iat[x] = df.index[x].strftime("%Y-%m-%d")  # zapisem datum nakupa


                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x]) - (
                        stDelnic * df['Close'].iat[x])  # posodbi cash TODO tudi tuki dodaj fees
                df['Shares'].iat[x] = df['Shares'].iat[x] + stDelnic

                check = 2

        # cena > Upper band -> sell signal
        elif df["Close"].iat[x] > df[f'Upper band'].iat[x] and pretekli_dnevi_buy >= holdObdobje: # x > 0 and df["Close"].iat[x - 1] > df[f'Upper band'].iat[x - 1] and

            if check != 1 and check != 0:

                # TODO dodaj še davek na dobiček 27,5% -> done

                # prodaj vse delnic izracunaj profit in placaj davek
                prodano = (df['Shares'].iat[x] * df['Close'].iat[x])  # delnice v denar
                prodanoFees = util.fees(prodano)  # ostanek denarja po fees
                sellPrice = prodanoFees
                df['Sell'].iat[x] = prodanoFees  # zapisemo sell price
                df['Profit'].iat[x] = util.profit(df['Buy'].iat[x], sellPrice)
                # za graf trgovanja
                df['Sell-Signal'].iat[x] = df["Close"].iat[x]
                df["Sell-date"].iat[x] = df.index[x].strftime("%Y-%m-%d") # zapisem datum nakupa

                df['Buy'].iat[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                df['Buy-date'].iat[x] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell


                # ce je dobicek pozitiven zaracunamo davek na dobicek in ga odstejemo od prodanoFees da dobimo ostanek
                if (df['Profit'].iat[x] > 0):
                    prodanoFees = prodanoFees - util.taxes(df['Profit'].iat[x])

                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x]) + prodanoFees  # posodbi cash
                df['Shares'].iat[x] = 0
                # updejtamo total
                df['Total'].iat[x] = df['Cash'].iat[x]

                check = 1

    # print(df)
    # plotShares(df, ticker)
    # MACD_trading_graph(sPeriod, lPeriod, df, ticker)
    # profit_graph(df, 0, ticker)


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    # print(df)
    # newDf = df[['Close', 'Buy', 'Sell', 'Cash', 'Shares', 'Total']].copy()
    # print(newDf)
    return df


def bollinger_trading_graph(sma_period, bands_multiplayer, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    # cena
    df['Close'].plot(ax=ax1, color='black', label="Cena", alpha=0.5)
    #df[f'SMA-{sma_period}'].plot(ax=ax1 ,color='orange', linestyle="--")

    # kratki in dolgi SMA
    df['Upper band'].plot(ax=ax1, label="Zgornji pas", color="blue", linestyle="--")
    df['Lower band'].plot(ax=ax1, label="Spodnji pas", color="purple", linestyle="--")

    # buy/sell signali
    ax1.plot(df['Buy-Signal'], '^', markersize=6, color='green', label='Buy signal', lw=2)
    ax1.plot(df['Sell-Signal'], 'v', markersize=6, color='red', label='Sell signal', lw=2)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def profit_graph(df, mode, company, cash):
    # prikaz grafa sredstev
    # mode = 0 -> prikaz podjetja
    # mode = 1 -> prikaz portfolia

    fig = plt.figure(figsize=(8, 6), dpi=200)
    if (mode == 0):
        fig.suptitle(f'Končna vrednost podjetja {company}: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
        df['Total'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)
    elif (mode == 1):
        fig.suptitle(f'Končna vrednost portfolia: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost portfolia v $')
        df['Total'].plot(ax=ax1, label="Vrednost portfolia", color='black', alpha=0.5)

    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def plotShares(df, company):
    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Num of shares')
    df['Shares'].plot(ax=ax1, color='black', alpha=0.5)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df['Shares'])

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

def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    # key = sma_lenght, value = std_multiplier
    slovar_parametrov = {}
    slovar_parametrov[10] = 1.9
    slovar_parametrov[20] = 2
    slovar_parametrov[30] = 2
    slovar_parametrov[40] = 2.1
    slovar_parametrov[50] = 2.1
    for sma_length in slovar_parametrov: # 10 - 50
        # print("Trenutna Long vrednost: ", long)

        #for std_multiplier in range(40, 110 , 10): # 110

            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = {}
            print(f"Kombinacija: SMA length = {sma_length} , std_multiplier = {slovar_parametrov[sma_length]}")
            # print debug
            #print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
            temp = backtest(start_period, end_period, sma_length, slovar_parametrov[sma_length], dowTickers, stock_data, hold_obdobje)
            # backtest(start, end, sma_period, bands_multiplayer, dowTickers, stock_data, holdObdobje)
            #print("Data: ", temp)
            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = temp
            # print("Trenutna Short vrednost: ", short)
            print()
            counter += 1

    print("Counter: ", counter)

    return ucni_rezultati

def testirajNaPortfoliu(dowTickers, stock_data, hold_obdobje):

    rez_ucni = najdiOptimalneParametreNaPotrfoliu("2005-11-21", "2016-5-21", dowTickers, stock_data, hold_obdobje)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        # print debug
        print("Kombinacija : ", x)
        #print("Before in rez_total_ucni: ", rez_total_ucni[x])
        #print("Before in rez_total_ucni type: ", type(rez_total_ucni[x]))
        #print("Before in rez_ucni[x][Total].iat[-1]: ", rez_total_ucni[x])
        #print("Before in rez_ucni[x][Total].iat[-1] type: ", type(rez_total_ucni[x]))
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        #print("After: ", rez_total_ucni[x])
        print()

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])

# Bollinger bands strategy
# datetmie = leto, mesec, dan

# sma_period = 20
# bands_multiplayer = 2

# testing date time
start = "2005-11-21"
#end = "2012-10-25"
#end = "2008-4-1"
#end = "2020-10-1"
# end = "2008-2-19"
#end = "2021-1-1"

#end = "2012-1-1"
end = "2016-5-21"
holdObdobje = 365

begin_time = datetime.datetime.now()

dowTickers = dow.endTickers # podatki o sezona sprememb dow jones indexa
stock_data = getStocks.getAllStockData(start_date=start, end_date=end)

# backtest(start, end, sma_period, bands_multiplayer, dowTickers, stock_data, holdObdobje)

testirajNaPortfoliu(dowTickers, stock_data, holdObdobje)

print(datetime.datetime.now() - begin_time)

"""
test_ticker = "HD"
test_data = yf.download(test_ticker, start=start, end=end, progress=False)
test_data = test_data[["High", "Low", "Close"]].copy()
test_data = zacetniDf(test_data, sma_period)  # dodamo stolpce
return_df = bollingerBands(sma_period, bands_multiplayer, test_data, test_ticker, 0, 0, True)
print(datetime.datetime.now() - begin_time)


bollinger_trading_graph(sma_period, bands_multiplayer, return_df, test_ticker)
profit_graph(return_df, 0, test_ticker, return_df["Total"].iat[-1])
"""



"""
df = yf.download("HD", start=start, end=end, progress=False)
df = zacetniDf(df, sma_period)
df["Typical price"] = (df["High"] + df["Low"] + df["Close"]) / 3
df["STD"] = df["Typical price"].rolling(window=sma_period, min_periods=1, center=False).std(ddof=0)
df[f"TP SMA"] = df["Typical price"].rolling(sma_period).mean()
df['Upper band'] = df[f"TP SMA"] + bands_multiplayer * df["STD"]
df['Lower band'] = df[f"TP SMA"] - bands_multiplayer * df["STD"]

ax = df[["Close", "Upper band", "Lower band"]].plot(color=["blue", "red", "green"])
plt.show()

#bollinger_trading_graph(sma_period, bands_multiplayer, df, "HD")

"""