import pandas_datareader.data as web
import pandas as pd




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


def percentageFee(percent, whole):
    return (percent * whole) / 100.0


# return money after fee
def fees(money):

    feeMoney = percentageFee(feePercentage, money)

    return money - feeMoney


# return money after tax
def taxes(profit, percentage):
    None


def profit():
    None


def getMoney():
    startMoney = 1000

    return startMoney


def portfolio():
    None

