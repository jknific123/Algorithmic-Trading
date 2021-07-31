import math

import pandas_datareader.data as web
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import utils as util


# portfolio = {'AAPL': {'funds': 0, 'shares': 0, 'invested': 0}}
# print(portfolio)
# print(portfolio.keys())
# print(portfolio.values())
# print(portfolio['AAPL'])
# print(portfolio['AAPL']['funds'])
# -----rez-------------
# {'AAPL': {'funds': 0}}
# dict_keys(['AAPL'])
# dict_values([{'funds': 0}])
# {'funds': 0}
# 0
#

def sma_crossover(sPeriod, lPeriod, df, company):
    # naredimo nova stolpca za oba SMA
    df[f'SMA-{sPeriod}'] = df['Adj Close'].rolling(window=sPeriod, min_periods=1, center=False).mean()
    df[f'SMA-{lPeriod}'] = df['Adj Close'].rolling(window=lPeriod, min_periods=1, center=False).mean()

    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako kreiramo nova stolpca
    # za buy/sell signale
    df['Buy'] = np.nan
    df['Sell'] = np.nan
    df['Cash'] = 0
    df['Shares'] = 0
    df['Total'] = 0

    df = df[lPeriod:]

    # check -> zato da nimamo dveh zapovrstnih buy/sell signalov: 2 = buy, 1 = sell
    check = 0
    for x in range(len(df)):

        # filing shares, cash, total
        if (x - 1) >= 0:  # preverimo ce smo znotraj tabele
            df['Shares'].iloc[x] = np.nan_to_num(df['Shares'].iloc[x - 1])  # prenesemo prejsnje st delnic naprej
            df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x - 1])  # prenesemo prejsnji Cash naprej
            df['Total'].iloc[x] = np.nan_to_num(df['Total'].iloc[x]) + (
                    df['Cash'].iloc[x] + df['Shares'].iloc[x] * df['Adj Close'].iloc[x])  # izracunamo total

        else:  # zacetek tabele -> inicializacija vrednosti
            df['Shares'].iloc[x] = np.nan_to_num(df['Shares'].iloc[x])
            df['Cash'].iloc[x] = util.getMoney()
            df['Total'].iloc[x] = np.nan_to_num(df['Total'].iloc[x]) + (
                    df['Cash'].iloc[x] + (df['Shares'].iloc[x] * df['Adj Close'].iloc[x]))

        # sSMA > lSMA -> buy signal
        if df[f'SMA-{sPeriod}'].iloc[x] > df[f'SMA-{lPeriod}'].iloc[x]:

            if check != 2:
                df['Buy'].iloc[x] = df['Adj Close'].iloc[x]
                # money = portfolio['AAPL'][] # TODO -> buy shares, get change, count in fees, get profit itd

                # kupi kolikor je možno delnic glede na cash -> drugi del je cena delnice + fee na nakup delnice
                stDelnic = math.floor(df['Cash'].iloc[x] / (df['Adj Close'].iloc[x] + util.percentageFee(1, df['Adj Close'].iloc[x])))

                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x]) - (
                        stDelnic * df['Adj Close'].iloc[x])  # posodbi cash
                df['Shares'].iloc[x] = df['Shares'].iloc[x] + stDelnic

                check = 2

        # sSMA < lSMA -> sell signal
        elif df[f'SMA-{sPeriod}'].iloc[x] < df[f'SMA-{lPeriod}'].iloc[x]:

            if check != 1 and check != 0:
                df['Sell'].iloc[x] = df['Adj Close'].iloc[x]

                # prodaj vse delnic
                prodano = (df['Shares'].iloc[x] * df['Adj Close'].iloc[x])  # delnice v denar TODO -> include fees
                prodanoFees = util.fees(prodano)  # ostanek denarja po fees
                df['Cash'].iloc[x] = np.nan_to_num(df['Cash'].iloc[x]) + prodanoFees  # posodbi cash
                df['Shares'].iloc[x] = 0

                check = 1

    print(df)
    # plotShares(df, company)
    SMA_trading_graph(sPeriod, lPeriod, df, company)
    profit_graph(df, 0, company)


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    # print(df)
    # newDf = df[['Adj Close', 'Buy', 'Sell', 'Cash', 'Shares', 'Total']].copy()
    # print(newDf)
    return df


def SMA_trading_graph(sPeriod, lPeriod, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    # cena
    df['Adj Close'].plot(ax=ax1, color='black', alpha=0.5)

    # kratki in dolgi SMA
    df[[f'SMA-{sPeriod}', f'SMA-{lPeriod}']].plot(ax=ax1, linestyle="--")

    # buy/sell signali
    ax1.plot(df['Buy'], '^', markersize=6, color='green', label='Buy signal', lw=2)
    ax1.plot(df['Sell'], 'v', markersize=6, color='red', label='Sell signal', lw=2)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def profit_graph(df, mode, company):
    # prikaz grafa sredstev
    # mode = 0 -> prikaz podjetja
    # mode = 1 -> prikaz portfolia

    fig = plt.figure(figsize=(8, 6), dpi=200)
    if (mode == 0):
        fig.suptitle(company)
        ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
        df['Total'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)
    elif (mode == 1):
        fig.suptitle(f'Končna vrednost portfolia: {company}')
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


# SMA crossover strategy

# pridobimo podatke preko apija
aapl = web.DataReader('AAPL', 'yahoo', start='2006, 10, 1', end='2012, 1, 1')

# tickers = ['AAPL', 'MSFT', 'IBM', 'GOOG']
# all_data = util.get(tickers, dt.datetime(2006, 10, 1), dt.datetime(2012, 1, 1))

# print(all_data)

short_period = 40
long_period = 100

new = aapl[['Adj Close']].copy()

portfolio = pd.DataFrame(index=np.arange(30), columns=["numShares", "currCash", "curHoldings"])

# Dow Jones Index podjetja not 20 let 1999 - 2020
tickers = ['HD', 'INTC']
# , 'AAPL', 'IBM', 'AXP', 'BA', 'CAT', 'KO', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'MMM', 'PG', 'WMT', 'DIS']

# print(portfolio)

# tuki potem for za usa podjetja iz dow jones indexa

allFunds = pd.DataFrame
allShares = {}

for i in range(len(tickers)):
    data = web.DataReader(tickers[i], 'yahoo', start='2000, 1, 1', end='2020, 1, 1')
    totals = sma_crossover(short_period, long_period, data, tickers[i])

    allShares[tickers[i]] = totals['Shares'].iloc[-1]
    if (i == 0):
        allFunds = totals[['Total']].copy()
    else:
        allFunds['Total'] = allFunds['Total'] + totals['Total']

print(allFunds)
profit_graph(allFunds, 1, round(allFunds['Total'].iloc[-1], 4))

print("Skupna sredstva portfolia: ", round(allFunds['Total'].iloc[-1], 4), "$")
print("Profit: ", round(allFunds['Total'].iloc[-1] - (len(tickers) * util.getMoney()), 4), "$")

print("Delnice, ki jih še imamo v portfoliu:")
for key, value in allShares.items():
    print(key, " : ", value)
