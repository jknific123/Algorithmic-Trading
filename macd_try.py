import math

import pandas_datareader.data as web
import pandas as pd
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
import utils as util
import dow_jones_companies as dow
import yfinance as yf
import get_stock_data as getStocks


def days_between(d1, d2):

    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def macd(sPeriod, lPeriod,signal_period, df, ticker, starting_index, status, odZacetkaAliNe, holdObdobje):
    # naredimo nove stolpce za EMA-e, MACD in signal line

    df[f'EMA-{sPeriod}'] = df['Close'].ewm(span=sPeriod, adjust=False).mean()
    df[f'EMA-{lPeriod}'] = df['Close'].ewm(span=lPeriod, adjust=False).mean()
    df["MACD"] = df[f'EMA-{sPeriod}'] - df[f'EMA-{lPeriod}']
    df[f"Signal-{signal_period}"] = df["MACD"].ewm(span=signal_period, adjust=False).mean()


    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi EMA že na voljo
    if starting_index == 0:
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

        # MACD > signal line -> buy signal
        if df["MACD"].iat[x] > df[f"Signal-{signal_period}"].iat[x]:
            # print("MACD: ", df["MACD"].iat[x]," Signal line: ", df[f"Signal-{signal_period}"].iat[x])

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

        # MACD < signal line -> sell signal
        elif df["MACD"].iat[x] < df[f"Signal-{signal_period}"].iat[x] and pretekli_dnevi_buy >= holdObdobje:

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
                    #print("Profit taxes", util.taxes(df['Profit'].iat[x]))

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


def MACD_trading_graph(sPeriod, lPeriod, signal_period, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(f"{company}, trgovalni signali")
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    fig2 = plt.figure(figsize=(8, 6), dpi=200)
    fig2.suptitle(f"{company}: MACD in signalna črta")
    ax2 = fig2.add_subplot(111, ylabel='Vrednost MACD in Signalne črte')
    # cena
    df['Close'].plot(ax=ax1, color='black', label="Cena", alpha=0.5)

    # MACD in signal line
    df[["MACD", f'Signal-{signal_period}']].plot(ax=ax2, linestyle="--")
    #df[["MACD", f'Signal-{signal_period}']].plot(ax=ax1, linestyle="--", secondary_y=True)
    #df['Close'].plot(ax=ax2, alpha=0.25, secondary_y=True)


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

    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df['Shares'])

def zacetniDf(data):

    # kreiramo nova stolpca za buy/sell signale
    data[f'EMA-{short_period}'] = np.nan
    data[f'EMA-{long_period}'] = np.nan
    data["MACD"] = np.nan
    data[f"Signal-{signal_period}"] = np.nan
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


