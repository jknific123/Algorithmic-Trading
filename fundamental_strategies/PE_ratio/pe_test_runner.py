import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from fundamental_strategies.PE_ratio import create_PE_trading_signals_on_lines as fundamentalTradingSignals
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators
from dow_index_time_lines import get_time_lines as time_lines_db
from dow_index_time_lines.simulate_trading_portfolio import backtestPortfolio
from fundamental_strategies.PE_ratio.pe_ratio_grafi import profit_graph
from utility import utils as util


def simulateTradingOnPortfolio(start, portfolio, trading_dates, index_col, stock_prices_db, trgovalna_strategija):
    totals, ostali_cash = backtestPortfolio(startDate=start, portfolio=portfolio, trading_dates=trading_dates, index_column=index_col, stockPricesDB=stock_prices_db,
                                            trgovalna_strategija=trgovalna_strategija)
    profit_graph(totals, 1, 'Portfelj', round(totals['Total'].to_numpy()[-1], 2))

    vlozeni_cash = (util.getMoney('') * 30) - ostali_cash
    pretekli_cas = datetime.datetime.strptime(totals.index[-1], '%Y-%m-%d') - datetime.datetime.strptime(totals.index[0], '%Y-%m-%d')
    koncni_znesek = totals['Total'].to_numpy()[-1]
    print()
    print('Rezultati P/E strategije: ')
    print('Ostala sredstva zaradi nakupa nominalnih delnic: ', round(ostali_cash, 2), '$')
    print('Dejanski začetni vložek: ', round(vlozeni_cash, 2), '$')
    print("Skupna končna sredstva portfelja: ", round(koncni_znesek, 2), "$")
    print("Povprecna letna obrestna mera glede na začetni vložek: ", util.povprecnaLetnaObrestnaMera(vlozeni_cash, koncni_znesek, (pretekli_cas.days / 365)), '%')


"""
 Od tukaj naprej se izvaja testiranje:
"""

begin_time = datetime.datetime.now()

dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
TimeLinesDB = time_lines_db.TimeLinesData()
fundamentalIndicatorsDB = getFundamentalIndicators.StockFundamentalData()

trading_signals_lines, index_column = fundamentalTradingSignals.getTradingSignalsForAllTimeLines(time_lines=TimeLinesDB.time_lines,
                                                                                                 trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
                                                                                                 fDB=fundamentalIndicatorsDB)

portfolio_dict = fundamentalTradingSignals.createDictPortfolioFromDF(trading_signals_lines)

# testna 30%
# simulateTradingOnPortfolio(start='2017-02-02', portfolio=portfolio_dict, trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
#                            index_col=index_column, stock_prices_db=stockPricesDB, trgovalna_strategija='P/E')

# testna 20%
# simulateTradingOnPortfolio(start='2018-09-09', portfolio=portfolio_dict, trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
#                            index_col=index_column, stock_prices_db=stockPricesDB, trgovalna_strategija='P/E')

# testna 10%
simulateTradingOnPortfolio(start='2020-04-16', portfolio=portfolio_dict, trading_dates=fundamentalIndicatorsDB.fundamental_trading_dates,
                           index_col=index_column, stock_prices_db=stockPricesDB, trgovalna_strategija='P/E')

print('KONEC!!! ', datetime.datetime.now() - begin_time)
