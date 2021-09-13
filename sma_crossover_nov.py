import math
import pandas_datareader.data as web
import pandas as pd
import datetime as datetime
from datetime import timedelta

import numpy as np
import matplotlib.pyplot as plt

import get_stock_data as getStocks
import utils as util
import dow_jones_companies as dow
import yfinance as yf



def days_between(d1, d2):

    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

def sma_crossover(sPeriod, lPeriod, df, ticker, starting_index, status, odZacetkaAliNe, holdObdobje):
    # naredimo nova stolpca za oba SMA
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
            df['Shares'].iat[x] = np.nan_to_num(df['Shares'].iat[x - 1])  # prenesemo prejsnje st delnic naprej
            if x != starting_index:  # za izjeme ko dodamo nov ticker in ne smemo zbrisat starting cash
                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x - 1])  # prenesemo prejsnji Cash naprej
            elif x == starting_index and odZacetkaAliNe is False:  # takrat ko je isto podjetje kot prej
                df['Cash'].iat[x] = np.nan_to_num(df['Cash'].iat[x - 1])  # prenesemo prejsnji Cash naprej
            df['Total'].iat[x] = (df['Cash'].iat[x] + df['Shares'].iat[x] * df['Close'].iat[
                x])  # izracunamo total TODO probably treba dodat fees
            df['Ticker'].iat[x] = ticker
            df['Buy'].iat[x] = df['Buy'].iat[x - 1]
            df['Sell'].iat[x] = df['Sell'].iat[x - 1]
            df['Buy-date'].iat[x] = df['Buy-date'].iat[x - 1]
            df['Sell-date'].iat[x] = df['Sell-date'].iat[x - 1]


        else:  # zacetek tabele -> inicializacija vrednosti
            df['Shares'].iat[x] = np.nan_to_num(df['Shares'].iat[x])
            if df['Cash'].iat[x] == 0:  # nimamo se denarja
                df['Cash'].iat[x] = util.getMoney()
            df['Total'].iat[x] = (df['Cash'].iat[x] + (df['Shares'].iat[x] * df['Close'].iat[x]))
            df['Ticker'].iat[x] = ticker

        pretekli_dnevi_buy = 0
        if df["Buy-date"].iat[x] != "": #buy_date != "":
            pretekli_dnevi_buy = days_between(df["Buy-date"].iat[x], df.index[x].strftime("%Y-%m-%d"))

        #pretekli_dnevi_sell = 0
        #if df["Sell-date"].iat[x] != "":
        #    pretekli_dnevi_sell = days_between(df["Sell-date"].iat[x], df.index[x].strftime("%Y-%m-%d"))


        # sSMA > lSMA -> buy signal
        if df[f'SMA-{sPeriod}'].iat[x] > df[f'SMA-{lPeriod}'].iat[x]:

            # ce bi hotel tudi tuki das to v if za kupit -> and vmes_eno_leto
            vmes_eno_leto = False
            if check == 0:
                vmes_eno_leto = True
            elif check == 1:
                preteklo = days_between(df["Sell-date"].iat[x], df.index[x].strftime("%Y-%m-%d"))
                if preteklo >= holdObdobje: # 7 glede na obdobje ki ga gledam 30dni = mesec 365_= leto
                    vmes_eno_leto = True
                else:
                    vmes_eno_leto = False

            can_buy = math.floor(df['Cash'].iat[x] / (df['Close'].iat[x] + util.percentageFee(util.feePercentage,
                                                                                                    df[
                                                                                                        'Close'].iat[
                                                                                                        x])))  # to je biu poopravek, dalo je buy signal tudi ce ni bilo denarja za kupit delnico
            if check != 2 and can_buy > 0:  # zadnji signal ni bil buy in imamo dovolj denarja za nakup

                # kupi kolikor je možno delnic glede na cash -> drugi del je cena delnice + fee na nakup delnice
                stDelnic = math.floor(df['Cash'].iat[x] / (
                            df['Close'].iat[x] + util.percentageFee(util.feePercentage, df['Close'].iat[x])))
                buyPrice = stDelnic * df['Close'].iat[
                    x]  # stDelnic * njihova cena -> dejanski denar potreben za nakup TODO tudi tuki dodaj fees
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

        # sSMA < lSMA -> sell signal
        elif df[f'SMA-{sPeriod}'].iat[x] < df[f'SMA-{lPeriod}'].iat[x] and pretekli_dnevi_buy >= holdObdobje:

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
                # sell_date = df.index[x].strftime("%Y-%m-%d") # zapisem datum nakupa
                # print(f"buy: ", df["Buy-date"].iat[x], "sell: ", df["Sell-date"].iat[x])
                razlika_datumov = days_between(df["Buy-date"].iat[x], df["Sell-date"].iat[x])
                #df["Pretekli cas"].iat[x] = razlika_datumov

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
    # SMA_trading_graph(sPeriod, lPeriod, df, ticker)
    # profit_graph(df, 0, ticker)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    # print(df)
    # newDf = df[['Close', 'Buy', 'Sell', 'Cash', 'Shares', 'Total']].copy()
    # print(newDf)
    return df


