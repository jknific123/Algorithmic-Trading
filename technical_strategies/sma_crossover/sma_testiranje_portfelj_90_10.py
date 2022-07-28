import datetime as datetime
from technical_strategies.sma_crossover.sma_backtester import zacetniDf, backtest
from technical_strategies.sma_crossover.sma_crossover_nov import sma_crossover
# from dow_index_data import dow_jones_companies as dow
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.sma_crossover.sma_grafi import SMA_trading_graph, profit_graph
from utility import utils as util


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    ucni_zacetna_investicijat = {}
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]

    for long in long_values:  # 210 range(100, 210, 10)
        for short in short_values:  # 110 range(40, 110 , 10)
            if short != long:
                ucni_rezultati[f"[{short},{long}]"] = {}
                # print(f"Kombinacija: Short = {short} , Long = {long}")
                rezultati_backtesta = backtest(start_period, end_period, short, long, dowTickers, stock_prices_db, hold_obdobje)
                ucni_rezultati[f"[{short},{long}]"] = rezultati_backtesta['totals']['Total'].to_numpy()[-1]
                ucni_zacetna_investicijat[f"[{short},{long}]"] = rezultati_backtesta['zacetna investicija']

    ucni_return_dict = {'ucni_rezultati': ucni_rezultati, 'ucni_zacetna_investicijat': ucni_zacetna_investicijat}
    return ucni_return_dict


def testirajNaPortfoliuUcnaMnozica(dowTickers, stock_prices_db, hold_cas):
    zacetni_cas = datetime.datetime.now()
    # pridobimo dict key: kombinacija, value: koncno stanje sredstev
    return_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2020-4-16", dowTickers=dowTickers, stock_prices_db=stock_prices_db,
                                                     hold_obdobje=hold_cas)

    rez_total_ucni = return_ucni['ucni_rezultati']
    rez_zacetna_investicija_ucni = return_ucni['ucni_zacetna_investicijat']
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - zacetni_cas)

    # sortiram rezultate po velikosti koncnega stanja sredstev
    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}
    hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
    with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\sma_crossover\sma_rezultati_ucna_90_10\SMA_crossover_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
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
    optimalni_dnevni = [[70, 175], [85, 200], [100, 200]]
    optimalni_tedenski = [[70, 175], [85, 200], [100, 200]]
    optimalni_mesecni = [[85, 200], [100, 200], [70, 175]]
    optimalni_letni = [[70, 175], [100, 175], [100, 200]]
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
            temp = backtest('2020-4-16', '2021-11-21', kombinacija[0], kombinacija[1], dowTickers, testnaStockPricesDB, hold_cas)
            koncno_stanje = temp['totals']['Total'].to_numpy()[-1]
            zacetna_investicija = temp['zacetna investicija']
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje
            rez_zacetna_investicija_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = zacetna_investicija

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\sma_crossover\sma_rezultati_testna_90_10\SMA_crossover_{hold_obdobje_string}_testna.txt', 'w',
                  encoding='UTF8') as f:
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


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, hold_obdobje_kombinacija_portfolio):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje_kombinacija_portfolio)

    print('Total profit: ', tmp['Total'].iat[-1])
    print(f"[{short_sma},{long_sma}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print('hold_obdobje: ', hold_obdobje_kombinacija_portfolio)
    print()


""" Testrianje SMA crossover na portelju delnic iz indeksa 90% - 10% """

list_hold_obdobja_portelj = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('Testrianje sma strategy portelj, inicializacija objektov')

# najdi opitmalne parametre na portfoliu za hold obdobja na ucni mnozici
# najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(hold_obdobja_list=list_hold_obdobja_portelj, dowJonesIndexDataPortfelj=dowJonesIndexData,
#                                                            stockPricesDBPortfelj=stockPricesDB)

testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_portelj)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", short_sma=100, long_sma=200,
#                                   dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=365)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
