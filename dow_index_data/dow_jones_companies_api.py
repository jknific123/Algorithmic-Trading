# !/usr/bin/env python
import pandas as pd

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json


def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


url = "https://financialmodelingprep.com/api/v3/historical/dowjones_constituent?apikey=950c6e208107d01d9616681a4cf99685"
# print(get_jsonparsed_data(url))

companies = get_jsonparsed_data(url)

slovarImen = {}
slovarTickers = {}

# slovar -> key: leto
# value: lists
# podjetja v Dow Jones
# podjetja dodana v Dow Jones
# podjetja odstranjena iz Dow Jones

# naredimo liste
for i in companies:
    slovarImen[i["dateAdded"]] = {}
    slovarImen[i["dateAdded"]]["removed"] = []
    slovarImen[i["dateAdded"]]["added"] = []
    slovarImen[i["dateAdded"]]["all"] = []

    slovarTickers[i["dateAdded"]] = {}
    slovarTickers[i["dateAdded"]]["removed"] = []
    slovarTickers[i["dateAdded"]]["added"] = []
    slovarTickers[i["dateAdded"]]["all"] = []

# print(slovarImen)
# print()
for x in companies:
    # print(x)
    # print()

    # removed from index
    if x["addedSecurity"] == '':

        if x["removedSecurity"] == "Howmet Aerospace Inc":
            x["removedSecurity"] = "Alcoa Corporation"
            x["symbol"] = "AA"
        """
        """
        slovarImen[x["dateAdded"]]["removed"].append(x["removedSecurity"])
        slovarTickers[x["dateAdded"]]["removed"].append(x["symbol"])

    # added to index
    elif x["addedSecurity"] != '':

        if x["addedSecurity"] == "Howmet Aerospace Inc":
            x["addedSecurity"] = "Alcoa Corporation"
            x["symbol"] = "AA"
        """
        """
        slovarImen[x["dateAdded"]]["added"].append(x["addedSecurity"])
        slovarTickers[x["dateAdded"]]["added"].append(x["symbol"])

# print()
# print()

# print("Slovar imen")
for x in slovarImen:
    # print(x, ": ", slovarImen[x])

    if x == "October 8, 1998":
        slovarImen["March 17, 1997"]["added"].extend(slovarImen[x]["added"])
        slovarTickers["March 17, 1997"]["added"].extend(slovarTickers[x]["added"])
        slovarImen["March 17, 1997"]["removed"].extend(slovarImen[x]["removed"])
        slovarTickers["March 17, 1997"]["removed"].extend(slovarTickers[x]["removed"])

    if x == "April 8, 2004":
        slovarImen[x]["added"].append("AT&T Inc")
        slovarTickers[x]["added"].append("T")

    # print()

del slovarImen["October 8, 1998"]
del slovarTickers["October 8, 1998"]

# print()
# print(slovar["January 1, 1994"])
# print(len(slovar["January 1, 1994"]["added"]))
# print(type(companies.txt))
# print(slovar.keys())

# print()
# print()
obrnjenSlovarImen = res = dict(reversed(list(slovarImen.items())))
obrnjenSlovarTickers = res2 = dict(reversed(list(slovarTickers.items())))

"""""
print("Obrnjen slovarImen")
for x in obrnjenSlovarImen:
    print(x, ": ", obrnjenSlovarImen[x])
    print()

print("Konec obrnjenega imena")

print("Obrnjen slovarTickers")
for x in obrnjenSlovarTickers:
    print(x, ": ", obrnjenSlovarTickers[x])
    print()

print("Konec obrnjenega tickers")
"""""

keys = list(obrnjenSlovarImen)
keysTickers = list(obrnjenSlovarTickers)
# print(keys)
# print(keysTickers)

starting = set(obrnjenSlovarImen[keys[0]]["added"])
startingTickers = set(obrnjenSlovarTickers[keysTickers[0]]["added"])

"""""
print("Starting")
print(starting)
print(len(starting))
print(startingTickers)
print(len(startingTickers))
print()
"""""

# print("Glavni del imena")
for x in obrnjenSlovarImen:
    # odstranimo removed
    """""
    print("X: ", x)
    print("Starting lap: ", sorted(list(starting)))
    print("Starting len: ", len(starting))
    print()
    print("Removed ",set(obrnjenSlovarImen[x]["removed"]))
    print("Added  ",set(obrnjenSlovarImen[x]["added"]))
    print()
    """""

    tekociSet = (starting - set(obrnjenSlovarImen[x]["removed"])).union(set(obrnjenSlovarImen[x]["added"]))
    obrnjenSlovarImen[x]["all"] = sorted(list(tekociSet))
    """""
    print("Tekoci lap: ", sorted(list(tekociSet)))
    print("Tekoci len: ", len(tekociSet))
    print("Diff1: ", starting.difference(tekociSet))
    print("Diff2: ", tekociSet.difference(starting))
    """""

    starting = tekociSet

    # print(starting)  # print(len(starting))  # print()

