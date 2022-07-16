import datetime as datetime
import numpy as np
from technical_strategies.sthohastic_oscilator.stohastic_oscilator_backtester import backtest
from technical_strategies.sthohastic_oscilator.stohastic_oscilator import stohastic_oscilator
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.sthohastic_oscilator.stohastic_oscilator_grafi import stohastic_trading_graph, profit_graph
from utility import utils as util


def zacetniDf(data):
    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako
    # kreiramo nova stolpca za buy/sell signale
    data['Buy'] = np.nan
    data['Sell'] = np.nan
    data['Cash'] = 0.0
    data['Shares'] = 0
    data['Profit'] = 0.0
    data['Total'] = 0.0
    data['Ticker'] = ""
    data['Buy-Signal'] = np.nan
    data['Sell-Signal'] = np.nan
    data["Buy-date"] = ""
    data["Sell-date"] = ""

    return data


def najdiOptimalneParametreNaIndeksu(data, ticker, hold_obdobje):
    print("Testiram na ucni mnozici")
    K_dolzina_vrednost = [5, 9, 15, 20, 25]
    D_dolzina_vrednosti = [3, 5, 8, 11, 14]
    testni_rezultati = {}
    for k_sma in K_dolzina_vrednost:  # 210
        for d_sma in D_dolzina_vrednosti:  # 110
            if k_sma > d_sma:
                testni_rezultati[f"[{k_sma},{d_sma}]"] = {}
                data_df = data.copy(deep=True)
                print(f"Kombinacija: K_SMA = {k_sma} , %D = {d_sma}")
                testni_rezultati[f"[{k_sma},{d_sma}]"] = stohastic_oscilator(high_low_period=k_sma, d_sma_period=d_sma, df=data_df, ticker=ticker, starting_index=0, status=0,
                                                                             odZacetkaAliNe=True, holdObdobje=hold_obdobje, potrebnoRezatiGledeNaDatum=True)

    return testni_rezultati


def testirajNaIndeksuUcnaMnozica(company_ticker, hold_obdobje, stockPricesDBIndex):
    print('Testiram podjetje: ', company_ticker)
    zacetni_cas_na_enem = datetime.datetime.now()
    # '2005-02-07' namesto '2005-11-21 za max long sma na ucni mnozici
    company_data_ucna = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2017-02-02", companyTicker=company_ticker)
    company_data_ucna = company_data_ucna[['Close', 'High', 'Low']].copy()
    company_data_ucna = zacetniDf(data=company_data_ucna)  # dodamo stolpce

    rez_ucni = najdiOptimalneParametreNaIndeksu(data=company_data_ucna, ticker=company_ticker, hold_obdobje=hold_obdobje)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        rez_total_ucni[x] = rez_ucni[x]['Total'].to_numpy()[-1]

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}
    print('Rezultati: ')
    hold_obdobje_string = util.getStringForHoldObdobje(hold_obdobje)
    with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\/sthohastic_oscilator\/Stohastic_rezultati_indeks_ucna\/stohastic_oscilator_{company_ticker}_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(round(sorted_rez_total_ucni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], util.ucnaMnozicaLeta())) + '%'
            f.write(row_string)
            f.write('\n')
        f.write('hold_obdobje: ' + str(hold_obdobje))
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas_na_enem))
        f.write('\n')
        print('hold_obdobje: ', hold_obdobje)
        print(datetime.datetime.now() - zacetni_cas_na_enem)


def pozeniTestiranjeNaSamemIndeksu(hold_obdobja_list, stockPricesDBIndex):
    for hold_obdobje in hold_obdobja_list:
        testirajNaIndeksuUcnaMnozica(company_ticker='^DJI', hold_obdobje=hold_obdobje, stockPricesDBIndex=stockPricesDBIndex)


def testirajOptimalneNaTestniMnoziciZaHoldObdobjaIndeks(testnaStockPricesDB, hold_obdobja_list):
    optimalni_dnevni = [[20, 14], [25, 5], [25, 8]]
    optimalni_tedenski = [[20, 14], [25, 5], [25, 8]]
    optimalni_mesecni = [[15, 14], [20, 14], [25, 8]]
    optimalni_letni = [[25, 5], [25, 8], [20, 5]]
    dict_parametrov = {1: optimalni_dnevni, 7: optimalni_tedenski, 31: optimalni_mesecni, 365: optimalni_letni}

    indeks_data_testna = testnaStockPricesDB.getCompanyStockDataInRange(date_from="2016-04-19", date_to="2021-11-21", companyTicker='^DJI')
    indeks_data_testna = indeks_data_testna[['Close', 'High', 'Low']].copy()
    indeks_data_testna = zacetniDf(data=indeks_data_testna)  # dodamo stolpce

    for hold_cas in hold_obdobja_list:
        trenutni_parametri_list = []
        trenutni_parametri_list = dict_parametrov[hold_cas]
        hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
        print('Testiram za hold obdobje: ' + hold_obdobje_string, hold_cas)
        rez_total_testni = {}
        zacetni_cas = datetime.datetime.now()
        for kombinacija in trenutni_parametri_list:
            print('Kombinacija: ', kombinacija)
            data_df = indeks_data_testna.copy(deep=True)
            temp = stohastic_oscilator(kombinacija[0], kombinacija[1], data_df, '^DJI', 0, 0, True, hold_cas, True)
            koncno_stanje = temp['Total'].to_numpy()[-1]
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\/sthohastic_oscilator\/Stohastic_rezultati_indeks_testna\/bollinger_bands_^DJI_{hold_obdobje_string}_testna.txt', 'w', encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta())
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], util.testnaMnozicaLeta())) + '%'
                f.write(row_string)
                f.write('\n')
            f.write('hold_obdobje: ' + str(hold_cas))
            f.write('\n')
            f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
            f.write('\n')


def testirajNaIndeksuEnoKombinacijo(start_date, end_date, k_sma, d_sma, stock_prices_db, hold_obdobje_kombinacija_indeks):
    indeks_data = stock_prices_db.getCompanyStockDataInRange(date_from=start_date, date_to=end_date, companyTicker='^DJI')
    indeks_data = indeks_data[['Close', 'High', 'Low']].copy()
    indeks_data = zacetniDf(data=indeks_data)  # dodamo stolpce
    data_df = indeks_data.copy(deep=True)
    tmp = stohastic_oscilator(k_sma, d_sma, data_df, '^DJI', 0, 0, True, hold_obdobje_kombinacija_indeks, True)

    # bollinger_trading_graph(sma_period=sma_length, bands_multiplayer=bands_multiplayer, df=tmp, company='^DJI')
    # profit_graph(tmp, 0, '^DJI', tmp["Total"].iloc[-1])

    print('Total profit: ', tmp['Total'].iat[-1])
    print(f"[{k_sma},{d_sma}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print('hold_obdobje: ', hold_obdobje_kombinacija_indeks)
    print()


"""
 Od tukaj naprej se izvaja testiranje Stohastic oscilator strategije na DJIA indeksu:
"""

# sma_period = 20
# bands_multiplayer = 2
list_hold_obdobja_indeks = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('BB strategy indeks, inicializacije objekta')


# pozeniTestiranjeNaSamemIndeksu(hold_obdobja_list=list_hold_obdobja_indeks, stockPricesDBIndex=stockPricesDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobjaIndeks(testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_indeks)

# # preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
# testirajNaIndeksuEnoKombinacijo(start_date="2005-02-07", end_date="2021-11-21", k_sma=20, d_sma=5,
#                                 stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_indeks=365)