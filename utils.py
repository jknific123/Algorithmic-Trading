import pandas_datareader.data as web
import pandas as pd
import datetime as datetime




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

def pogojBuy(datum, currCompany_data, avgData):

    # ROE > avg(5 let), D/E < 2, P/B < 1, profitMargin nad 10% in narascajoc trend, age > 10, goodwill > avg, revenue > avg, DCF > cena

    print(avgData)

    flag = True
    leto = datetime.datetime.strptime(datum, "%Y-%m-%d").year
    print("leto",leto)
    print("datum", datum)
    if currCompany_data[datum]["ROE"] < avgData[str(leto)]["avgROE"]:
        flag = False
    if currCompany_data[datum]["D/E"] > 2:
        flag = False
    if currCompany_data[datum]["P/B"] > 1:
        flag = False
    if currCompany_data[datum]["profitMargin"] < 0.1:
        flag = False
    if currCompany_data[datum]["company_age"] < 10:
        flag = False
    if currCompany_data[datum]["goodwill"] < avgData[str(leto)]["avgGoodwill"]:
        flag = False
    if currCompany_data[datum]["revenue"] < avgData[str(leto)]["avgRevenue"]:
        flag = False
    if currCompany_data[datum]["dcf"] < currCompany_data[datum]["price"]:
        flag = False

    return flag


"""
date = "2005-11-21"

companyData = {}
companyData["2005-11-21"] = {}
companyData["2005-11-21"]["ROE"] = 0.5
companyData["2005-11-21"]["D/E"] = 1
companyData["2005-11-21"]["P/B"] = 0.5
companyData["2005-11-21"]["profitMargin"] = 0.5
companyData["2005-11-21"]["company_age"] = 15
companyData["2005-11-21"]["goodwill"] = 1000
companyData["2005-11-21"]["revenue"] = 1000
companyData["2005-11-21"]["dcf"] = 64
companyData["2005-11-21"]["price"] = 60

avg = {}
avg["2005"] = {}
avg["2005"]["avgROE"] = 0.3
avg["2005"]["avgGoodwill"] = 500
avg["2005"]["avgRevenue"] = 500

print(pogojBuy(date, companyData, avg))
"""