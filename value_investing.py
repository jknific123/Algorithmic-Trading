import math

import pandas_datareader.data as web
import pandas as pd
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
import utils as util
import dow_jones_companies as dow
import yfinance as yf
import requests
import fundamental_indicators as fundamentals

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30

million = 1000000
hundred_million = 100 * million

# vrne naslednji delovni datum ce trenutni datum ni delovni dan, uazme date time in vrne datum v string formatu
def to_week_day(date):
    if date.isoweekday() in set((6, 7)):
        date += datetime.timedelta(days=-date.isoweekday() + 8)
    return date.strftime("%Y-%m-%d")


def mixed_fundamentals_strategy(start_date, end_date, df, ticker, starting_index, status, odZacetkaAliNe, fundamental_data):


    # global hundred_million
    global hundred_million
    company_data = fundamentals.getDataCompany(ticker, start_date, end_date, fundamental_data)
    fundamentals.printData(company_data)



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
            df['Shares'].iloc[x] = np.nan_to_num(df['Shares'].iloc[x - 1])  # prenesemo prejsnje st delnic naprej
            if x != starting_index:  # za izjeme ko dodamo nov ticker in ne smemo zbrisat starting cash
                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x - 1])  # prenesemo prejsnji Cash naprej
            elif x == starting_index and odZacetkaAliNe is False: # takrat ko je isto podjetje kot prej
                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x - 1])  # prenesemo prejsnji Cash naprej
            df['Total'].iloc[x] = (df['Cash'].iloc[x] + df['Shares'].iloc[x] * df['Adj Close'].iloc[x])  # izracunamo total TODO probably treba dodat fees
            df['Ticker'].iloc[x] = ticker
            df['Buy'].iloc[x] = df['Buy'].iloc[x - 1]
            df['Sell'].iloc[x] = df['Sell'].iloc[x - 1]


        else:  # zacetek tabele -> inicializacija vrednosti
            df['Shares'].iloc[x] = np.nan_to_num(df['Shares'].iloc[x])
            if df['Cash'].iloc[x] == 0: # nimamo se denarja
                df['Cash'].iloc[x] = util.getMoney()
            df['Total'].iloc[x] = (df['Cash'].iloc[x] + (df['Shares'].iloc[x] * df['Adj Close'].iloc[x]))
            df['Ticker'].iloc[x] = ticker



        # pridobim trenutni datum, datum lanskega reporta in list vseh datumov
        trenutni_datum = df.index[x].strftime("%Y-%m-%d")
        prvi_datum_v_company_data = list(company_data.keys())[0]
        vsi_datumi = list(company_data.keys())
        vsi_datumi.remove(prvi_datum_v_company_data) # da ga ne gledam 2x

        if x == 0:
            print("JE NA PRVEM MESTU")
            df["P/B ratio"].iloc[x] = company_data[prvi_datum_v_company_data]["P/B"]
            df["P/E ratio"].iloc[x] = company_data[prvi_datum_v_company_data]["P/E"]
            df["ROE"].iloc[x] = company_data[prvi_datum_v_company_data]["ROE"]
            df["MarketCap"].iloc[x] = company_data[prvi_datum_v_company_data]["marketCapitalization"]


        if trenutni_datum in vsi_datumi:
            print("JE V SLOVAR KEYS")
            df["P/B ratio"].iloc[x] = company_data[trenutni_datum]["P/B"]
            df["P/E ratio"].iloc[x] = company_data[trenutni_datum]["P/E"]
            df["ROE"].iloc[x] = company_data[trenutni_datum]["ROE"]
            df["MarketCap"].iloc[x] = company_data[trenutni_datum]["marketCapitalization"]


        # P/E < 15, P/B < 2, ROE > 15%, market cap > 100M$ -> BUY signal
        if (trenutni_datum in vsi_datumi and company_data[trenutni_datum]["P/E"] < 15 and company_data[trenutni_datum]["P/B"] < 2 and company_data[trenutni_datum]["ROE"] > 0.15 and company_data[trenutni_datum]["marketCapitalization"] > hundred_million) or (x == 0 and company_data[prvi_datum_v_company_data]["P/E"] < 15 and company_data[prvi_datum_v_company_data]["P/B"] < 2 and company_data[prvi_datum_v_company_data]["ROE"] > 0.15 and company_data[prvi_datum_v_company_data]["marketCapitalization"] > hundred_million):
            print("SEM V BUY")

            can_buy = math.floor(df['Cash'].iloc[x] / (df['Adj Close'].iloc[x] + util.percentageFee(util.feePercentage, df['Adj Close'].iloc[x]))) # to je biu poopravek, dalo je buy signal tudi ce ni bilo denarja za kupit delnico
            if check != 2 and can_buy > 0: # zadnji signal ni bil buy in imamo dovolj denarja za nakup

                print("SEM V BUY IN BOM KUPIL", trenutni_datum)

                # kupi kolikor je možno delnic glede na cash -> drugi del je cena delnice + fee na nakup delnice
                stDelnic = math.floor(df['Cash'].iloc[x] / (df['Adj Close'].iloc[x] + util.percentageFee(util.feePercentage, df['Adj Close'].iloc[x])))
                buyPrice = stDelnic * df['Adj Close'].iloc[x]  # stDelnic * njihova cena -> dejanski denar potreben za nakup TODO tudi tuki dodaj fees
                df['Buy'].iloc[x] = buyPrice  # zapisemo buy price
                df['Sell'].iloc[x] = 0  # zapisemo 0 da oznacimo da je bil zadnji signal buy
                # za graf trgovanja
                df['Buy-Signal'].iloc[x] = df["Adj Close"].iloc[x]


                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x]) - (
                        stDelnic * df['Adj Close'].iloc[x])  # posodbi cash TODO tudi tuki dodaj fees
                df['Shares'].iloc[x] = df['Shares'].iloc[x] + stDelnic


                check = 2

        # P/E > 15, P/B > 2, ROE < 15%, market cap < 100M$ -> Sell signal
        #elif (trenutni_datum in slovar_keys and slovar_pb[trenutni_datum] > 1) or (x == 0 and slovar_pb[prvi_datum_v_slovar_pb] > 1): marketCapitalization
        elif (trenutni_datum in vsi_datumi and (company_data[trenutni_datum]["P/E"] > 15 or company_data[trenutni_datum]["P/B"] > 2 or company_data[trenutni_datum]["ROE"] < 0.15 or company_data[trenutni_datum]["marketCapitalization"] < hundred_million)) or (x == 0 and (company_data[prvi_datum_v_company_data]["P/E"] > 15 or company_data[prvi_datum_v_company_data]["P/B"] > 2 or company_data[prvi_datum_v_company_data]["ROE"] < 0.15 or company_data[prvi_datum_v_company_data]["marketCapitalization"] < hundred_million)):
            print("SEM V SELL")

            if check != 1 and check != 0:
                print("SEM V SELL IN BOM PORODAL", trenutni_datum)
                # TODO dodaj še davek na dobiček 27,5% -> done

                # prodaj vse delnic izracunaj profit in placaj davek
                prodano = (df['Shares'].iloc[x] * df['Adj Close'].iloc[x])  # delnice v denar
                prodanoFees = util.fees(prodano)  # ostanek denarja po fees
                sellPrice = prodanoFees
                df['Sell'].iloc[x] = prodanoFees  # zapisemo sell price
                df['Profit'].iloc[x] = util.profit(df['Buy'].iloc[x], sellPrice)
                # za graf trgovanja
                df['Sell-Signal'].iloc[x] = df["Adj Close"].iloc[x]
                df['Buy'].iloc[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell

                # ce je dobicek pozitiven zaracunamo davek na dobicek in ga odstejemo od prodanoFees da dobimo ostanek
                if (df['Profit'].iloc[x] > 0):
                    prodanoFees = prodanoFees - util.taxes(df['Profit'].iloc[x])

                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x]) + prodanoFees  # posodbi cash
                df['Shares'].iloc[x] = 0
                # updejtamo total
                df['Total'].iloc[x] = df['Cash'].iloc[x]


                check = 1

    # print(df)
    # plotShares(df, ticker)
    # MACD_trading_graph(sPeriod, lPeriod, df, ticker)
    # profit_graph(df, 0, ticker)


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    # print(df)
    # newDf = df[['Adj Close', 'Buy', 'Sell', 'Cash', 'Shares', 'Total']].copy()
    # print(newDf)
    return df


