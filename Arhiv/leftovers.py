
# iz bollinger bands

"""
# gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        #print(ticker)
        tickerTotals = portfolio[ticker]
        allShares[ticker] = tickerTotals['Shares'].iat[-1]

        if (count == 0):
            allFunds = tickerTotals[['Total']].copy()
        else:
            allFunds['Total'] = allFunds['Total'] + tickerTotals['Total']

        count += 1

    print(allFunds)
    profit_graph(allFunds, 1, "Portfolio", round(allFunds['Total'].iat[-1], 4))

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

"""



"""
    # gremo cez cel portfolio in sestejemo Totals ter potem plotamo graf

    allFunds = pd.DataFrame
    allShares = {}
    count = 0
    print("Pred totals: ", portfolio.keys())
    for ticker in portfolio:

        #print(ticker)
        tickerTotals = portfolio[ticker]
        allShares[ticker] = tickerTotals['Shares'].iloc[-1]

        #nan = tickerTotals["Total"].loc["2008-2-19"]
        #print(nan)

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

    print("Izloceni")
    print(sezIzlocenih)
    print(izloceniTickerji)
"""






# pazi ko zlimaš skupi je se podvoji vrstica z istim datumom, končna prej, začetna zdej

# print(index)

# glede na end date obdobja gledam v slovar sprememb kje breajkat
# slovar spremmemb je dowTickers -> spremembe indexa skozi leta

# ce je obdobje po zadnji spremembi indexa prekratko sepravi manj kot long_period dni potem je problem -> dal sem long_period * 2

# slovar tekocega indexa key -> ticker, value dataframe, ko se remova in pol adda concatat dataframe skupaj
# na mesto removed podjetja se doda ticker added podjetja, na value mesto pa se concata dataframe prejšnjega podjetja
# isto se prepiše ticker v datafrejmu



# staro zaganjanje
"""

# Dow Jones Index podjetja not 20 let 1999 - 2020
tickers = ['HD', 'INTC'] #, 'IBM', 'AXP', 'BA', 'CAT', 'KO', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'MMM', 'PG', 'WMT', 'DIS']


# tuki potem for za usa podjetja iz dow jones indexa

allFunds = pd.DataFrame
allShares = {}

for i in range(len(tickers)):
    # pridobimo podatke preko apija
    data = web.DataReader(tickers[i], 'yahoo', start='2000, 1, 1', end='2020, 1, 1')
    data = data[['Adj Close']].copy()
    totals = sma_crossover(short_period, long_period, data, tickers[i])

    allShares[tickers[i]] = totals['Shares'].iloc[-1]
    if (i == 0):
        allFunds = totals[['Total']].copy()
    else:
        allFunds['Total'] = allFunds['Total'] + totals['Total']

print(allFunds)
profit_graph(allFunds, 1, round(allFunds['Total'].iloc[-1], 4))

startFunds = len(tickers) * util.getMoney()
endFunds = allFunds['Total'].iloc[-1]

print("Zacetna sredstva: ", startFunds, "$")
print("Skupna sredstva portfolia: ", round(allFunds['Total'].iloc[-1], 4), "$")
print("Profit: ", round(allFunds['Total'].iloc[-1] - (len(tickers) * util.getMoney()), 4), "$")
print("Kumulativni donos v procentih: ", round((endFunds - startFunds) / startFunds, 4) * 100, "%")


print("Delnice, ki jih še imamo v portfoliu:")
for key, value in allShares.items():
    print(key, " : ", value)

"""

