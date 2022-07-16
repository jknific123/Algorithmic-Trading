import datetime as datetime
from mixed_strategies.moja_tehnicna.moja_tehnicna_backtester import backtest
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from utility import utils as util


def MACDkombinacije():
    ema_short_vrednosti = [10, 12, 15, 18, 20]
    ema_long_vrednosti = [20, 24, 30, 35, 40]
    signal_vrednosti = [3, 6, 9]
    macd_kombinacije = []
    for ema_short in ema_short_vrednosti:
        for ema_long in ema_long_vrednosti:
            for signal in signal_vrednosti:
                if ema_short != ema_long:
                    kombinacija = [ema_short, ema_long, signal]
                    macd_kombinacije.append(kombinacija)

    return macd_kombinacije


def BBkombinacije():
    bollinger_bands_kombinacije = [[10, 1.9], [20, 2], [30, 2], [40, 2.1], [50, 2.1]]
    return bollinger_bands_kombinacije


def StohasticOscilatorKombinacije():
    K_dolzina_vrednost = [5, 9, 15, 20, 25]
    D_dolzina_vrednosti = [3, 5, 8, 11, 14]
    stoh_kombinacije = []
    for k_sma in K_dolzina_vrednost:
        for d_sma in D_dolzina_vrednosti:
            if k_sma > d_sma:
                kombinacija = [k_sma, d_sma]
                stoh_kombinacije.append(kombinacija)

    return stoh_kombinacije


def stKombinacij(macd, bb, stoh):
    count = 0
    for macd_kombinacija in macd:
        for bb_kombinacija in bb:
            for stoh_kombinacija in stoh:
                count += 1

    print('stkombinacij: ', count)


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}

    # MACD parameters
    macd_dnevni_portfelj = [[18, 40, 9], [20, 35, 9], [20, 40, 9]]
    macd_tedenski_portfelj = [[20, 35, 9], [18, 40, 9], [20, 40, 9]]
    macd_mesecni_portfelj = [[20, 40, 9], [18, 40, 9], [20, 35, 9]]
    macd_letni_portfelj = [[18, 24, 9], [20, 24, 9], [15, 30, 9]]

    # Stohastic oscilator parameters
    stohastic_dnevni_portfelj = [[20, 14], [15, 14], [15, 11]]
    stohastic_tedenski_portfelj = [[20, 14], [15, 14], [15, 11]]
    stohastic_mesecni_portfelj = [[20, 14], [15, 14], [15, 11]]
    stohastic_letni_portfelj = [[5, 3], [20, 5], [25, 3]]

    # Bollinger bands parameters
    bollinger_dnevni_portfelj = [[30, 2], [40, 2.1], [50, 2.1]]
    bollinger_tedenski_portfelj = [[30, 2], [40, 2.1], [50, 2.1]]
    bollinger_mesecni_portfelj = [[30, 2], [40, 2.1], [50, 2.1]]
    bollinger_letni_portfelj = [[30, 2], [50, 2.1], [40, 2.1]]
    paramsDict = {
        1: [macd_dnevni_portfelj, stohastic_dnevni_portfelj, bollinger_dnevni_portfelj],
        7: [macd_tedenski_portfelj, stohastic_tedenski_portfelj, bollinger_tedenski_portfelj],
        31: [macd_mesecni_portfelj, stohastic_mesecni_portfelj, bollinger_mesecni_portfelj],
        365: [macd_letni_portfelj, stohastic_letni_portfelj, bollinger_letni_portfelj]}

    for macd in paramsDict[hold_obdobje][0]:
        for stohastic in paramsDict[hold_obdobje][1]:
            for bollinger in paramsDict[hold_obdobje][2]:
                ucni_rezultati[f"[{macd},{stohastic},{bollinger}]"] = {}
                print(f"Kombinacija: MACD = {macd} , Stohastic = {stohastic}, Bollinger = {bollinger}")
                short_period_macd = macd[0]
                long_period_macd = macd[1]
                signal_period_macd = macd[2]
                high_low_period_stohastic = stohastic[0]
                d_sma_period_stohastic = stohastic[1]
                sma_period_bollinger = bollinger[0]
                bands_multiplayer_bollinger = bollinger[1]
                rezultati_backtesta = backtest(start_period, end_period, short_period_macd, long_period_macd, signal_period_macd, high_low_period_stohastic, d_sma_period_stohastic,
                                               sma_period_bollinger, bands_multiplayer_bollinger, dowTickers, stock_prices_db, hold_obdobje)
                ucni_rezultati[f"[{macd},{stohastic},{bollinger}]"] = rezultati_backtesta['Total'].to_numpy()[-1]
                print()

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


def testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers, testnaStockPricesDB, hold_obdobja_list):
    optimalni_dnevni = [[[20, 35, 9], [15, 11], [30, 2]],  [[20, 40, 9], [20, 14], [30, 2]],  [[20, 40, 9], [15, 14], [30, 2]]]
    optimalni_tedenski = [[[18, 40, 9], [15, 11], [30, 2]],  [[20, 40, 9], [20, 14], [30, 2]],  [[20, 40, 9], [15, 14], [30, 2]]]
    optimalni_mesecni = [[[20, 35, 9], [20, 14], [30, 2]],  [[20, 35, 9], [15, 14], [30, 2]],  [[20, 35, 9], [15, 11], [30, 2]]]
    optimalni_letni = [[[20, 24, 9], [25, 3], [30, 2]],  [[18, 24, 9], [5, 3], [30, 2]],  [[20, 24, 9], [5, 3], [30, 2]]]
    dict_parametrov = {1: optimalni_dnevni, 7: optimalni_tedenski, 31: optimalni_mesecni, 365: optimalni_letni}

    for hold_cas in hold_obdobja_list:
        trenutni_parametri_list = []
        trenutni_parametri_list = dict_parametrov[hold_cas]
        hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
        print('Testiram za hold obdobje: ' + hold_obdobje_string, hold_cas)
        rez_total_testni = {}
        zacetni_cas = datetime.datetime.now()
        for kombinacija in trenutni_parametri_list:
            print('Kombinacija: ', kombinacija)
            temp = backtest('2017-02-02', '2021-11-21', short_period_macd=kombinacija[0][0], long_period_macd=kombinacija[0][1], signal_period_macd=kombinacija[0][2],
                            high_low_period_stohastic=kombinacija[1][0], d_sma_period_stohastic=kombinacija[1][1], sma_period_bollinger=kombinacija[2][0],
                            bands_multiplayer_bollinger=kombinacija[2][1], dowTickers=dowTickers, stockPricesDB=testnaStockPricesDB, hold_obdobje=hold_cas)
            koncno_stanje = temp['Total'].to_numpy()[-1]
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]},{kombinacija[2]}]"] = koncno_stanje

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_testna\/Moja_tehnicna_{hold_obdobje_string}_testna.txt', 'w', encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta())
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], util.testnaMnozicaLeta())) + '%'
                f.write(row_string)
                f.write('\n')
            f.write('hold_obdobje: ' + str(hold_cas))
            f.write('\n')
            f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
            f.write('\n')


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_period_macd, long_period_macd, signal_period_macd, high_low_period_stohastic, d_sma_period_stohastic, sma_period_bollinger, bands_multiplayer_bollinger,
                                      dowTickers, stock_prices_db, hold_obdobje):

    tmp = backtest(start=start_date, end=end_date, short_period_macd=short_period_macd, long_period_macd=long_period_macd, signal_period_macd=signal_period_macd,
                   high_low_period_stohastic=high_low_period_stohastic, d_sma_period_stohastic=d_sma_period_stohastic, sma_period_bollinger=sma_period_bollinger,
                   bands_multiplayer_bollinger=bands_multiplayer_bollinger, dowTickers=dowTickers, stockPricesDB=stock_prices_db, hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['Total'].iat[-1])
    print(f"[{short_period_macd},{long_period_macd},{signal_period_macd}],[{high_low_period_stohastic},{d_sma_period_stohastic}],[{sma_period_bollinger},{bands_multiplayer_bollinger}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print('hold_obdobje: ', hold_obdobje)
    print()


"""
 Od tukaj naprej se izvaja testiranje Moja tehnicna strategije na portfelju:
"""

list_hold_obdobja_portelj = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('Moja tehnicna strategy portfelj, inicializacije objekta')

# najdi opitmalne parametre na portfoliu za hold obdobja na ucni mnozici
# najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(hold_obdobja_list=list_hold_obdobja_portelj, dowJonesIndexDataPortfelj=dowJonesIndexData,
#                                                            stockPricesDBPortfelj=stockPricesDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_portelj)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", short_period_macd=20, long_period_macd=24, signal_period_macd=9,
                                  high_low_period_stohastic=5, d_sma_period_stohastic=3, sma_period_bollinger=30, bands_multiplayer_bollinger=2,
                                  dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=365)