# print("Glavni del imena")
for x in obrnjenSlovarTickers:
    # odstranimo removed
    """""
    print("X: ", x)
    print("Starting lap: ", sorted(list(startingTickers)))
    print("Starting len: ", len(startingTickers))
    print()
    print("Removed ",set(obrnjenSlovarTickers[x]["removed"]))
    print("Added  ",set(obrnjenSlovarTickers[x]["added"]))
    print()
    """""

    tekociSetTickers = (startingTickers - set(obrnjenSlovarTickers[x]["removed"])).union(set(obrnjenSlovarTickers[x]["added"]))
    obrnjenSlovarTickers[x]["all"] = sorted(list(tekociSetTickers))
    """""
    print("Tekoci lap: ", sorted(list(tekociSetTickers)))
    print("Tekoci len: ", len(tekociSetTickers))
    print("Diff1: ", startingTickers.difference(tekociSetTickers))
    print("Diff2: ", tekociSetTickers.difference(startingTickers))
    """""

    startingTickers = tekociSetTickers

    # print()

# print(obrnjenSlovarImen.keys())

del obrnjenSlovarImen["January 1, 1994"]
del obrnjenSlovarImen["March 17, 1997"]
del obrnjenSlovarImen["November 1, 1999"]

del obrnjenSlovarTickers["January 1, 1994"]
del obrnjenSlovarTickers["March 17, 1997"]
del obrnjenSlovarTickers["November 1, 1999"]

"""""
print()
print(obrnjenSlovarImen.keys())
print()

print("FINAL: ")

for x in obrnjenSlovarImen:

    # odstranimo removed
    print("X: ", x)
    print()
    print("Removed ",(obrnjenSlovarImen[x]["removed"]))
    print("Added  ",(obrnjenSlovarImen[x]["added"]))
    print("All ", (obrnjenSlovarImen[x]["all"]))
    print(len(obrnjenSlovarImen[x]["all"]))
    print()

print()
print("Tickerss")
print()

for x in obrnjenSlovarTickers:

    # odstranimo removed
    print("X: ", x)
    print()
    print("Removed ",(obrnjenSlovarTickers[x]["removed"]))
    print("Added  ",(obrnjenSlovarTickers[x]["added"]))
    print("All ", (obrnjenSlovarTickers[x]["all"]))
    print(len(obrnjenSlovarTickers[x]["all"]))
    print()
"""""

# changing keys of dictionary
# November 21, 2005 -> 2008, 11, 21
tickers = {"2005-11-21" if k == 'April 8, 2004' else k: v for k, v in obrnjenSlovarTickers.items()}
tickers = {"2008-02-19" if k == 'February 19, 2008' else k: v for k, v in tickers.items()}
tickers = {"2008-09-22" if k == 'September 22, 2008' else k: v for k, v in tickers.items()}
tickers = {"2009-06-08" if k == 'June 8, 2009' else k: v for k, v in tickers.items()}
tickers = {"2012-09-24" if k == 'September 24, 2012' else k: v for k, v in tickers.items()}
tickers = {"2013-09-23" if k == 'September 23, 2013' else k: v for k, v in tickers.items()}
tickers = {"2015-03-19" if k == 'March 19, 2015' else k: v for k, v in tickers.items()}
tickers = {"2017-09-01" if k == 'September 1, 2017' else k: v for k, v in tickers.items()}
tickers = {"2018-06-26" if k == 'June 26, 2018' else k: v for k, v in tickers.items()}
tickers = {"2019-04-02" if k == 'April 2, 2019' else k: v for k, v in tickers.items()}
tickers = {"2020-08-31" if k == 'August 31, 2020' else k: v for k, v in tickers.items()}

# tickers = {"1999-11-1" if k == 'November 1, 1999' else k:v for k,v in tickers.items()}


del tickers["2017-09-01"]  # zbrišem ker ima podjetje DD v removed in added tko da ni pomembno

names = {"November 21, 2005" if k == 'April 8, 2004' else k: v for k, v in obrnjenSlovarImen.items()}

"""""
print()
print("Tickerss2")
print()



for x in tickers:

    # odstranimo removed
    print("X: ", x)
    print()
    print("Removed ",(tickers[x]["removed"]))
    print("Added  ",(tickers[x]["added"]))
    print("All ", (tickers[x]["all"]))
    print(len(tickers[x]["all"]))
    print()



print()
for x in tickers:
    print(x, tickers[x])
    print()


print()
print("NAMES")
for x in names:
    print(x, names[x])
    print()
"""""


def allTickersEver():
    allTickers = []
    for season in endTickers:
        print("Sezona: ", season)
        print(endTickers[season])
        print(len(endTickers[season]["all"]))
        allTickers = allTickers + endTickers[season]["all"]
        print()

    allTickers = sorted(allTickers)
    allTickersEver = list(sorted(list(set(allTickers))))
    print("Vsi tickerji skozi obdobja: ", allTickersEver)
    print(len(allTickersEver))
    print()

    return allTickersEver


endTickers = tickers
allTickers = []
print('endTickers!: ', endTickers)

# pretvorimo slovar v DF in ga nato shranimo na disk kot .csv datoteko
df = pd.DataFrame(endTickers)
df.to_csv(f'D:\Faks\Algorithmic-Trading\dow_index_data\DowJonesCompaniesData.csv')

print('SEM V DOW JONES COMPANIES')
"""
for season in endTickers:

    print("Sezona: ", season)
    print(endTickers[season])
    print(len(endTickers[season]["all"]))
    allTickers = allTickers + endTickers[season]["all"]
    print()

allTickersEver()
"""
"""
allTickers = sorted(allTickers)
allTickersEver = set(allTickers)
print(sorted(allTickersEver))
print(len(allTickersEver))
print()
print(sorted(allTickers))

for x in obrnjenSlovarImen:
    print(obrnjenSlovarImen[x])
    print(len(obrnjenSlovarImen[x]["all"]))
    print()

"""""