"""""

for x in starting:

    data = web.DataReader(x, 'yahoo', start='2005, 11, 21', end='2008, 2, 19')
    data = data[['Adj Close']].copy()
    data = zacetniDf(data) # dodamo stolpce
    return_df = sma_crossover(short_period, long_period, data, x, 0, 0, True)
    index[x] = return_df

# print(index)

print("ZAMENJAJ")
# zamenjamo glede na obdobje indexa
for x in index:

    if x in odstrani['removed']:

        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            # print()
            # print(index[x].tail(1))
            # print()
        # print(index[x].tail(1)["Shares"])
        # print(index[x].tail(1)["Cash"])
        # print(x, "->", dodaj["added"][odstrani["removed"].index(x)])
        nov_ticker = dodaj["added"][odstrani["removed"].index(x)]
        naslednje_obdobje = '2008, 2, 19'
        real_start_date = datetime.datetime.strptime(naslednje_obdobje, "%Y, %m, %d")
        plus_one_start_date = real_start_date + datetime.timedelta(days=1)  #  adding one day
        modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov
        new_df = web.DataReader(nov_ticker, 'yahoo', start=modified_date, end=end)
        new_df = new_df[['Adj Close']].copy()
        new_df = zacetniDf(new_df)
        ex_df = index[x]
        ex_data = ex_df.tail(1)

        # print("Shares", ex_data["Shares"][0])
        # print("Cash", ex_data["Cash"][0])


        if ex_df["Shares"][-1] == 0:  # super samo prepisemo kes
            new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]

        elif ex_df["Shares"][-1] > 0: # moramo prodat delnice in jih investirat v podjetje ki ga dodajamo

            prodano = (ex_df['Shares'].iloc[-1] * ex_df['Adj Close'].iloc[-1])  # delnice v denar
            prodanoFees = util.fees(prodano)  # ostanek denarja po fees
            sellPrice = prodanoFees
            ex_df['Sell'].iloc[-1] = prodanoFees  # zapisemo sell price
            ex_df['Profit'].iloc[-1] = util.profit(ex_df['Buy'].iloc[-1], sellPrice)

            ex_df['Buy'].iloc[-1] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell

            # ce je dobicek pozitiven zaracunamo davek na dobicek in ga odstejemo od prodanoFees da dobimo ostanek
            if (ex_df['Profit'].iloc[-1] > 0):
                prodanoFees = prodanoFees - util.taxes(ex_df['Profit'].iloc[-1])

            # print("Cash before: ", ex_df['Cash'].iloc[-1])
            # print("UpdateCash: ", np.nan_to_num(ex_df['Cash'].iloc[-1]) + prodanoFees)
            ex_df['Cash'].iloc[-1] = np.nan_to_num(ex_df['Cash'].iloc[-1]) + prodanoFees  # posodbi cash
            # print("RealUpdated Cash ", ex_df['Cash'].iloc[-1])
            ex_df['Shares'].iloc[-1] = 0
            ex_df['Total'].iloc[-1] = ex_df["Cash"].iloc[-1]

            # prejsni df je posodobljen in delnice so prodane, samo prepisemo Cash v new_df
            # print("Notri", ex_df.iloc[-1])
            new_df["Cash"].loc[plus_one_start_date] = ex_df["Cash"][-1]
            new_df["Total"].loc[plus_one_start_date] = ex_df["Cash"][-1]

        odvec = new_df[:plus_one_start_date]
        starting_index = len(odvec) - 1
        # concat_new = pd.concat([ex_df, new_df])
        # starting_index = len(ex_df)
        # concat_new["Ticker"].iloc[starting_index] = dodaj["added"][odstrani["removed"].index(x)] # zapisemo nov ticker
        # concat_new["Total"].iloc[starting_index] = concat_new["Cash"].iloc[starting_index]

        # startamo trading algo
        new_returns = sma_crossover(short_period, long_period, new_df, nov_ticker, starting_index, 0, True) # zadnji argument True ker je razlicen ticker in zacnemo od zacetka trejdat, isti -> False ker samo nadaljujemo trejdanje

        added_returns = new_returns[plus_one_start_date:]
        concat_returns = pd.concat([ex_df, added_returns])
        profit_graph(concat_returns, 1, round(concat_returns['Total'].iloc[-1], 4))
        new_index = {nov_ticker if k == x else k: v for k, v in index.items()}
        new_index[nov_ticker] = concat_returns
        isOk = new_index[nov_ticker]
        index = new_index
        print(index)

    # end if x is in removed
    elif x not in odstrani['removed']:

        naslednje_obdobje = '2008, 2, 19'
        real_start_date = datetime.datetime.strptime(naslednje_obdobje, "%Y, %m, %d")
        plus_one_start_date = real_start_date + datetime.timedelta(days=1)  #  adding one day
        # modified_date = plus_one_start_date - datetime.timedelta(days=(long_period * 2))  # odstevamo long period da dobimo dovolj podatkov

        totals = index[x]
        zadnji_signal = 0

        if totals['Shares'].iloc[-1] == 0:
            zadnji_signal = 1  # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
        elif totals['Shares'].iloc[-1] != 0:
            zadnji_signal = 2  # imamo delnice tako da jih lahko samo prodamo zdej

        new_data = web.DataReader(x, 'yahoo', start=plus_one_start_date, end=end)
        new_data = new_data[['Adj Close']].copy()
        starting_index = len(totals)

        concat_data = pd.concat([totals, new_data])

        concat_totals = sma_crossover(short_period, long_period, concat_data, f"new{x}", starting_index, zadnji_signal, False)
        index[x] = concat_totals
        profit_graph(concat_totals, 1, round(concat_totals['Total'].iloc[-1], 4))




# tuki naprej je ce je isto podjetje in samo nadaljujes trejdanje


# v enem delu
data1 = web.DataReader("HD", 'yahoo', start='2000, 1, 1', end='2020, 1, 1')
data1 = data1[['Adj Close']].copy()
# v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako kreiramo nova stolpca
# za buy/sell signale
data1['Buy'] = np.nan
data1['Sell'] = np.nan
data1['Cash'] = 0
data1['Shares'] = 0
data1['Profit'] = 0
data1['Total'] = 0
data1['Ticker'] = ""
totals1 = sma_crossover(short_period, long_period, data1, "HD")
#profit_graph(totals1, 1, round(totals1['Total'].iloc[-1], 4))


# loceno
data = web.DataReader("HD", 'yahoo', start='2000, 1, 1', end='2010, 1, 1')
data = data[['Adj Close']].copy()

# v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako kreiramo nova stolpca
# za buy/sell signale
data[f'SMA-{short_period}'] = np.nan
data[f'SMA-{long_period}'] = np.nan
data['Buy'] = np.nan
data['Sell'] = np.nan
data['Cash'] = 0
data['Shares'] = 0
data['Profit'] = 0
data['Total'] = 0
data['Ticker'] = ""

zadnji_signal = 0
totals = sma_crossover(short_period, long_period, data, "HD", 0, zadnji_signal, False)
profit_graph(totals, 1, round(totals['Total'].iloc[-1], 4))


if totals['Shares'].iloc[-1] == 0:
    zadnji_signal = 1 # nimamo delnic kar pomeni da smo jih prodali in jih moramo zdej kupit
elif totals['Shares'].iloc[-1] != 0:
    zadnji_signal = 2 # imamo delnice tako da jih lahko samo prodamo zdej



new_data = web.DataReader("HD", 'yahoo', start='2010, 1, 1', end='2020, 1, 1')
new_data = new_data[['Adj Close']].copy()
starting_index = len(totals)

concat_data = pd.concat([totals, new_data])


concat_totals = sma_crossover(short_period, long_period, concat_data, "newHD", starting_index, zadnji_signal, False)
profit_graph(concat_totals, 1, round(concat_totals['Total'].iloc[-1], 4))
"""""




