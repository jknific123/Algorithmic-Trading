import datetime as datetime
from matplotlib import pyplot as plt
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
import get_time_lines as time_lines_db
import create_fundamental_signals_on_lines as fundamentalTradingSignals
from simulate_trading_portfolio import backtestPortfolio
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators


def simulateTradingOnPortfolio(start, portfolio, trading_dates, index_col, stock_prices_db, trgovalna_strategija):
    rez = backtestPortfolio(startDate=start, portfolio=portfolio, trading_dates=trading_dates,
                            index_column=index_col, stockPricesDB=stock_prices_db, trgovalna_strategija=trgovalna_strategija)
    profit_graph(rez, 1, 'Portfelj', round(rez['Total'].to_numpy()[-1], 2))


def profit_graph(df, mode, company, cash):
    # prikaz grafa sredstev
    # mode = 0 -> prikaz podjetja
    # mode = 1 -> prikaz portfelja

    fig = plt.figure(figsize=(8, 6), dpi=200)
    if mode == 0:
        fig.suptitle(f'Končna vrednost podjetja {company}: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
        df['Total'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)
    elif mode == 1:
        fig.suptitle(f'Končna vrednost portfelja: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost portfelja v $')
        df['Total'].plot(ax=ax1, label="Vrednost portfelja", color='black', alpha=0.5)

    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


"""
 Od tukaj naprej se izvaja testiranje:
"""

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
TimeLinesDB = time_lines_db.TimeLinesData()
fundamentalIndicatorsDB = getFundamentalIndicators.StockFundamentalData()

trading_signals_lines, index_column = fundamentalTradingSignals.getTradingSignalsForAllTimeLines(time_lines=TimeLinesDB.time_lines,
                                                                                                 trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
                                                                                                 fDB=fundamentalIndicatorsDB)

portfolio_dict = fundamentalTradingSignals.createDictPortfolioFromDF(trading_signals_lines)

simulateTradingOnPortfolio(start='2017-02-02', portfolio=portfolio_dict, trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
                           index_col=index_column, stock_prices_db=stockPricesDB, trgovalna_strategija='P/E')

print('KONEC!!! ', datetime.datetime.now() - begin_time)
