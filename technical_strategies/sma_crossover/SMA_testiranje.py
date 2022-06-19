import datetime as datetime

from technical_strategies.sma_crossover.sma_backtester import zacetniDf, backtest
from technical_strategies.sma_crossover.sma_crossover_nov import sma_crossover
# from dow_index_data import dow_jones_companies as dow
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.sma_crossover.sma_grafi import SMA_trading_graph, profit_graph


# probal primerjat moje backteste s trejdanjem na DOW indexu...
def trejdajNaEnemPodjetju(hold_obdobje):
    test_ticker = "^DJI"
    test_data = stockPricesDB.getCompanyStockDataInRange(date_from="2016-05-21", date_to="2020-01-01", companyTicker=test_ticker)
    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = sma_crossover(40, 100, test_data, test_ticker, 0, 0, True, hold_obdobje)

    SMA_trading_graph(40, 100, return_df, test_ticker)
    profit_graph(return_df, 0, test_ticker, return_df["Total"].iloc[-1])


def najdiOptimalneParametreNaEnem(data, ticker, hold_obdobje):
    print("Testiram na ucni mnozici")
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]
    testni_rezultati = {}
    counter = 0
    for long in long_values:
        # print("Trenutna Long vrednost: ", long)

        for short in short_values:
            testni_rezultati[f"[{short},{long}]"] = {}
            # print(f"Kombinacija: Short = {short} , Long = {long}")
            testni_rezultati[f"[{short},{long}]"] = sma_crossover(short, long, data, ticker, 0, 0, True, hold_obdobje)
            # print("Trenutna Short vrednost: ", short)
            # print()
            counter += 1

    # print("Counter: ", counter)
    print('Zaključil testiranje na enem')

    return testni_rezultati


def testirajNaEnemPodjetju(hold_obdobje):
    test_ticker = "HD"
    test_data_ucna = stockPricesDB.getCompanyStockDataInRange(date_from="2005-11-21", date_to="2016-5-21", companyTicker=test_ticker)

    test_data_ucna = test_data_ucna[['Close']].copy()
    test_data_ucna = zacetniDf(data=test_data_ucna)  # dodamo stolpce

    rez_ucni = najdiOptimalneParametreNaEnem(data=test_data_ucna, ticker=test_ticker, hold_obdobje=hold_obdobje)
    print(datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]

    for long in long_values:  # 210 range(100, 210, 10)
        # print("Trenutna Long vrednost: ", long)

        for short in short_values:  # 110 range(40, 110 , 10)

            if short != long:
                ucni_rezultati[f"[{short},{long}]"] = {}
                print(f"Kombinacija: Short = {short} , Long = {long}")
                # print debug
                # print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
                temp = backtest(start_period, end_period, short, long, dowTickers, stock_prices_db, hold_obdobje)
                # print("Data: ", temp)
                ucni_rezultati[f"[{short},{long}]"] = temp
                # print("Trenutna Short vrednost: ", short)
                print()
            counter += 1

    print("Counter: ", counter)

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_prices_db, hold_obdobje):
    rez_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2016-05-21", dowTickers=dowTickers,
                                                  stock_prices_db=stock_prices_db, hold_obdobje=hold_obdobje)
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


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, hold_obdobje):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje SMA Crossover strategije:
"""

holdObdobje = 1

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('sma strategy po klicu inicializacije objekta')

# testirajNaEnemPodjetju(hold_obdobje=holdObdobje)
# testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2016-05-21", short_sma=85, long_sma=200, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica
testirajNaPortfoliuEnoKombinacijo(start_date="2016-05-21", end_date="2021-01-01", short_sma=85, long_sma=200, dowTickers=dowJonesIndexData,
                                  stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