"""

def dividendPayouthGrowth(company_dividend):

    dolzina = len(company_dividend)
    print(dolzina)

    keys = list(company_dividend.keys())
    for i in range(len(company_dividend)):

        payoutGrowth = 0
        if i == 0:
            company_dividend[keys[i]]["dividendPayoutGrowth"] = company_dividend[keys[i]]["dividendPerShare"]
        else:
            if company_dividend[keys[i]]["dividendPerShare"] != 0 and company_dividend[keys[i - 1]]["dividendPerShare"] != 0:
                payoutGrowth = company_dividend[keys[i]]["dividendPerShare"] / company_dividend[keys[i - 1]]["dividendPerShare"]
                company_dividend[keys[i]]["dividendPayoutGrowth"] = (payoutGrowth - 1)
            else:
                company_dividend[keys[i]]["dividendPayoutGrowth"] = 0

    return company_dividend



"""


"""""
zacetnaSezona = endTickers['1999-11-1']

index = {}
for x in zacetnaSezona["all"]:

    if x == "EK":
        x = "KODK"
    # data = yf.download(x, start='1999-11-1', end="2020-11-12", progress=False)
    #data = data[['Adj Close']].copy()
    #index[x] = data

for x in index:
    print(x)
    print(index[x])

print(zacetnaSezona["all"])
print(len(zacetnaSezona["all"]))

#for x in obrnjenSlovarImen["November 1, 1999"]["all"]:
    #print("PAR: ", x, zacetnaSezona["all"][obrnjenSlovarImen["November 1, 1999"]["all"].index(x)])

"""""


