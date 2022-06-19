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

    return df