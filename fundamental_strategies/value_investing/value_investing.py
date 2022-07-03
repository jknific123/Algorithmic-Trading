import math
import pandas as pd
import datetime as datetime
import numpy as np

from functools import cache

from utility import utils as util
from stock_fundamental_data import fundamental_indicators as fundamentals

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30

million = 1000000
hundred_million = 100 * million


# vrne naslednji delovni datum ce trenutni datum ni delovni dan, uazme date time in vrne datum v string formatu
@cache
def to_week_day(date):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    if date.isoweekday() in {6, 7}:
        date += datetime.timedelta(days=-date.isoweekday() + 8)
    return date.strftime("%Y-%m-%d")


def pogojBuy(datum, currCompany_data, avgData):

    # ROE > avg(5 let), D/E < 2, P/B < 1, profitMargin nad 10% in narascajoc trend, age > 10, goodwill > avg, revenue > avg, DCF > cena
    print("SEM v pogojBuy")
    print(currCompany_data)
    print()
    print(avgData)
    print()

    flag = True
    leto = datetime.datetime.strptime(datum, "%Y-%m-%d").year
    print("leto",leto)
    print("datum", datum)
    if currCompany_data[datum]["ROE"] < avgData[str(leto)]["avgROE"]:
        flag = False
        print("ROE false")
        #None
    if currCompany_data[datum]["D/E"] > 2:
        flag = False
        print("D/E false")
    if currCompany_data[datum]["P/B"] > 2:
        flag = False
        print("P/B false")
        #None
    if currCompany_data[datum]["profitMargin"] < 0.1:
        flag = False
        print("profitMargin false")
    if currCompany_data[datum]["company_age"] < 10:
        flag = False
        print("company_age false")
    if currCompany_data[datum]["goodwill"] < avgData[str(leto)]["avgGoodwill"]:
        #flag = False
        #print("goodwill false")
        None
    if currCompany_data[datum]["revenue"] < avgData[str(leto)]["avgRevenue"]:
        #flag = False
        #print("revenue false")
        None
    if currCompany_data[datum]["dcf"] < currCompany_data[datum]["price"]:
        flag = False
        print("dcf false")

    if flag == True:
        print("ALLL TRUEEE BUYYY")

    return flag

def pogojSell(datum, currCompany_data, avgData):


    flag = True
    leto = datetime.datetime.strptime(datum, "%Y-%m-%d").year

    if currCompany_data[datum]["ROE"] > avgData[str(leto)]["avgROE"]:
        flag = False
    if currCompany_data[datum]["D/E"] < 2:
        flag = False
    if currCompany_data[datum]["P/B"] < 2:
        flag = False
    if currCompany_data[datum]["profitMargin"] > 0.1:
        flag = False
    #if currCompany_data[datum]["company_age"] < 10:
     #   flag = False
    if currCompany_data[datum]["goodwill"] > avgData[str(leto)]["avgGoodwill"]:
        #flag = False
        None
    if currCompany_data[datum]["revenue"] > avgData[str(leto)]["avgRevenue"]:
        #flag = False
        None
    if currCompany_data[datum]["dcf"] > currCompany_data[datum]["price"]:
        flag = False

    return flag


def value_investing_strategy(start_date, end_date, df, ticker, starting_index, status, odZacetkaAliNe, fundamental_data, avg_fundamentals):

    company_data = fundamentals.getDataCompany(ticker, start_date, end_date, fundamental_data, True)
    # print("Printam fundamentals na zacetku strategije")
    # fundamentals.printData(company_data)

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

        # pridobim trenutni datum, datum lanskega reporta in list vseh datumov
        trenutni_datum = df.index[x]  # prej: .strftime("%Y-%m-%d")
        prvi_datum_v_company_data = list(company_data.keys())[0]
        vsi_datumi = list(company_data.keys())
        vsi_datumi.remove(prvi_datum_v_company_data)  # da ga ne gledam 2x

        if x == 0:
            print("JE NA PRVEM MESTU")
            df["ROE"] = company_data[prvi_datum_v_company_data]["ROE"]
            df["D/E ratio"] = company_data[prvi_datum_v_company_data]["D/E"]
            df["P/B ratio"] = company_data[prvi_datum_v_company_data]["P/B"]
            df["ProfitMargin"] = company_data[prvi_datum_v_company_data]["profitMargin"]
            df["Age"] = company_data[prvi_datum_v_company_data]["company_age"]
            df["Goodwill"] = company_data[prvi_datum_v_company_data]["goodwill"]
            df["Revenue"] = company_data[prvi_datum_v_company_data]["revenue"]
            df["DCF"] = company_data[prvi_datum_v_company_data]["dcf"]

        if trenutni_datum in vsi_datumi:
            print("JE V SLOVAR KEYS")
            df["ROE"] = company_data[trenutni_datum]["ROE"]
            df["D/E ratio"] = company_data[trenutni_datum]["D/E"]
            df["P/B ratio"] = company_data[trenutni_datum]["P/B"]
            df["ProfitMargin"] = company_data[trenutni_datum]["profitMargin"]
            df["Age"] = company_data[trenutni_datum]["company_age"]
            df["Goodwill"] = company_data[trenutni_datum]["goodwill"]
            df["Revenue"] = company_data[trenutni_datum]["revenue"]
            df["DCF"] = company_data[trenutni_datum]["dcf"]


        # P/E < 15, P/B < 2, ROE > 15%, market cap > 100M$ -> BUY signal
        if (trenutni_datum in vsi_datumi and pogojBuy(trenutni_datum, company_data, avg_fundamentals)) or (x == 0 and pogojBuy(prvi_datum_v_company_data, company_data, avg_fundamentals)):
            print("SEM V BUY")
            print("datum: ", trenutni_datum)

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

        # P/E > 15, P/B > 2, ROE < 15%, market cap < 100M$ -> Sell signal
        #elif (trenutni_datum in slovar_keys and slovar_pb[trenutni_datum] > 1) or (x == 0 and slovar_pb[prvi_datum_v_slovar_pb] > 1): marketCapitalization
        elif (trenutni_datum in vsi_datumi and pogojSell(trenutni_datum, company_data, avg_fundamentals)) or (x == 0 and pogojSell(prvi_datum_v_company_data, company_data, avg_fundamentals)):
            print("SEM V SELL")

            if check != 1 and check != 0:  # zadnji signal ni bil sell in nismo na zacetku
                print("SEM V SELL IN BOM PORODAL", trenutni_datum)
                # TODO dodaj še davek na dobiček 27,5% -> done

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