def mojaFundamentalna_trading_graph(df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    # cena
    df['Adj Close'].plot(ax=ax1, color='black', label="Cena", alpha=0.5)
    # df[f'SMA-{sma_period}'].plot(ax=ax1 ,color='orange', linestyle="--")

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


def zacetniDf(data):

    # kreiramo nova stolpca za buy/sell signale
    data["P/E ratio"] = np.nan
    data["P/B ratio"] = np.nan
    data["ROE"] = np.nan
    data["MarketCap"] = np.nan
    data['Buy'] = np.nan
    data['Sell'] = np.nan
    data['Cash'] = 0
    data['Shares'] = 0
    data['Profit'] = 0
    data['Total'] = 0
    data['Ticker'] = ""
    data['Buy-Signal'] = np.nan
    data['Sell-Signal'] = np.nan

    return data


def backtest(start, end, dowTickers, fundamental_data):

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

                    data = yf.download(x, start=zacetnoObdobje, end=plus_one_start_date, progress=False)
                    data = data[['Adj Close']].copy()
                    data = zacetniDf(data)  # dodamo stolpce
                    return_df = mixed_fundamentals_strategy(zacetnoObdobje, koncnoObdobje, data, x, 0, 0, True, fundamental_data)
                    portfolio[x] = return_df

                else:

                    # izjema za podjetje GM, za katerega nimam podatkov zato samo naredim prazen dataframe
                    if x == "GM":
                        index = pd.date_range(zacetnoObdobje, "2009-6-8", freq='D')
                        columns = ["Adj Close"]
                        prazen = pd.DataFrame(index=index, columns=columns)
                        prazen = zacetniDf(prazen)
                        prazen["Cash"] = prazen["Cash"].add(util.getMoney())
                        prazen["Total"] = prazen["Cash"]
                        portfolio[x] = prazen

                    elif x != "GM":
                        data = yf.download(x, start=zacetnoObdobje, end=koncnoObdobje, progress=False)
                        data = data[['Adj Close']].copy()
                        data = zacetniDf(data)  # dodamo stolpce
                        return_df = mixed_fundamentals_strategy(zacetnoObdobje, koncnoObdobje, data, x, 0, 0, True, fundamental_data)
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
                    # modified_date = plus_one_start_date - datetime.timedelta( days=(sma_period * 2))  # odstevamo long period da dobimo dovolj podatkov
                    new_df = yf.download(nov_ticker, start=plus_one_start_date, end=koncnoObdobje, progress=False) # old:  start=modified_date

                    new_df = new_df[['Adj Close']].copy()
                    new_df = zacetniDf(new_df)
                    ex_df = portfolio[odstranjenTicker]
                    ex_data = ex_df.tail(1)


                    if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
                        new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]

                    elif ex_df["Shares"][-1] > 0:  # moramo prodat delnice in jih investirat v podjetje ki ga dodajamo

                        prodano = (ex_df['Shares'].iloc[-1] * ex_df['Adj Close'].iloc[-1])  # delnice v denar
                        prodanoFees = util.fees(prodano)  # ostanek denarja po fees
                        sellPrice = prodanoFees
                        ex_df['Sell'].iloc[-1] = prodanoFees  # zapisemo sell price
                        ex_df['Profit'].iloc[-1] = util.profit(ex_df['Buy'].iloc[-1], sellPrice)

                        ex_df['Buy'].iloc[-1] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell

                        # ce je dobicek pozitiven zaracunamo davek na dobicek in ga odstejemo od prodanoFees da dobimo ostanek
                        if (ex_df['Profit'].iloc[-1] > 0):
                            prodanoFees = prodanoFees - util.taxes(ex_df['Profit'].iloc[-1])

                        ex_df['Cash'].iloc[-1] = np.nan_to_num(ex_df['Cash'].iloc[-1]) + prodanoFees  # posodbi cash
                        ex_df['Shares'].iloc[-1] = 0
                        ex_df['Total'].iloc[-1] = ex_df["Cash"].iloc[-1]

                        # prejsni df je posodobljen in delnice so prodane, samo prepisemo Cash v new_df
                        new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]
                        new_df["Total"].loc[plus_one_start_date] = ex_df["Cash"][-1]

                    odvec = new_df[:plus_one_start_date]
                    starting_index = len(odvec) - 1

                    # startamo trading algo
                    new_returns = mixed_fundamentals_strategy(zacetnoObdobje, koncnoObdobje, new_df, nov_ticker, starting_index, 0,
                                                True, fundamental_data)  # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

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

                    if totals['Shares'].iloc[-1] == 0:
                        zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
                    elif totals['Shares'].iloc[-1] != 0:

                        zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

                    print("Trenutni ostali ticker: ", ostaliTicker)
                    new_data = yf.download(ostaliTicker, start=plus_one_start_date, end=koncnoObdobje, progress=False)

                    new_data = new_data[['Adj Close']].copy()
                    starting_index = len(totals)

                    concat_data = pd.concat([totals, new_data])

                    concat_totals = mixed_fundamentals_strategy(zacetnoObdobje, koncnoObdobje, concat_data, ostaliTicker, starting_index,
                                                  zadnji_signal, False, fundamental_data) # old: f"new{ostaliTicker}"
                    portfolio[ostaliTicker] = concat_totals



    # gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        #print(ticker)
        tickerTotals = portfolio[ticker]
        allShares[ticker] = tickerTotals['Shares'].iloc[-1]

        if (count == 0):
            allFunds = tickerTotals[['Total']].copy()
        else:
            allFunds['Total'] = allFunds['Total'] + tickerTotals['Total']

        count += 1

    print(allFunds)
    profit_graph(allFunds, 1, "Portfolio", round(allFunds['Total'].iloc[-1], 4))

    # se izpis podatkov portfolia
    startFunds = len(portfolio) * util.getMoney()
    endFunds = allFunds['Total'].iloc[-1]

    print("Zacetna sredstva: ", startFunds, "$")
    print("Skupna sredstva portfolia: ", round(allFunds['Total'].iloc[-1], 4), "$")
    # print("Profit: ", round(allFunds['Total'].iloc[-1] - (len(portfolio) * util.getMoney()), 4), "$")
    print("Profit: ", round(endFunds - startFunds, 4), "$")
    print("Kumulativni donos v procentih: ", round((endFunds - startFunds) / startFunds, 4) * 100, "%")


    print("Delnice, ki jih še imamo v portfoliu:")
    for key, value in allShares.items():
        print(key, " : ", value)


# Bollinger bands strategy
# datetmie = leto, mesec, dan


# testing date time
start = "2005-11-21"
#end = "2012-10-25"
#end = "2008-4-1"
#end = "2020-10-1"
end = "2020-11-21"
# end = "2008-2-19"

# end = "2011-11-21"

begin_time = datetime.datetime.now()

dowTickers = dow.endTickers # podatki o sezona sprememb dow jones indexa
fundamental_data = fundamentals.getAllFundamentals(fundamentals.vsi_tickerji)
backtest(start, end, dowTickers, fundamental_data)
print(datetime.datetime.now() - begin_time)

"""
test_ticker = "DIS"
test_data = yf.download(test_ticker, start=start, end=end, progress=False)
test_data = test_data[['Adj Close']].copy()
test_data = zacetniDf(test_data)  # dodamo stolpce
return_df = mixed_fundamentals_strategy(start, end, test_data, test_ticker, 0, 0, True)

mojaFundamentalna_trading_graph(return_df, test_ticker)
"""


