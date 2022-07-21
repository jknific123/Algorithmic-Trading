import datetime as datetime

from mixed_strategies.moja_mesana.moja_mesana_value.moja_mesana_value_investing_backtester import zacetniDf, backtest
from mixed_strategies.moja_mesana.moja_mesana_value.moja_mesana_value_investing import value_investing_strategy
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from stock_fundamental_data import get_fundamental_data as getFundamentalIndicators
from mixed_strategies.moja_mesana.moja_mesana_value.moja_mesana_value_investing_grafi import mojaFundamentalna_trading_graph, profit_graph
from utility import utils as util


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, fundamental_indicators_db):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]

    for long in long_values:  # 210 range(100, 210, 10)
        for short in short_values:  # 110 range(40, 110 , 10)
            if short != long:
                ucni_rezultati[f"[{short},{long}]"] = {}
                print(f"Kombinacija: Short = {short} , Long = {long}")
                rezultati_backtesta = backtest(start_period, end_period, short, long, dowTickers, stock_prices_db, fundamental_indicators_db)
                ucni_rezultati[f"[{short},{long}]"] = rezultati_backtesta['Total'].to_numpy()[-1]

    return ucni_rezultati


def testirajNaPortfoliuUcnaMnozica(dowTickers, stock_prices_db, fundamental_indicators_db_portfelj):
    zacetni_cas = datetime.datetime.now()
    # pridobimo dict key: kombinacija, value: koncno stanje sredstev
    rez_total_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2017-02-02", dowTickers=dowTickers,
                                                        stock_prices_db=stock_prices_db, fundamental_indicators_db=fundamental_indicators_db_portfelj)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - zacetni_cas)

    # sortiram rezultate po velikosti koncnega stanja sredstev
    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}
    with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\moja_mesana\moja_mesana_value\mesana_value_ucna\Value_investing_SMA_crossover.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(round(sorted_rez_total_ucni[x], 2)) + ' ' + str(
                util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], util.ucnaMnozicaLeta())) + '%'
            f.write(row_string)
            f.write('\n')
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
        f.write('\n')


def najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(dowJonesIndexDataPortfelj, stockPricesDBPortfelj, fundamentalIndicatorsDBPortfelj):
    testirajNaPortfoliuUcnaMnozica(dowTickers=dowJonesIndexDataPortfelj, stock_prices_db=stockPricesDBPortfelj,
                                   fundamental_indicators_db_portfelj=fundamentalIndicatorsDBPortfelj)


def testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers, testnaStockPricesDB, fundamentalIndicatorsDB):
    optimalni_parametri = [[85, 100], [70, 124], [40, 100]]

    rez_total_testni = {}
    zacetni_cas = datetime.datetime.now()
    for kombinacija in optimalni_parametri:
        print('Kombinacija: ', kombinacija)
        temp = backtest('2017-02-02', '2021-11-21', kombinacija[0], kombinacija[1], dowTickers, testnaStockPricesDB, fundamentalIndicatorsDB)
        koncno_stanje = temp['Total'].to_numpy()[-1]
        rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje

    sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
    with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\moja_mesana\moja_mesana_value\mesana_value_testna\Value_investing_SMA_crossover_testna.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_testni:
            print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta())
            row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], util.testnaMnozicaLeta())) + '%'
            f.write(row_string)
            f.write('\n')
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
        f.write('\n')


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, fundamental_indicators_db):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers,
                   stockPricesDB=stock_prices_db, fundamental_data=fundamental_indicators_db)

    print('Total profit: ', tmp['Total'].iat[-1])
    print(f"[{short_sma},{long_sma}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print()


""" Testrianje Value investing + SMA crossover na portelju delnic iz indeksa """

begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
fundamentalIndicatorsDB = getFundamentalIndicators.StockFundamentalData()
print('Testrianje sma strategy portelj, inicializacija objektov')

# najdi opitmalne parametre na portfoliu za hold obdobja na ucni mnozici
# najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(dowJonesIndexDataPortfelj=dowJonesIndexData,
#                                                            stockPricesDBPortfelj=stockPricesDB, fundamentalIndicatorsDBPortfelj=fundamentalIndicatorsDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, fundamentalIndicatorsDB=fundamentalIndicatorsDB)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", short_sma=40, long_sma=100,
                                  dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, fundamental_indicators_db=fundamentalIndicatorsDB)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
