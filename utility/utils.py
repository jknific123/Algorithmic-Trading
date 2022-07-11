import pandas_datareader.data as web
import pandas as pd
import datetime as datetime
import numpy as np


def get(tickers, startdate, enddate):
    def data(ticker):
        return web.DataReader(ticker, 'yahoo', start=startdate, end=enddate)

    datas = map(data, tickers)

    return pd.concat(datas, keys=tickers, names=['Ticker', 'Date'])


# TODO taxes, prihodki, comission na buy in sell order, starting money, portfolio

# fee values from  0 - 2 %
# 0 -> 0%
# 1 -> 0,5%
# 2 -> 1%
feePercentage = 1

# vrednost davka na dobiček
taxRate = 25


def percentageFee(percent, whole):
    return (percent * whole) / 100.0


# return money after fee
def fees(money):
    feeMoney = percentageFee(feePercentage, money)

    return money - feeMoney


# return amount of money to be paid for taxes
def taxes(money):
    taxMoney = percentageFee(taxRate, money)

    return taxMoney


# returns profit
def profit(buyPrice, sellPrice):
    return sellPrice - buyPrice


def getMoney(company_ticker):
    if company_ticker != '^DJI':
        startMoney = 1000
        return startMoney
    elif company_ticker == '^DJI':
        startMoney = 30000
        return startMoney


def preveriPravilnostDatumov(ticker, portfolio):

    tickerTotals = portfolio[ticker]

    tmpIndexCheck = portfolio[ticker][['Total']]
    print("Podjetje: ", ticker, " velikost DF: ", len(portfolio[ticker].index), " ima unique index: ", tickerTotals.index.is_unique)
    print("duplikati: ", tmpIndexCheck.index.duplicated())
    tickerTotals = tickerTotals.loc[~tickerTotals.index.duplicated(), :]
    print("Popravljeno podjetje: ", ticker, " velikost DF: ", len(tickerTotals), " ima unique index: ", tickerTotals.index.is_unique)

    for z in range(0, len(tickerTotals)):
        if z != 0:
            prejsnji_datum = datetime.datetime.strptime(tickerTotals.index[z - 1], "%Y-%m-%d").date()
            trenutni_datum = datetime.datetime.strptime(tickerTotals.index[z], "%Y-%m-%d").date()
            if prejsnji_datum > trenutni_datum:
                print("Napaka v zaporedju datumov!!")
                print("Podjetje: ", ticker)
                print("prejsnji_datum: ", prejsnji_datum)
                print("trenutni_datum: ", trenutni_datum)


def getStringForHoldObdobje(hold_obdobje):
    if hold_obdobje == 1:
        return 'dnevni'
    elif hold_obdobje == 7:
        return 'tedenski'
    elif hold_obdobje == 31:
        return 'mesecni'
    elif hold_obdobje == 365:
        return 'letni'


def poisciIndexZaRezanjeDf(df):
    # poiscem index zacetnega datuma 2005-11-21
    # for i in range(len(df)):
    #     if df.index[i] == '2005-11-21':
    #         print('nasel index za 2005-11-21: ', i)
    #         return i
    # print('NAPAKA nisem nasel indexa za 2005-11-21, vracam long_sma_period')
    return 200  # ker vemo da je 200 dni viska na zacetku za najdaljsi long sma

