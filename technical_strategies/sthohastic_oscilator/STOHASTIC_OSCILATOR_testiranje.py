import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.sthohastic_oscilator.stohastic_oscilator_backtester import backtest


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    SMA_vrednosti = [5, 9, 15, 20, 25]
    D_dolzina_vrednosti = [3, 6, 9]

    for sma in SMA_vrednosti:  # 210

        for d in D_dolzina_vrednosti:  # 110

            ucni_rezultati[f"[{sma},{d}]"] = {}
            print(f"Kombinacija: SMA = {sma} , %D = {d}")
            temp = backtest(start_period, end_period, sma, d, dowTickers, stock_data, hold_obdobje)
            ucni_rezultati[f"[{sma},{d}]"] = temp
            print()
            counter += 1

    print("Counter: ", counter)

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_prices_db, hold_obdobje):

    rez_ucni = najdiOptimalneParametreNaPotrfoliu("2005-11-21", "2016-06-20", dowTickers, stock_prices_db, hold_obdobje)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        print("Kombinacija : ", x)
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        print()

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, sma, d_sma, dowTickers, stock_prices_db, hold_obdobje):
    tmp = backtest(start=start_date, end=end_date, high_low_period=sma, d_sma_period=d_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje Stohastic oscilator strategije:
"""

holdObdobje = 1

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('stohastic oscilator strategy po klicu inicializacije objekta')

# testirajNaEnemPodjetju(hold_obdobje=holdObdobje)
# testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2016-06-20", sma=14, d_sma=3, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica
testirajNaPortfoliuEnoKombinacijo(start_date="2016-06-20", end_date="2021-01-01", sma=5, d_sma=9, dowTickers=dowJonesIndexData,
                                  stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
