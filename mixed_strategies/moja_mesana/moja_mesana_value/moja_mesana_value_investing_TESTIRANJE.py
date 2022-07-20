import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators
from mixed_strategies.moja_mesana.moja_mesana_value.moja_mesana_value_investing_backtester import backtest


def testirajNaPortfoliu(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, fundamental_indicators):
    backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers,
             stockPricesDB=stock_prices_db, fundamental_data=fundamental_indicators)


"""
 Od tukaj naprej se izvaja testiranje Value investing + SMA crossover strategije:
"""

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
fundamentalIndicatorsDB = getFundamentalIndicators.StockFundamentalData()
print('value investing strategy po klicu inicializacije objekta')
# fundamental_data = fundamentals.getAllFundamentals(fundamentals.vsi_tickerji)

# ucna mnozica
testirajNaPortfoliu(start_date="2005-11-21", end_date="2017-02-02", short_sma=85, long_sma=200,
                    dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# testna mnozica
testirajNaPortfoliu(start_date="2017-02-02", end_date="2021-11-21",  short_sma=85, long_sma=200,
                    dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)

# tesiraj na vseh podatkih
# testirajNaPortfoliu(start_date="2005-11-21", end_date="2021-11-21",  short_sma=85, long_sma=200,
#                     dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators=fundamentalIndicatorsDB)


print('KONEC!!! ', datetime.datetime.now() - begin_time)
