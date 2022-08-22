import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators
from mixed_strategies.moja_fundamentalna.old_version.moja_fundamentalna_backtester import backtest


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
# testirajNaPortfoliu(start_date="2005-11-21", end_date="2017-02-02", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testna mnozica 30%
testirajNaPortfoliu(start_date="2017-02-02", end_date="2021-11-21", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testna mnozica 20%
# testirajNaPortfoliu(start_date="2018-09-09", end_date="2021-11-21", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testna mnozica 10%
# testirajNaPortfoliu(start_date="2020-04-16", end_date="2021-11-21", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testiraj na celotnih podatkih
# testirajNaPortfoliu(start_date="2005-11-21", end_date="2021-11-21", dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)


print('KONEC!!! ', datetime.datetime.now() - begin_time)
