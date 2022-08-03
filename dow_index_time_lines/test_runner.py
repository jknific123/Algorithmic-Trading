import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
import get_time_lines as time_lines_db
import create_signals_on_time_lines as tradingSignals
from simulate_trading_portfolio import backtestPortfolio


def simulateTradingOnPortfolio(portfolio):
    rez = backtestPortfolio(portfolio=portfolio)


"""
 Od tukaj naprej se izvaja testiranje:
"""

# holdObdobje = 1
list_hold_obdobja = [1, 7, 31, 365]
begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
TimeLinesDB = time_lines_db.TimeLinesData()

trading_signals_lines = tradingSignals.getTradingSignalsForAllTimeLines(time_lines=TimeLinesDB.time_lines, shortSma=20, longSma=50, holdObdobje=1)
portfolio_dict = tradingSignals.createDictPortfolioFromDF(trading_signals_lines)

simulateTradingOnPortfolio(portfolio=portfolio_dict)

print('KONEC!!! ', datetime.datetime.now() - begin_time)