def preveri():

    prva = endTickers["1999-11-1"]["all"]

    for x in prva:

        if x != "EK":
            if x == "HWM":
                x = "AA"
            print("Podjetje: ", x)
            data = yf.download(x, start="1999-11-1", end="2020-11-12", progress=False)
            print(data)

    print("DRUGA:")
    druga = endTickers["2005-11-21"]["all"]
    for x in druga:

        if x == "HWM":
            x = "AA"
        print("Podjetje: ", x)
        data = yf.download(x, start="2005-11-21", end="2020-11-12", progress=False)
        print(data)


# preveri()


dija_divisor = 0.123017848#0.246#0.123017848 # 0.147 #as of Sept. 2019#0.184 #0.123017848 # leta 13.6.2007
                # 0.15198707565833   Nov. 24, 2020
                # Since June 3, 2021, the Dow Divisor is 0.15188516925198

def graf(plot_data):
    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle("DIJA 2000 - 2020")
    ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
    plot_data['Close'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)

    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()

def brezGM():
    start = '2005-11-21'
    end = "2009-6-8"
    obdobjaGM = []
    for x in endTickers:

        if x <= end:
            obdobjaGM.append(x)

    print("Obdobja: ", obdobjaGM)

    moj_dija = pd.DataFrame()
    skupno = pd.DataFrame()
    prejsnje_obdobje = pd.DataFrame()
    prvi_dan = pd.DataFrame()
    for indexLeto in range(0, len(obdobjaGM) - 1):  # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetno = obdobjaGM[indexLeto]
        koncno = obdobjaGM[indexLeto + 1]

        #if zacetno == "2008-2-19":
            #nov dija_divisor


        for i in range(0, len(endTickers[zacetno]["all"])): # dobimo cene za all podjetja v tem obdobju

            podjetje = endTickers[zacetno]["all"][i]

            if podjetje != "GM":
                if podjetje == "HWM":
                    podjetje = "AA"
                data = yf.download(podjetje, start=zacetno, end=koncno, progress=False)

                if i == 0:
                    print(i, indexLeto)
                    skupno = data[['Adj Close']].copy()
                    print("Skupno iteracija: ",skupno)
                    if zacetno == start:
                        prvi_dan[podjetje] = data.head(1)["Adj Close"].copy()

                elif i > 0:
                    skupno["Adj Close"] = skupno["Adj Close"] + data["Adj Close"]
                    if zacetno == start:
                        prvi_dan[podjetje] = data.head(1)["Adj Close"].copy()

        if indexLeto != 0: # nismo v prvi iteraciji

            skupno["Adj Close"] = skupno["Adj Close"].div(dija_divisor) # sum delimo z divisorjem in dobimo vrednost dija v tem obdobju
            concat_data = pd.concat([prejsnje_obdobje, skupno])
            moj_dija = concat_data[['Adj Close']].copy()
            prejsnje_obdobje = moj_dija[['Adj Close']].copy()

        elif indexLeto == 0:
            print("zacetek skupno", skupno)
            skupno["Adj Close"] = skupno["Adj Close"].div(dija_divisor) # sum delimo z divisorjem in dobimo vrednost dija v tem obdobju
            prejsnje_obdobje = skupno[['Adj Close']].copy()
            print("zacetek skupno divisor", prejsnje_obdobje)


        print("Skupno: ", skupno)

    print(moj_dija)
    prvi_dan["sum"] = prvi_dan.sum(axis=1)
    print("sum prvi dan: ", prvi_dan["sum"])
    print("sum prvi dan / divisor: ", prvi_dan["sum"].div(dija_divisor))

    # graf(moj_dija)

    # ploting DIJA 2000 - 2010

    dija = yf.download("^DJI", start=start, end=end, progress=False)
    fig = plt.figure(figsize=(8, 6), dpi=200)

    pravi = pd.DataFrame
    pravi = dija[['Adj Close']].copy()
    pravi["sestevekDelnic"] = moj_dija[['Adj Close']].copy()
    pravi["divisor"] = pravi["sestevekDelnic"] / pravi["Adj Close"]
    pravi["mojDOW"] = pravi["sestevekDelnic"] / pravi["divisor"]






    fig.suptitle(f"DJIA 2005-11-21 do 2009-6-8 vs sintetični DJIA brez podjetja GM, divisor: {dija_divisor}")
    ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
    dija['Adj Close'].plot(ax=ax1, label="Vrednost pravega DJIA", color='black', alpha=0.5)
    moj_dija["Adj Close"].plot(ax=ax1, label="Vrednost sintetičnega DJIA", color='green')
    # pravi["mojDOW"].plot(ax=ax1, label="Vrednost sredstev sintetičnega DIJA",linestyle="--", color='green')


    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()

    # graf(dija)
    #zadnji = dija.tail(1).index.item()
    #print(zadnji)

    print("Zadnji dan vrednost pravi DJIA: ", dija["Adj Close"].iloc[-1])
    print("Zadnji dan vrednost sintetični DJIA: ", moj_dija["Adj Close"].iloc[-1])
    print("Divisor: ", dija_divisor)
    prvi_dan["sum"].iloc[0] = prvi_dan["sum"].iloc[0] / dija_divisor
    print("prvi dan vrednost: ", prvi_dan["sum"].iloc[0])

    print("Donosnost moja: ", pravi["mojDOW"].iloc[-1] - pravi["mojDOW"].iloc[0])
    print("Donosnost original: ", dija["Adj Close"].iloc[-1] - dija["Adj Close"].iloc[0])


    # problematicni KODK , GM



