import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from mixed_strategies.moja_tehnicna.moja_tehnicna_backtester import backtest


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0

    # MACD parameters TODO stare vrednosti
    macd_dnevni = [[20, 40, 9], [20, 35, 9], [18, 40, 9]]
    macd_tedenski = [[20, 35, 9], [20, 40, 9], [18, 40, 9]]
    macd_mesecni = [[20, 35, 9], [20, 40, 9], [18, 40, 9]]
    macd_letni = [[20 ,24, 9], [18, 24, 9], [18, 30, 9]]

    # Stohastic oscilator parameters
    stohastic_dnevni = [[5, 9], [9, 9], [5, 6]]
    stohastic_tedenski = [[5, 9], [9, 9], [5, 6]]
    stohastic_mesecni = [[5, 9], [9, 9], [5, 6]]
    stohastic_letni = [[20 ,9], [20, 6], [9 , 3]]

    # Bollinger bands parameters
    bollinger_dnevni = [[50, 2.1], [40, 2.1], [30, 2]]
    bollinger_tedenski = [[50, 2.1], [40, 2.1], [30, 2]]
    bollinger_mesecni = [[40, 2.1], [50, 2.1], [30, 2]]
    bollinger_letni = [[30, 2], [40, 2.1], [50, 2.1]]



    for macd in macd_dnevni: # 210

        for stohastic in stohastic_dnevni:

            for bollinger in bollinger_dnevni:

                ucni_rezultati[f"[{macd},{stohastic},{bollinger}]"] = {}
                print(f"Kombinacija: MACD = {macd} , Stohastic = {stohastic}, Bollinger = {bollinger}")
                short_period = macd[0]
                long_period = macd[1]
                signal_period = macd[2]
                high_low_period = stohastic[0]
                d_sma_period = stohastic[1]
                sma_period = bollinger[0]
                bands_multiplayer = bollinger[1]
                temp = backtest(start_period, end_period, short_period, long_period, signal_period, high_low_period, d_sma_period, sma_period, bands_multiplayer,
                                dowTickers, stock_data, hold_obdobje)
                ucni_rezultati[f"[{macd},{stohastic},{bollinger}]"] = temp
                print()
                counter += 1

    print("Counter: ", counter)

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_prices_db, hold_obdobje):

    rez_ucni = najdiOptimalneParametreNaPotrfoliu("2005-11-21", "2017-02-02", dowTickers, stock_prices_db, hold_obdobje)
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


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_period_macd, long_period_macd, signal_period_macd, high_low_period_stohastic, d_sma_period_stohastic, sma_period_bollinger, bands_multiplayer_bollinger,
                                      dowTickers, stock_prices_db, hold_obdobje):

    tmp = backtest(start=start_date, end=end_date, short_period_macd=short_period_macd, long_period_macd=long_period_macd, signal_period_macd=signal_period_macd,
                   high_low_period_stohastic=high_low_period_stohastic, d_sma_period_stohastic=d_sma_period_stohastic, sma_period_bollinger=sma_period_bollinger,
                   bands_multiplayer_bollinger=bands_multiplayer_bollinger, dowTickers=dowTickers, stockPricesDB=stock_prices_db, hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['totals']['Total'].iat[-1])


"""
 Od tukaj naprej se izvaja testiranje Mixed tehnical strategije:
"""

# MACD crossover + Stohastic oscilator + Bollinger bands strategy
# datetmie = leto, mesec, dan

# MACD
#short_period = 12
#long_period = 26
#signal_period = 9

# Stohastic oscilator
#high_low_period = 14
#d_sma_period = 3

# Bollinger bands
#sma_period = 20
#bands_multiplayer = 2

holdObdobje = 365

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('stohastic oscilator strategy po klicu inicializacije objekta')

# testirajNaEnemPodjetju(hold_obdobje=holdObdobje)
# testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)


# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2017-02-02", short_period_macd=12, long_period_macd=26, signal_period_macd=9,
#                                   high_low_period_stohastic=14, d_sma_period_stohastic=3, sma_period_bollinger=20, bands_multiplayer_bollinger=2,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica 30%
testirajNaPortfoliuEnoKombinacijo(start_date="2017-02-02", end_date="2021-11-21", short_period_macd=1, long_period_macd=1, signal_period_macd=1,
                                  high_low_period_stohastic=5, d_sma_period_stohastic=3, sma_period_bollinger=30, bands_multiplayer_bollinger=2,
                                  dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica 20%
# testirajNaPortfoliuEnoKombinacijo(start_date="2018-09-09", end_date="2021-11-21", short_period=12, long_period=26, signal_period=9,
#                                   high_low_period=14, d_sma_period=3,
#                                   sma_period=20, bands_multiplayer=2,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica 10%
# testirajNaPortfoliuEnoKombinacijo(start_date="2020-04-16", end_date="2021-11-21", short_period_macd=1, long_period_macd=1, signal_period_macd=1,
#                                   high_low_period_stohastic=20, d_sma_period_stohastic=14, sma_period_bollinger=40, bands_multiplayer_bollinger=2.1,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

print('KONEC!!! ', datetime.datetime.now() - begin_time)





















