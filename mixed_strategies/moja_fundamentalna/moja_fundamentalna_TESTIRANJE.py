import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators
from mixed_strategies.moja_fundamentalna.moja_fundamentalna_backtester import backtest


def testirajNaPortfoliu(start_date, end_date, dowTickers, stock_prices_db, fundamental_indicators):
    backtest(start=start_date, end=end_date, dowTickers=dowTickers, stockPricesDB=stock_prices_db, fundamental_data=fundamental_indicators)


"""
 Od tukaj naprej se izvaja testiranje Mixed fundamentals investing strategije:
"""

begin_time = datetime.datetime.now()

dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
fundamentalIndicatorsDB = getFundamentalIndicators.StockFundamentalData()
print('mixed fundamentals strategy po klicu inicializacije objekta')

# ucna mnozica
testirajNaPortfoliu(start_date="2005-11-21", end_date="2016-06-20", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testna mnozica
# testirajNaPortfoliu(start_date="2016-06-20", end_date="2021-01-01", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamental_data)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
