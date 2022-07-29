import datetime as datetime

import numpy as np

from buy_and_hold_backtester import zacetniDf, backtest
from buy_and_hold_strategy import buy_and_hold
# from dow_index_data import dow_jones_companies as dow
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from buy_and_hold_grafi import SMA_trading_graph, profit_graph
from utility import utils as util


def zacetniDf(data):
    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako
    # kreiramo nova stolpca za buy/sell signale
    data['Buy'] = np.nan
    data['Sell'] = np.nan
    data['Cash'] = 0.0
    data['Shares'] = 0.0
    data['Profit'] = 0.0
    data['Total'] = 0.0
    data['Ticker'] = ""
    data['Buy-Signal'] = np.nan
    data['Sell-Signal'] = np.nan
    data["Buy-date"] = ""
    data["Sell-date"] = ""

    return data


def trejdajNaCelotnemIndexu(short_sma, long_sma, stockPricesDBIndex):
    index_ticker = "^DJI"
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-11-21", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(test_data, index_ticker, 0, 0, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, round(return_df["Total"].iloc[-1], 2))

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], util.vsaLeta())
    print('Koncno stanje: ', return_df["Total"].iloc[-1])
    print(cagr, '%')


def trejdajNaCelotnemIndexuTestna(short_sma, long_sma, stockPricesDBIndex):
    index_ticker = "^DJI"
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2017-02-02", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(test_data, index_ticker, 0, 0, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, round(return_df["Total"].iloc[-1], 2))

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], util.testnaMnozicaLeta())
    print('Koncno stanje: ', return_df["Total"].iloc[-1])
    print(cagr, '%')


def trejdajNaCelotnemIndexuTestna20procentov(short_sma, long_sma, stockPricesDBIndex):
    index_ticker = "^DJI"
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2018-09-09", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(test_data, index_ticker, 0, 0, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, round(return_df["Total"].iloc[-1], 2))

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], util.testnaMnozicaLeta20procentov())
    print('Koncno stanje: ', return_df["Total"].iloc[-1])
    print(cagr, '%')


def trejdajNaCelotnemIndexuTestna10procentov(short_sma, long_sma, stockPricesDBIndex):
    index_ticker = "^DJI"
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2020-04-16", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(test_data, index_ticker, 0, 0, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, round(return_df["Total"].iloc[-1], 2))

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], util.testnaMnozicaLeta10procentov())
    print('Koncno stanje: ', return_df["Total"].iloc[-1])
    print(cagr, '%')


def trejdajNaCelotnemIndexuZadnjeLeto(short_sma, long_sma, stockPricesDBIndex):
    index_ticker = "^DJI"
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2020-11-21", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(test_data, index_ticker, 0, 0, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, round(return_df["Total"].iloc[-1], 2))

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], 1)
    print('Koncno stanje: ', return_df["Total"].iloc[-1])
    print(cagr, '%')


"""
 Od tukaj naprej se izvaja testiranje Buy and hold strategije:
"""

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('bu and hold strategy po klicu inicializacije objekta')

# trejdajNaCelotnemIndexu(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB)

# trejdajNaCelotnemIndexuTestna(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB)

# trejdajNaCelotnemIndexuTestna20procentov(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB)

# trejdajNaCelotnemIndexuTestna10procentov(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB)

# trejdajNaCelotnemIndexuZadnjeLeto(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
