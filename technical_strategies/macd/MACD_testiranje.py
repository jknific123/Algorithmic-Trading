import datetime as datetime

from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.macd.macd import macd
from technical_strategies.macd.macd_backtester import zacetniDf, backtest


# probal primerjat moje backteste s trejdanjem na DOW indexu...
def trejdajNaEnemPodjetju(hold_obdobje):
    test_ticker = "^DJI"
    test_data = stockPricesDB.getCompanyStockDataInRange(date_from="2016-05-21", date_to="2020-01-01", companyTicker=test_ticker)
    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = macd(12, 26, 9, test_data, test_ticker, 0, 0, True, hold_obdobje)


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    ema1_vrednosti = [10, 12, 15, 18, 20]
    ema2_vrednosti = [20, 24, 30, 35, 40]
    signal_vrednosti = [3, 6, 9]

    for ema1 in ema1_vrednosti:
        # print("Trenutna Long vrednost: ", long)

        for ema2 in ema2_vrednosti:

            for signal in signal_vrednosti:

                if ema1 != ema2:
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = {}
                    print(f"Kombinacija: Ema1 = {ema1} , Ema2 = {ema2} , Signal = {signal}")
                    # print debug
                    # print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
                    temp = backtest(start_period, end_period, ema1, ema2, signal, dowTickers, stock_data, hold_obdobje)

                    # print("Data: ", temp)
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = temp
                    # print("Trenutna Short vrednost: ", short)
                    print()
                counter += 1

    print("Counter: ", counter)

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_prices_db, hold_obdobje):
    rez_ucni = najdiOptimalneParametreNaPotrfoliu("2005-11-21", "2016-05-21", dowTickers, stock_prices_db, hold_obdobje)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        # print debug
        print("Kombinacija : ", x)
        # print("Before in rez_total_ucni: ", rez_total_ucni[x])
        # print("Before in rez_total_ucni type: ", type(rez_total_ucni[x]))
        # print("Before in rez_ucni[x][Total].iat[-1]: ", rez_total_ucni[x])
        # print("Before in rez_ucni[x][Total].iat[-1] type: ", type(rez_total_ucni[x]))
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        # print("After: ", rez_total_ucni[x])
        print()

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, signal_line, dowTickers, stock_prices_db, hold_obdobje):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, signal_period=signal_line, dowTickers=dowTickers,
                   stockPricesDB=stock_prices_db, hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje MACD strategije:
"""

# MACD crossover strategy
# datetmie = leto, mesec, dan
# short_period = 12 # 12 #20
# long_period = 26 #26 #40
# signal_period = 9#9

holdObdobje = 1

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('MACD strategy po klicu inicializacije objekta')

# testirajNaEnemPodjetju(hold_obdobje=holdObdobje)
# testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2016-05-21", short_sma=12, long_sma=26, signal_line=9, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica
testirajNaPortfoliuEnoKombinacijo(start_date="2016-05-21", end_date="2021-01-01", short_sma=20, long_sma=40, signal_line=9, dowTickers=dowJonesIndexData,
                                  stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