def backtest(start, end, short_period, long_period, signal_period, dowTickers, stock_data, holdObdoje):

    obdobja = []
    for x in dowTickers:

        if x < end:
            obdobja.append(x)


    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if end > zadnjeObdobje:
        obdobja.append(end)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    #print("Obdobja: ", obdobja)




    portfolio = {}
    izloceniTickerji = []
    starting_companies = []
    begining = "2005-11-21"

    # te imajo probleme pri koncnem obdobju 2008-2-19
    problematicni = ["MO", "HON"]

    for i in range(0, len(obdobja) - 1): # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetnoObdobje = obdobja[i]
        koncnoObdobje = obdobja[i + 1]
        # print(i, zacetnoObdobje, "+", koncnoObdobje)

        # zacetek
        if zacetnoObdobje == begining:
            starting_companies = dowTickers[zacetnoObdobje]["all"]
            # starting_companies.remove("GM") # odstranimo časnovno linijo GM ker nimamo podatkov
            izloceniTickerji.append("GM") # dodamo GM pod izlocene

            for x in starting_companies:
                # print("Company: ", x)

                if x in problematicni and koncnoObdobje == "2008-2-19": # to podjetje ima izjemo
                    # print("Popravljam problematicne")
                    real_end_date = datetime.datetime.strptime(koncnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_end_date + datetime.timedelta(days=1)

                    data = getStocks.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=plus_one_start_date, companyTicker=x, allStockData=stock_data) # yf.download(x, start=zacetnoObdobje, end=plus_one_start_date, progress=False)
                    data = data[['Close']].copy()
                    data = zacetniDf(data)  # dodamo stolpce
                    return_df = macd(short_period, long_period, signal_period, data, x, 0, 0, True, holdObdobje)
                    portfolio[x] = return_df

                else:

                    # izjema za podjetje GM, za katerega nimam podatkov zato samo naredim prazen dataframe
                    if x == "GM":
                        index = pd.date_range(zacetnoObdobje, "2009-6-8", freq='D')
                        columns = ["Close"]
                        prazen = pd.DataFrame(index=index, columns=columns)
                        prazen = zacetniDf(prazen)
                        prazen["Cash"] = prazen["Cash"].add(util.getMoney())
                        prazen["Total"] = prazen["Cash"]
                        portfolio[x] = prazen

                    elif x != "GM":
                        data = getStocks.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=koncnoObdobje, companyTicker=x, allStockData=stock_data) # yf.download(x, start=zacetnoObdobje, end=koncnoObdobje, progress=False)
                        data = data[['Close']].copy()
                        data = zacetniDf(data)  # dodamo stolpce
                        return_df = macd(short_period, long_period, signal_period, data, x, 0, 0, True, holdObdobje)
                        portfolio[x] = return_df


            # print(portfolio.keys())
            # print(starting_companies)
            # print(dowTickers["2005-11-21"]["all"])
            # print("LEN: ", len(portfolio))


        # ce nismo na zacetku gremo cez removed in added in naredimo menjave ter trejdamo za naslednje obdobje
        elif zacetnoObdobje != begining:

            dodani = []
            # gremo najprej cez removed in opravimo zamenjave
            for odstranjenTicker in dowTickers[zacetnoObdobje]["removed"]:

                starting_companies = portfolio.keys()

                if odstranjenTicker in starting_companies: # odstranjenTicker je v trenutnem portfoliu -> ga zamenjamo z isto ležečim tickerjem iz added


                    nov_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    # print(odstranjenTicker, "->", nov_ticker)
                    # naslednje_obdobje = '2008, 2, 19'
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                    modified_date = plus_one_start_date - datetime.timedelta(
                        days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov
                    new_df = getStocks.getCompanyStockDataInRange(date_from=modified_date, date_to=koncnoObdobje, companyTicker=nov_ticker, allStockData=stock_data) # yf.download(nov_ticker, start=modified_date, end=koncnoObdobje, progress=False)

                    new_df = new_df[['Close']].copy()
                    new_df = zacetniDf(new_df)
                    ex_df = portfolio[odstranjenTicker]
                    ex_data = ex_df.tail(1)


                    if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
                        new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]

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
                        new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].loc[plus_one_start_date] = ex_df["Cash"][-1]

                    odvec = new_df[:plus_one_start_date]
                    starting_index = len(odvec) - 1

                    # startamo trading algo
                    new_returns = macd(short_period, long_period, signal_period, new_df, nov_ticker, starting_index, 0,
                                                True, holdObdobje)  # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

                    added_returns = new_returns[plus_one_start_date:]
                    concat_returns = pd.concat([ex_df, added_returns])
                    new_portfolio = {nov_ticker if k == odstranjenTicker else k: v for k, v in portfolio.items()}
                    new_portfolio[nov_ticker] = concat_returns
                    portfolio = new_portfolio
                    dodani.append(nov_ticker)
                    # print("Po izlocanju: ", odstranjenTicker)
                    # print(sorted(portfolio.keys()))

            # smo updejtali vse removed, zdej pa samo nadaljujemo trejdanej z usemi ostalimi

            ostali = set(portfolio.keys()) - set(dodani)
            ostali = sorted(list(ostali))
            # print("Ostali tickerji: ", sorted(ostali))
            for ostaliTicker in ostali:

                real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                # modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov

                if ostaliTicker != "GM":

                    totals = portfolio[ostaliTicker]
                    zadnji_signal = 0

                    #print("Podjetje: ", ostaliTicker)
                    #print("df: ", totals)
                    #print()
                    if totals['Shares'].iat[-1] == 0:
                        zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                    elif totals['Shares'].iat[-1] != 0:
                        zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                    # print("Trenutni ostali ticker: ", ostaliTicker)
                    new_data = getStocks.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=ostaliTicker, allStockData=stock_data) # yf.download(ostaliTicker, start=plus_one_start_date, end=koncnoObdobje, progress=False)

                    new_data = new_data[['Close']].copy()
                    starting_index = len(totals)

                    concat_data = pd.concat([totals, new_data])

                    concat_totals = macd(short_period, long_period, signal_period, concat_data, f"new{ostaliTicker}", starting_index,
                                                  zadnji_signal, False, holdObdobje)
                    portfolio[ostaliTicker] = concat_totals

    totals = prikaziPodatkePortfolia(portfolio, izloceniTickerji)

    return totals

def prikaziPodatkePortfolia(portfolio, izloceniTickerji):
    # gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    # print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        # print(ticker)
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
    print(izloceniTickerji)

    return allFunds


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    ema1_vrednosti = [10, 12, 15, 18, 20]
    ema2_vrednosti = [20, 24, 30, 35, 40]
    signal_vrednosti = [3, 6, 9]

    for ema1 in ema1_vrednosti:
        # print("Trenutna Long vrednost: ", long)

        for ema2 in ema2_vrednosti:

            for signal in signal_vrednosti:

                if ema1 != ema2:
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = {}
                    print(f"Kombinacija: Ema1 = {ema1} , Ema2 = {ema2} , Signal = {signal}")
                    # print debug
                    #print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
                    temp = backtest(start_period, end_period, ema1, ema2, signal, dowTickers, stock_data, hold_obdobje)
                    #print("Data: ", temp)
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = temp
                    # print("Trenutna Short vrednost: ", short)
                    print()
                counter += 1

    #print("Counter: ", counter)

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



# MACD crossover strategy
# datetmie = leto, mesec, dan
short_period = 12 # 12 #20
long_period = 26 #26 #40
signal_period = 9#9


# testing date time
start = "2005-11-21"
#end = "2012-10-25"
#end = "2008-4-1"
# end = "2020-10-1"
# end = "2008-2-19"

#start = "2020-1-1"
#end = "2021-12-30"

end = "2016-5-21"

holdObdobje = 365

# end = "2020-11-12"

begin_time = datetime.datetime.now()

dowTickers = dow.endTickers # podatki o sezona sprememb dow jones indexa
stock_data = getStocks.getAllStockData(start_date=start, end_date=end)
# backtest(start, end, short_period, long_period, signal_period, dowTickers, stock_data, holdObdobje)

testirajNaPortfoliu(dowTickers, stock_data, holdObdobje)

print(datetime.datetime.now() - begin_time)


"""
test_ticker = "HD"
test_data = yf.download(test_ticker, start=start, end=end, progress=False)
test_data = test_data[['Close']].copy()
test_data = zacetniDf(test_data)  # dodamo stolpce
return_df = macd(short_period, long_period, signal_period, test_data, test_ticker, 0, 0, True)

MACD_trading_graph(short_period, long_period, signal_period, return_df, test_ticker)
profit_graph(return_df, 0, test_ticker, return_df["Total"].iat[-1])
"""