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


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    ucni_zacetna_investicijat = {}
    stohasticni_oscilator_kombinacije = StohasticOscilatorKombinacije()
    bollinger_bands_kombinacije = BBkombinacije()

    for stohastic in stohasticni_oscilator_kombinacije:
        for bollinger in bollinger_bands_kombinacije:
            ucni_rezultati[f"[{stohastic},{bollinger}]"] = {}
            print(f"Kombinacija: Stohastic = {stohastic}, Bollinger = {bollinger}")
            short_period_macd = 1
            long_period_macd = 1
            signal_period_macd = 1
            high_low_period_stohastic = stohastic[0]
            d_sma_period_stohastic = stohastic[1]
            sma_period_bollinger = bollinger[0]
            bands_multiplayer_bollinger = bollinger[1]
            rezultati_backtesta = backtest(start_period, end_period, short_period_macd, long_period_macd, signal_period_macd, high_low_period_stohastic, d_sma_period_stohastic,
                                           sma_period_bollinger, bands_multiplayer_bollinger, dowTickers, stock_prices_db, hold_obdobje)
            ucni_rezultati[f"[{stohastic},{bollinger}]"] = rezultati_backtesta['totals']['Total'].to_numpy()[-1]
            ucni_zacetna_investicijat[f"[{stohastic},{bollinger}]"] = rezultati_backtesta['zacetna investicija']

    ucni_return_dict = {'ucni_rezultati': ucni_rezultati, 'ucni_zacetna_investicijat': ucni_zacetna_investicijat}
    return ucni_return_dict


def testirajNaPortfoliuUcnaMnozica(dowTickers, stock_prices_db, hold_cas):
    zacetni_cas = datetime.datetime.now()
    # pridobimo dict key: kombinacija, value: koncno stanje sredstev
    return_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2020-04-16", dowTickers=dowTickers, stock_prices_db=stock_prices_db,
                                                     hold_obdobje=hold_cas)

    rez_total_ucni = return_ucni['ucni_rezultati']
    rez_zacetna_investicija_ucni = return_ucni['ucni_zacetna_investicijat']
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - zacetni_cas)

    # sortiram rezultate po velikosti koncnega stanja sredstev
    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
    with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_ucna_90_10\/Moja_tehnicna_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(round(sorted_rez_total_ucni[x], 2)) + ' ' + str(
                util.povprecnaLetnaObrestnaMera(rez_zacetna_investicija_ucni[x], sorted_rez_total_ucni[x], util.ucnaMnozicaLeta90procentov())) + '% ' + str(
                round(rez_zacetna_investicija_ucni[x], 2))

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
    optimalni_dnevni = [[[5, 3], [10, 1.9]],  [[9, 8], [20, 2]],  [[15, 14], [10, 1.9]]]
    optimalni_tedenski = [[[5, 3], [10, 1.9]],  [[9, 8], [20, 2]],  [[15, 14], [10, 1.9]]]
    optimalni_mesecni = [[[9, 5], [20, 2]],  [[9, 8], [20, 2]],  [[15, 14], [10, 1.9]]]
    optimalni_letni = [[[20, 3], [40, 2.1]],  [[9, 5], [10, 1.9]],  [[9, 5], [20, 2]]]
    dict_parametrov = {1: optimalni_dnevni, 7: optimalni_tedenski, 31: optimalni_mesecni, 365: optimalni_letni}

    for hold_cas in hold_obdobja_list:
        trenutni_parametri_list = []
        trenutni_parametri_list = dict_parametrov[hold_cas]
        hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
        print('Testiram za hold obdobje: ' + hold_obdobje_string, hold_cas)
        rez_total_testni = {}
        rez_zacetna_investicija_testni = {}
        zacetni_cas = datetime.datetime.now()
        for kombinacija in trenutni_parametri_list:
            print('Kombinacija: ', kombinacija)
            temp = backtest('2020-04-16', '2021-11-21', short_period_macd=1, long_period_macd=1, signal_period_macd=1,
                            high_low_period_stohastic=kombinacija[0][0], d_sma_period_stohastic=kombinacija[0][1], sma_period_bollinger=kombinacija[1][0],
                            bands_multiplayer_bollinger=kombinacija[1][1], dowTickers=dowTickers, stockPricesDB=testnaStockPricesDB, hold_obdobje=hold_cas)
            koncno_stanje = temp['totals']['Total'].to_numpy()[-1]
            zacetna_investicija = temp['zacetna investicija']
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje
            rez_zacetna_investicija_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = zacetna_investicija

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_testna_90_10\/Moja_tehnicna_{hold_obdobje_string}_testna.txt', 'w', encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta10procentov())
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(
                    util.povprecnaLetnaObrestnaMera(rez_zacetna_investicija_testni[x], sorted_rez_total_testni[x], util.testnaMnozicaLeta10procentov())) + '% ' + str(
                    round(rez_zacetna_investicija_testni[x], 2))

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
    print(f"[{high_low_period_stohastic},{d_sma_period_stohastic}],[{sma_period_bollinger},{bands_multiplayer_bollinger}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
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

testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_portelj)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", short_period_macd=1, long_period_macd=1, signal_period_macd=1,
#                                   high_low_period_stohastic=25, d_sma_period_stohastic=3, sma_period_bollinger=20, bands_multiplayer_bollinger=2,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=365)
