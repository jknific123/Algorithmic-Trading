import datetime as datetime
import numpy as np
from mixed_strategies.moja_tehnicna.moja_tehnicna_backtester import backtest
from mixed_strategies.moja_tehnicna.moja_tehnicna import mixed_tehnical_strategy
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from mixed_strategies.moja_tehnicna.moja_tehnicna_grafi import stohastic_indicator_graf, profit_graph, bollinger_trading_graph
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


def najdiOptimalneParametreNaIndeksu(data, ticker, hold_obdobje):
    print("Testiram na testni")
    testni_rezultati = {}

    stohasticni_oscilator_kombinacije = StohasticOscilatorKombinacije()
    bollinger_bands_kombinacije = BBkombinacije()

    for stohastic in stohasticni_oscilator_kombinacije:
        for bollinger in bollinger_bands_kombinacije:
            testni_rezultati[f"[{stohastic},{bollinger}]"] = {}
            data_df = data.copy(deep=True)
            print(f"Kombinacija: Stohastic = {stohastic}, Bollinger = {bollinger}")
            short_period_macd = 1
            long_period_macd = 1
            signal_period_macd = 1
            high_low_period_stohastic = stohastic[0]
            d_sma_period_stohastic = stohastic[1]
            sma_period_bollinger = bollinger[0]
            bands_multiplayer_bollinger = bollinger[1]
            testni_rezultati[f"[{stohastic},{bollinger}]"] = mixed_tehnical_strategy(short_period_macd=short_period_macd, long_period_macd=long_period_macd,
                                                                                     signal_period_macd=signal_period_macd, high_low_period_stohastic=high_low_period_stohastic,
                                                                                     d_sma_period_stohastic=d_sma_period_stohastic, sma_period_bollinger=sma_period_bollinger,
                                                                                     bands_multiplayer_bollinger=bands_multiplayer_bollinger, df=data_df, ticker=ticker,
                                                                                     starting_index=0, status=0, odZacetkaAliNe=True, holdObdobje=hold_obdobje,
                                                                                     potrebnoRezatiGledeNaDatum=True)
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
    with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_indeks_ucna\/Moja_tehnicna_{company_ticker}_{hold_obdobje_string}.txt', 'w',
              encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(round(sorted_rez_total_ucni[x], 2)) + ' ' + str(
                util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], util.ucnaMnozicaLeta())) + '%'
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
    optimalni_dnevni = [[[25, 8], [30, 2]], [[15, 8], [30, 2]], [[25, 8], [40, 2.1]]]
    optimalni_tedenski = [[[25, 8], [30, 2]], [[15, 8], [30, 2]], [[25, 8], [40, 2.1]]]
    optimalni_mesecni = [[[15, 8], [30, 2]], [[9, 5], [20, 2]], [[25, 8], [40, 2.1]]]
    optimalni_letni = [[[25, 8], [30, 2]], [[9, 5], [20, 2]], [[25, 8], [40, 2.1]]]
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
            temp = mixed_tehnical_strategy(short_period_macd=1, long_period_macd=1, signal_period_macd=1, high_low_period_stohastic=kombinacija[0][0],
                                           d_sma_period_stohastic=kombinacija[0][1], sma_period_bollinger=kombinacija[1][0], bands_multiplayer_bollinger=kombinacija[1][1],
                                           df=data_df, ticker='^DJI', starting_index=0, status=0, odZacetkaAliNe=True, holdObdobje=hold_cas, potrebnoRezatiGledeNaDatum=True)

            koncno_stanje = temp['Total'].to_numpy()[-1]
            rez_total_testni[f"[{kombinacija[0]},{kombinacija[1]}]"] = koncno_stanje

        sorted_rez_total_testni = {k: v for k, v in sorted(rez_total_testni.items(), key=lambda item: item[1])}
        with open(f'D:\Faks\Algorithmic-Trading\/mixed_strategies\/moja_tehnicna\/moja_tehnicna_rezultati_indeks_testna\/Moja_tehnicna_^DJI_{hold_obdobje_string}_testna.txt', 'w',
                  encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.testnaMnozicaLeta())
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(
                    util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], util.testnaMnozicaLeta())) + '%'
                f.write(row_string)
                f.write('\n')
            f.write('hold_obdobje: ' + str(hold_cas))
            f.write('\n')
            f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
            f.write('\n')


def testirajNaIndeksuEnoKombinacijo(start_date, end_date, high_low_period_stohastic, d_sma_period_stohastic, sma_period_bollinger, bands_multiplayer_bollinger, stock_prices_db,
                                    hold_obdobje):
    indeks_data = stock_prices_db.getCompanyStockDataInRange(date_from=start_date, date_to=end_date, companyTicker='^DJI')
    indeks_data = indeks_data[['Close', 'High', 'Low']].copy()
    indeks_data = zacetniDf(data=indeks_data)  # dodamo stolpce
    data_df = indeks_data.copy(deep=True)
    tmp = mixed_tehnical_strategy(short_period_macd=1, long_period_macd=1, signal_period_macd=1,
                                  high_low_period_stohastic=high_low_period_stohastic, d_sma_period_stohastic=d_sma_period_stohastic,
                                  sma_period_bollinger=sma_period_bollinger, bands_multiplayer_bollinger=bands_multiplayer_bollinger,
                                  df=data_df, ticker='^DJI', starting_index=0, status=0, odZacetkaAliNe=True, holdObdobje=hold_obdobje, potrebnoRezatiGledeNaDatum=True)

    stohastic_indicator_graf(high_low_period_stohastic, d_sma_period_stohastic, tmp, '^DJI')
    bollinger_trading_graph(sma_period_bollinger, bands_multiplayer_bollinger, tmp, '^DJI')
    profit_graph(tmp, 0, '^DJI', tmp["Total"].iloc[-1])

    print('Total profit: ', tmp['Total'].iat[-1])
    print(
        f"[{high_low_period_stohastic},{d_sma_period_stohastic}],[{sma_period_bollinger},{bands_multiplayer_bollinger}]: {round(tmp['Total'].to_numpy()[-1], 2)} {util.povprecnaLetnaObrestnaMera(30000, tmp['Total'].to_numpy()[-1], util.vsaLeta())}%")
    print('hold_obdobje: ', hold_obdobje)
    print()


"""
 Od tukaj naprej se izvaja testiranje Moja tehnicna strategije na DJIA indeksu:
"""

list_hold_obdobja_indeks = [1, 7, 31, 365]
begin_time = datetime.datetime.now()
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('Moja tehnicna  indeks, inicializacije objekta')

# pozeniTestiranjeNaSamemIndeksu(hold_obdobja_list=list_hold_obdobja_indeks, stockPricesDBIndex=stockPricesDB)

# testirajOptimalneNaTestniMnoziciZaHoldObdobjaIndeks(testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja_indeks)

# # preverjanje uspesnosti optimalnih kombinacij na celotnem casovnem obdobju
testirajNaIndeksuEnoKombinacijo(start_date="2016-04-19", end_date="2021-11-21", high_low_period_stohastic=25, d_sma_period_stohastic=8, sma_period_bollinger=40,
                                bands_multiplayer_bollinger=2.1, stock_prices_db=stockPricesDB, hold_obdobje=1)
