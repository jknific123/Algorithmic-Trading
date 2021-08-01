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

# vrednost davka na dobiček
taxRate = 27.5


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


def getMoney():
    startMoney = 1000

    return startMoney


def portfolio():
    None

