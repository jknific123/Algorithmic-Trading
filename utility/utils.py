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




# idx = pd.Index(['Labrador', 'Beagle', 'Labrador', 'Lhasa', 'Husky', 'Beagle'])
#
# print(idx)
#
# print(idx.duplicated(keep='first'))


# range1 = pd.date_range('2021-10-01','2021-10-6')
# range2 = pd.date_range('2021-10-6','2021-10-11')

# range1 = ["2021-10-01", "2021-10-02", "2021-10-03", "2021-10-04"]
# range2 = ["2021-10-01", "2021-10-02", "2021-10-03", "2021-10-04", "2021-10-04"]
#
#
# df1 = pd.DataFrame(np.random.rand(len(range1), 1), columns=['value'], index=range1)
# df2 = pd.DataFrame(np.random.rand(len(range2), 1), columns=['value'], index=range2)
#
# print(df1)
# print(df2)
#
# df3 = df1['value'] + df2['value']
#
# print('df3')
# print(df3)