def SMA_trading_graph(sPeriod, lPeriod, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    # cena
    df['Close'].plot(ax=ax1, color='black', alpha=0.5)

    # kratki in dolgi SMA
    df[[f'SMA-{sPeriod}', f'SMA-{lPeriod}']].plot(ax=ax1, linestyle="--")

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


def zacetniDf(data):
    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako
    # kreiramo nova stolpca za buy/sell signale
    data[f'SMA-{short_period}'] = np.nan
    data[f'SMA-{long_period}'] = np.nan
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
    #data["Pretekli cas"] = 0

    return data


def backtest(start, end, sma_period_short, sma_period_long, dowTickers, stock_data, hold_obdobje):
    obdobja = []

    # hardcodam za testno mnozico

    if start == "2016-5-21":
        obdobja.append(start)
    for x in dowTickers:

        if x >= start and x < end:  ## zna bit da je tuki treba se = dat
            obdobja.append(x)

    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if end > zadnjeObdobje:
        obdobja.append(end)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    print("Obdobja: ", obdobja)

    portfolio = {}
    izloceniTickerji = []
    starting_companies = []
    begining = start  # "2005-11-21"
    sezIzlocenih = []

    # te imajo probleme pri koncnem obdobju 2008-2-19
    problematicni = ["MO", "HON"]

    for i in range(0, len(obdobja) - 1):  # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetnoObdobje = obdobja[i]
        koncnoObdobje = obdobja[i + 1]
        print(i, zacetnoObdobje, "+", koncnoObdobje)

        # zacetek
        if zacetnoObdobje == begining:
            # hardcodam za zacetno od ucne in testne mnozice
            print("V zacetnem")

            if zacetnoObdobje == "2005-11-21":
                starting_companies = dowTickers[zacetnoObdobje]["all"]
            elif zacetnoObdobje == "2016-5-21":
                starting_companies = dowTickers["2015-3-19"]["all"]

            # starting_companies.remove("GM") # odstranimo časnovno linijo GM ker nimamo podatkov
            izloceniTickerji.append("GM")  # dodamo GM pod izlocene

            # starting_companies = dowTickers[zacetnoObdobje]["all"]
            # trejdamo z all od zacetnegaObdobja
            for x in starting_companies:
                print("Company: ", x)
                # if x != "GM" and x != "HWM":
                # data = web.DataReader(x, 'yahoo', start=zacetnoObdobje, end=koncnoObdobje)

                if x in problematicni and koncnoObdobje == "2008-2-19":  # to podjetje ima izjemo
                    print("Popravljam problematicne")
                    real_end_date = datetime.datetime.strptime(koncnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_end_date + datetime.timedelta(days=1)

                    data = getStocks.getCompanyStockDataInRange(date_from=zacetnoObdobje, date_to=plus_one_start_date, companyTicker=x, allStockData=stock_data) # yf.download(x, start=zacetnoObdobje, end=plus_one_start_date, progress=False)
                    data = data[['Close']].copy()
                    data = zacetniDf(data)  # dodamo stolpce
                    return_df = sma_crossover(sma_period_short, sma_period_long, data, x, 0, 0, True, hold_obdobje)
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
                        return_df = sma_crossover(sma_period_short, sma_period_long, data, x, 0, 0, True, hold_obdobje)
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
                    nov_ticker = dowTickers[zacetnoObdobje]["added"][
                        dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    print(odstranjenTicker, "->", nov_ticker)
                    # naslednje_obdobje = '2008, 2, 19'
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                    modified_date = plus_one_start_date - datetime.timedelta(
                        days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov
                    # new_df = web.DataReader(nov_ticker, 'yahoo', start=modified_date, end=koncnoObdobje)
                    new_df = getStocks.getCompanyStockDataInRange(date_from=modified_date, date_to=koncnoObdobje, companyTicker=nov_ticker, allStockData=stock_data) # yf.download(nov_ticker, start=modified_date, end=koncnoObdobje, progress=False)

                    new_df = new_df[['Close']].copy()
                    new_df = zacetniDf(new_df)
                    # ex_df = index[odstranjenTicker]
                    ex_df = portfolio[odstranjenTicker]
                    ex_data = ex_df.tail(1)

                    # print("Shares", ex_data["Shares"][0])
                    # print("Cash", ex_data["Cash"][0])
                    # TODO tukaj pride error -> popravljeno
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

                        # print("Cash before: ", ex_df['Cash'].iloc[-1])
                        # print("UpdateCash: ", np.nan_to_num(ex_df['Cash'].iloc[-1]) + prodanoFees)
                        ex_df['Cash'].iat[-1] = np.nan_to_num(ex_df['Cash'].iat[-1]) + prodanoFees  # posodbi cash
                        # print("RealUpdated Cash ", ex_df['Cash'].iloc[-1])
                        ex_df['Shares'].iat[-1] = 0
                        ex_df['Total'].iat[-1] = ex_df["Cash"].iat[-1]

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
                    new_returns = sma_crossover(sma_period_short, sma_period_long, new_df, nov_ticker, starting_index,
                                                0,
                                                True, hold_obdobje)  # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

                    added_returns = new_returns[plus_one_start_date:]
                    concat_returns = pd.concat([ex_df, added_returns])
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
                plus_one_start_date = real_start_date + datetime.timedelta(days=1)  # adding one day
                # modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov

                if ostaliTicker != "GM":

                    totals = portfolio[ostaliTicker]
                    zadnji_signal = 0
                    # TODO tuki spet error -> popravljeno
                    if totals['Shares'].iat[-1] == 0:
                        zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                    elif totals['Shares'].iat[-1] != 0:
                        zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                    print("Trenutni ostali ticker: ", ostaliTicker)
                    # new_data = web.DataReader(ostaliTicker, 'yahoo', start=plus_one_start_date, end=koncnoObdobje)
                    new_data = getStocks.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=ostaliTicker, allStockData=stock_data) # yf.download(ostaliTicker, start=plus_one_start_date, end=koncnoObdobje, progress=False)

                    new_data = new_data[['Close']].copy()
                    starting_index = len(totals)

                    concat_data = pd.concat([totals, new_data])

                    concat_totals = sma_crossover(sma_period_short, sma_period_long, concat_data, f"new{ostaliTicker}",
                                                  starting_index,
                                                  zadnji_signal, False, hold_obdobje)
                    portfolio[ostaliTicker] = concat_totals
                    # profit_graph(concat_totals, 0, f"new{ostaliTicker}", round(concat_totals['Total'].iat[-1], 4))

    totals = prikaziPodatkePortfolia(portfolio, sezIzlocenih, izloceniTickerji)

    return totals


def prikaziPodatkePortfolia(portfolio, sezIzlocenih, izloceniTickerji):
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
    print(sezIzlocenih)
    print(izloceniTickerji)

    return allFunds


def najdiOptimalneParametreNaEnem(data, ticker, hold_obdobje):
    print("Testiram na ucni mnozici")
    testni_rezultati = {}
    counter = 0
    for long in range(100, 210, 10):
        # print("Trenutna Long vrednost: ", long)

        for short in range(40, 110, 10):
            testni_rezultati[f"[{short},{long}]"] = {}
            print(f"Kombinacija: Short = {short} , Long = {long}")
            testni_rezultati[f"[{short},{long}]"] = sma_crossover(short, long, data, ticker, 0, 0, True, hold_obdobje)
            # print("Trenutna Short vrednost: ", short)
            print()
            counter += 1

    print("Counter: ", counter)

    return testni_rezultati


def testirajNaEnemPodjetju(hold_obdobje):
    test_ticker = "HD"
    test_data_ucna = yf.download(test_ticker, start="2005-11-21", end="2016-5-21", progress=False)
    test_data_ucna = test_data_ucna[['Close']].copy()
    test_data_ucna = zacetniDf(test_data_ucna)  # dodamo stolpce
    # return_df = sma_crossover(short_period, long_period, test_data, test_ticker, 0, 0, True)

    rez_ucni = najdiOptimalneParametreNaEnem(test_data_ucna, test_ticker, hold_obdobje)
    print(datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        print(x, ": ", rez_ucni[x]['Total'].iat[-1])

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])

    # to dej stran, se ne testira na testni
    test_data_testna = yf.download(test_ticker, start="2016-5-21", end="2021-1-1", progress=False)
    test_data_testna = test_data_testna[['Close']].copy()
    test_data_testna = zacetniDf(test_data_testna)  # dodamo stolpce
    rez_testni = najdiOptimalneParametreNaEnem(test_data_testna, test_ticker, hold_obdobje)

    rez_total_testna = {}
    for x in rez_testni:
        rez_total_testna[x] = {}
        rez_total_testna[x] = rez_testni[x]['Total'].iat[-1]
        print(x, ": ", rez_testni[x]['Total'].iat[-1])

    print()
    print("Sorted testni!")
    print()

    sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testna.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_testni:
        print(x, ": ", sorted_rez_total_testni[x])



def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]

    for long in long_values: # 210 range(100, 210, 10)
        # print("Trenutna Long vrednost: ", long)

        for short in short_values: # 110 range(40, 110 , 10)

            if short != long:
                ucni_rezultati[f"[{short},{long}]"] = {}
                print(f"Kombinacija: Short = {short} , Long = {long}")
                # print debug
                #print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
                temp = backtest(start_period, end_period, short, long, dowTickers, stock_data, hold_obdobje)
                #print("Data: ", temp)
                ucni_rezultati[f"[{short},{long}]"] = temp
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



# 70% = 11-21-2005 do 21-5-2016 UCNA

# 30% = 21-5-2016 do 1-1-2021 TESTNA

# SMA crossover strategy
# datetmie = leto, mesec, dan
short_period = 80
long_period = 180

# testing date time
start = "2005-11-21"
# end = "2008-4-1"
# end = "2020-10-1"
# end = "2008-2-19"

end = "2016-5-21"
# end = "2020-11-12"

# start = "2016-5-21"

# end = "2021-1-1"

# end = "2021-1-1"
holdObdobje = 1


begin_time = datetime.datetime.now()

# testirajNaEnemPodjetju()

dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa
stock_data = getStocks.getAllStockData(start_date=start, end_date=end)

# backtest(start, end, short_period, long_period, dowTickers, stock_data, holdObdobje)

testirajNaPortfoliu(dowTickers, stock_data, holdObdobje)

print(datetime.datetime.now() - begin_time)

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
