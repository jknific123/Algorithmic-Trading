import math
import pandas_datareader.data as web
import pandas as pd
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt

import utils as util
import dow_jones_companies as dow
import yfinance as yf


vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS',  'GE', #'GM',
                'GS', 'HD', 'HON', 'HPQ', "AA", 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',    #'HWM' -> "AA"
                'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']


def getAllStockData(start_date, end_date):

    data = {}
    count = 0
    for x in vsi_tickerji:

        if x == "DOW":
            temp_start_date = '2019-03-20'
            temp_data = yf.download(x, start=temp_start_date, end=end_date, progress=False)  # downloadam podatke za doticno podjetje in jih shranim v slovar
        else:
            temp_data = yf.download(x, start=start_date, end=end_date, progress=False) # downloadam podatke za doticno podjetje in jih shranim v slovar,

        temp_data = temp_data[["High", "Low", "Close", "Adj Close"]].copy() # da vzamemo samo ceno
        data[x] = temp_data

        count += 1
        print(f"DOWNLOADED stock data for {x}. {count}/{len(vsi_tickerji)}")

    return data

def getCompanyStockDataInRange(date_from, date_to, companyTicker, allStockData):

    return_dataframe = pd.DataFrame
    return_dataframe = allStockData[companyTicker].loc[date_from:date_to]

    return return_dataframe

"""
test_ticker = "HD"
test_data_ucna = yf.download(test_ticker, start="2005-11-21", end="2021-1-1", progress=False)
test_data_ucna = test_data_ucna[['Adj Close']].copy()

skrajsan = getCompanyStockDataInRange("2016-5-21", "2020-1-1", test_ticker, test_data_ucna)

skrajsan_yfinance = yf.download(test_ticker, start="2016-5-21", end="2020-1-1", progress=False)
skrajsan_yfinance = skrajsan_yfinance[['Adj Close']].copy()

print("finito")
"""
