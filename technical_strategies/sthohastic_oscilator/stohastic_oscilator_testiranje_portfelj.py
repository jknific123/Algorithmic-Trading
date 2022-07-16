import datetime as datetime
from technical_strategies.sthohastic_oscilator.stohastic_oscilator_backtester import backtest
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from utility import utils as util


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    K_dolzina_vrednost = [5, 9, 15, 20, 25]
    D_dolzina_vrednosti = [3, 5, 8, 11, 14]
    for k_sma in K_dolzina_vrednost:  # 210
        for d_sma in D_dolzina_vrednosti:  # 110
            if k_sma > d_sma:
                ucni_rezultati[f"[{k_sma},{d_sma}]"] = {}
                print(f"Kombinacija: K_SMA = {k_sma} , %D = {d_sma}")
                rezultati_backtesta = backtest(start=start_period, end=end_period, high_low_period=k_sma, d_sma_period=d_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db, hold_obdobje=hold_obdobje)
                ucni_rezultati[f"[{k_sma},{d_sma}]"] = rezultati_backtesta['Total'].to_numpy()[-1]

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
    with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\/sthohastic_oscilator\/Stohastic_rezultati_ucna\/stohastic_oscilator_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
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
    optimalni_dnevni = [[20, 14], [15, 11], [15, 14]]
    optimalni_tedenski = [[20, 14], [15, 11], [15, 14]]
    optimalni_mesecni = [[20, 14], [15, 11], [15, 14]]
    optimalni_letni = [[25, 3], [20, 5], [5, 3]]
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
            temp = backtest('2017-02-02', '2021-11-21', kombinacija[0], kombinacija[1], dowTickers, testnaStockPricesDB, hold_cas)
            koncno_stanje = temp['Total'].to_numpy()[-1]
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\/sthohastic_oscilator\/Stohastic_rezultati_testna\/stohastic_oscilator_{hold_obdobje_string}_testna.txt', 'w', encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta())
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], util.testnaMnozicaLeta())) + '%'
                f.write(row_string)
                f.write('\n')
            f.write('hold_obdobje: ' + str(hold_cas))
            f.write('\n')
            f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
            f.write('\n')


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, k_sma, d_sma, dowTickers, stock_prices_db, hold_obdobje_kombinacija_portfolio):
    tmp = backtest(start=start_date, end=end_date, high_low_period=k_sma, d_sma_period=d_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje_kombinacija_portfolio)

    print('Total profit: ', tmp['Total'].iat[-1])
    print(f"[{k_sma},{d_sma}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print('hold_obdobje: ', hold_obdobje_kombinacija_portfolio)
    print()


"""
 Od tukaj naprej se izvaja testiranje Stohastic oscilator strategije na portfelju:
"""

list_hold_obdobja_portelj = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('Stohastic oscilator strategy portfelj, inicializacije objekta')

# najdi opitmalne parametre na portfoliu za hold obdobja na ucni mnozici
# najdiOptimalneParametreNaPotrfoliuZaHoldObdobjaUcnaMnozica(hold_obdobja_list=list_hold_obdobja_portelj,
#                                                            dowJonesIndexDataPortfelj=dowJonesIndexData, stockPricesDBPortfelj=stockPricesDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_portelj)

# preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2021-11-21", k_sma=25, d_sma=3,
                                  dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=365)
