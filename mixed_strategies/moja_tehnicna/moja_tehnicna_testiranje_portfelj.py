import datetime as datetime
from mixed_strategies.moja_tehnicna.moja_tehnicna_backtester import backtest
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from utility import utils as util


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0

    # MACD parameters
    macd_dnevni = [[20, 40, 9], [20, 35, 9], [18, 40, 9]]
    macd_tedenski = [[20, 35, 9], [20, 40, 9], [18, 40, 9]]
    macd_mesecni = [[20, 35, 9], [20, 40, 9], [18, 40, 9]]
    macd_letni = [[20, 24, 9], [18, 24, 9], [18, 30, 9]]

    # Stohastic oscilator parameters
    stohastic_dnevni = [[5, 9], [9, 9], [5, 6]]
    stohastic_tedenski = [[5, 9], [9, 9], [5, 6]]
    stohastic_mesecni = [[5, 9], [9, 9], [5, 6]]
    stohastic_letni = [[20, 9], [20, 6], [9, 3]]

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


def testirajNaPortfoliuUcnaMnozica(dowTickers, stock_prices_db, hold_cas):
    zacetni_cas = datetime.datetime.now()
    # pridobimo dict key: kombinacija, value: koncno stanje sredstev
    rez_total_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2017-02-02", dowTickers=dowTickers, stock_prices_db=stock_prices_db,
                                                        hold_obdobje=hold_cas)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    # sortiram rezultate po velikosti koncnega stanja sredstev
    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
    with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_ucna\/Moja_tehnicna_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(round(sorted_rez_total_ucni[x], 2)) + ' ' + str(
                util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], util.ucnaMnozicaLeta())) + '%'
            f.write(row_string)
            f.write('\n')
        f.write('hold_obdobje: ' + str(hold_cas))
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
        f.write('\n')


def najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(hold_obdobja_list, dowJonesIndexDataPortfelj, stockPricesDBPortfelj):
    for trenutno_hold_obdobje in hold_obdobja_list:
        testirajNaPortfoliuUcnaMnozica(dowTickers=dowJonesIndexDataPortfelj, stock_prices_db=stockPricesDBPortfelj, hold_cas=trenutno_hold_obdobje)




"""
 Od tukaj naprej se izvaja testiranje Moja tehnicna strategije na portfelju:
"""

list_hold_obdobja_portelj = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('Moja tehnicna strategy portfelj, inicializacije objekta')


# najdi opitmalne parametre na portfoliu za hold obdobja na ucni mnozici
najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(hold_obdobja_list=list_hold_obdobja_portelj,
                                                           dowJonesIndexDataPortfelj=dowJonesIndexData, stockPricesDBPortfelj=stockPricesDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_portelj)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", k_sma=25, d_sma=3,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=365)