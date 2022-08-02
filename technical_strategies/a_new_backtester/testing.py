import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from utility import utils as util


from technical_strategies.a_new_backtester.backtester import backtest


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, dowTickers, stock_prices_db):
    tmp = backtest(start=start_date, end=end_date, dowTickers=dowTickers, stockPricesDB=stock_prices_db)

    # print('Total profit: ', tmp['totals']['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje:
"""

# holdObdobje = 1
list_hold_obdobja = [1, 7, 31, 365]
begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()


testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