# brezGM()


"""""
start = '2005-11-21'
end = "2009-6-8"
obdobjaGM = []
for x in endTickers:

    if x <= end:
        obdobjaGM.append(x)

print("Obdobja: ", obdobjaGM)


moj_dija = {}

index = pd.date_range(start=start, end=end, freq='D')
columns = ["Close"]
plot_data = pd.DataFrame(index=index, columns=columns)
plot_data = plot_data.fillna(0)
skupno = pd.DataFrame()
for leto in range(0, len(obdobjaGM) - 1): # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

    zacetno = obdobjaGM[leto]
    koncno = obdobjaGM[leto + 1]
    for i in range(0, len(endTickers[zacetno]["all"])):

        podjetje = endTickers[zacetno]["all"][i]

        if podjetje != "GM":
            data = yf.download(podjetje, start=zacetno, end=koncno, progress=False)

            if i == 0 and zacetno == start:
                skupno = data[['Close']].copy()

            elif i > 0:
                skupno["Close"] = skupno["Close"] + data["Close"]

    print("Skupno: ", skupno)
    plot_data.merge(skupno, left_index=True, right_index=True, how='inner')
    # plot_data.sum(skupno, )
    print("plot_data:",  plot_data)
    #graf(plot_data)
    #plot_data["Close"] = plot_data["Close"].addskupno["Close"]



"""""

        # print(endTickers[zacetno]["all"][i])
"""""
print("removed", endTickers[zacetno]["removed"])
print("added", endTickers[zacetno]["added"])
print(endTickers[zacetno]["all"])
print()
"""""

"""""
# ploting DIJA 2000 - 2010

dija = yf.download("^DJI", start='1999-11-1', end="2020-11-12", progress=False)
fig = plt.figure(figsize=(8, 6), dpi=200)

fig.suptitle("DIJA 2000 - 2020")
ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
dija['Adj Close'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)

legend = plt.legend(loc="upper left", edgecolor="black")
legend.get_frame().set_alpha(None)
legend.get_frame().set_facecolor((0, 0, 1, 0.1))
plt.show()

zadnji = dija.tail(1).index.item()
print(zadnji)

print("Zadnji dan vrednost: ", dija["Close"].iloc[-1])
# problematicni KODK , GM
"""""

