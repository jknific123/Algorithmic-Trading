import datetime as datetime
from buy_and_hold_backtester import zacetniDf, backtest
from buy_and_hold_strategy import buy_and_hold
# from dow_index_data import dow_jones_companies as dow
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from buy_and_hold_grafi import SMA_trading_graph, profit_graph
from utility import utils as util


# probal primerjat moje backteste s trejdanjem na DOW indexu...
def trejdajNaCelotnemIndexu(short_sma, long_sma, stockPricesDBIndex, hold_obdobje):
    index_ticker = "^DJI"
    # testiram od 2017-02-02 do 2021-11-21, za start date dam: '2015-09-02' za max sma na testni mnozci
    # test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2017-02-02", companyTicker=index_ticker)
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = buy_and_hold(short_sma, long_sma, test_data, index_ticker, 0, 0, True, hold_obdobje, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, return_df["Total"].iloc[-1])

    cagr = util.povprecnaLetnaObrestnaMera(30000, return_df["Total"].iloc[-1], 16)
    print(cagr, '%')


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, hold_obdobje_kombinacija_portfolio):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje_kombinacija_portfolio)

    print('Total profit: ', tmp['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje Buy and hold strategije:
"""

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('bu and hold strategy po klicu inicializacije objekta')

testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", short_sma=10, long_sma=100, dowTickers=dowJonesIndexData,
                                  stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=1)

# trejdajNaCelotnemIndexu(short_sma=1, long_sma=1, stockPricesDBIndex=stockPricesDB, hold_obdobje=1)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
