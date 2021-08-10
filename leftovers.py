
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

