import datetime as datetime
from technical_strategies.sma_crossover.sma_backtester import zacetniDf, backtest
from technical_strategies.sma_crossover.sma_crossover_nov import sma_crossover
# from dow_index_data import dow_jones_companies as dow
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.sma_crossover.sma_grafi import SMA_trading_graph, SMA_trading_graph_diplomska, profit_graph
from utility import utils as util


def najdiOptimalneParametreNaEnem(data, ticker, hold_obdobje):
    print("Testiram na ucni mnozici")
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]
    testni_rezultati = {}
    counter = 0
    for long in long_values:
        for short in short_values:
            if long != short:
                testni_rezultati[f"[{short},{long}]"] = {}
                data_df = data.copy(deep=True)
                testni_rezultati[f"[{short},{long}]"] = sma_crossover(short, long, data_df, ticker, 0, 0, True, hold_obdobje, True)
                counter += 1
    # print('Zaključil testiranje na enem')

    return testni_rezultati


def testirajNaEnemPodjetju(company_ticker, hold_obdobje, stockPricesDBIndex):
    print('Testiram podjetje: ', company_ticker)
    zacetni_cas_na_enem = datetime.datetime.now()
    # '2005-02-07' namesto '2005-11-21 za max long sma na ucni mnozici
    company_data_ucna = stockPricesDB.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2017-02-02", companyTicker=company_ticker)
    company_data_ucna = company_data_ucna[['Close']].copy()
    company_data_ucna = zacetniDf(data=company_data_ucna)  # dodamo stolpce

    rez_ucni = najdiOptimalneParametreNaEnem(data=company_data_ucna, ticker=company_ticker, hold_obdobje=hold_obdobje)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        rez_total_ucni[x] = rez_ucni[x]['Total'].to_numpy()[-1]

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}
    print('Rezultati: ')
    hold_obdobje_string = util.getStringForHoldObdobje(hold_obdobje)
    with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\sma_crossover\sma_rezultati_indeks_ucna\SMA_crossover_{company_ticker}_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(sorted_rez_total_ucni[x]) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], 3864 / 365)) + '%'  # 70% dni deljeno leto
            f.write(row_string)
            f.write('\n')
        f.write('hold_obdobje: ' + str(hold_obdobje))
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas_na_enem))
        f.write('\n')
        print('hold_obdobje: ', hold_obdobje)
        print(datetime.datetime.now() - zacetni_cas_na_enem)


def pozeniTestiranjeNaPosameznihPodjetjih(stockPricesDB, hold_obdobja_list):
    counter = 0
    for ticker in stockPricesDB.vsi_tickerji:
        for hold_obdobje in hold_obdobja_list:
            testirajNaEnemPodjetju(company_ticker=ticker, hold_obdobje=hold_obdobje, stockPricesDBIndex=stockPricesDB)
        counter += 1
    print('counter: ', counter)


def pozeniTestiranjeNaSamemIndeksu(hold_obdobja_list, stockPricesDBIndex):
    for hold_obdobje in hold_obdobja_list:
        testirajNaEnemPodjetju(company_ticker='^DJI', hold_obdobje=hold_obdobje, stockPricesDBIndex=stockPricesDBIndex)


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_prices_db, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    long_values = [100, 124, 150, 175, 200]
    short_values = [40, 54, 70, 85, 100]

    for long in long_values:  # 210 range(100, 210, 10)
        for short in short_values:  # 110 range(40, 110 , 10)
            if short != long:
                ucni_rezultati[f"[{short},{long}]"] = {}
                # print(f"Kombinacija: Short = {short} , Long = {long}")
                temp = backtest(start_period, end_period, short, long, dowTickers, stock_prices_db, hold_obdobje)
                ucni_rezultati[f"[{short},{long}]"] = temp
                # print()

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_prices_db, hold_cas):
    zacetni_cas = datetime.datetime.now()
    rez_ucni = najdiOptimalneParametreNaPotrfoliu(start_period="2005-11-21", end_period="2017-02-02", dowTickers=dowTickers,
                                                  stock_prices_db=stock_prices_db, hold_obdobje=hold_cas)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        # print("Kombinacija : ", x)
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        # print()
    #
    # print()
    # print("Sorted ucni!")
    # print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}
    hold_obdobje_string = util.getStringForHoldObdobje(hold_cas)
    with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\sma_crossover\sma_rezultati_ucna\SMA_crossover_{hold_obdobje_string}.txt', 'w', encoding='UTF8') as f:
        for x in sorted_rez_total_ucni:
            print(x, ": ", sorted_rez_total_ucni[x])
            row_string = str(x) + ': ' + str(sorted_rez_total_ucni[x]) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_ucni[x], 3864 / 365)) + '%'  # 70% dni deljeno leto
            f.write(row_string)
            f.write('\n')
        f.write('hold_obdobje: ' + str(hold_cas))
        f.write('\n')
        f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
        f.write('\n')


def testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers, testnaStockPricesDB, hold_obdobja_list):
    optimalni_dnevni = [[70, 175], [70, 200], [85, 200]]
    optimalni_tedenski = [[85, 150], [70, 200], [85, 200]]
    optimalni_mesecni = [[70, 200], [70, 175], [85, 200]]
    optimalni_letni = [[70, 175], [85, 200], [100, 200]]
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
        with open(f'D:\Faks\Algorithmic-Trading\/technical_strategies\sma_crossover\sma_rezultati_testna\SMA_crossover_{hold_obdobje_string}_testna.txt', 'w', encoding='UTF8') as f:
            for x in sorted_rez_total_testni:
                print(x, ': ', sorted_rez_total_testni[x], ' ', util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], 1656 / 365))  # 30% dni delejno eno leto
                row_string = str(x) + ': ' + str(round(sorted_rez_total_testni[x], 2)) + ' ' + str(util.povprecnaLetnaObrestnaMera(30000, sorted_rez_total_testni[x], 1656 / 365)) + '%' # 30% dni deljeno leto
                f.write(row_string)
                f.write('\n')
            f.write('hold_obdobje: ' + str(hold_cas))
            f.write('\n')
            f.write('KONEC! ' + str(datetime.datetime.now() - zacetni_cas))
            f.write('\n')


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, short_sma, long_sma, dowTickers, stock_prices_db, hold_obdobje_kombinacija_portfolio):
    tmp = backtest(start=start_date, end=end_date, sma_period_short=short_sma, sma_period_long=long_sma, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje_kombinacija_portfolio)

    print('Total profit: ', tmp['totals']['Total'].iat[-1])


# probal primerjat moje backteste s trejdanjem na DOW indexu...
def trejdajNaCelotnemIndexu(short_sma, long_sma, stockPricesDBIndex, hold_obdobje):
    index_ticker = "^DJI"
    # testiram od 2017-02-02 do 2021-11-21, za start date dam: '2015-09-02' za max sma na testni mnozci
    # test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2017-02-02", companyTicker=index_ticker)
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2017-02-02", date_to="2021-11-21", companyTicker='^DJI')

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = sma_crossover(short_sma, long_sma, test_data, index_ticker, 0, 0, True, hold_obdobje, True)

    SMA_trading_graph(short_sma, long_sma, return_df, index_ticker)
    profit_graph(return_df, 0, index_ticker, return_df["Total"].iloc[-1])


def trejdajNaPodjetju(ticker, short_sma, long_sma, stockPricesDBPodjetje, hold_obdobje):
    test_data = stockPricesDBPodjetje.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2010-11-21", companyTicker=ticker)

    test_data = test_data[['Close']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = sma_crossover(short_sma, long_sma, test_data, ticker, 0, 0, True, hold_obdobje, True)

    SMA_trading_graph_diplomska(short_sma, long_sma, return_df)


def testirajTrejdanjeNaCelotnemIndexu(stockPricesDBIndex, hold_obdobja_list):
    for hold_obdobje_index in hold_obdobja_list:
        trejdajNaCelotnemIndexu(hold_obdobje_index, stockPricesDBIndex=stockPricesDBIndex)


def najdiOptimalneParametreNaPotrfoliuZaHoldObdobja(hold_obdobja_list):
    for trenutno_hold_obdobje in hold_obdobja_list:
        testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_cas=trenutno_hold_obdobje)


"""
 Od tukaj naprej se izvaja testiranje SMA Crossover strategije:
"""

# holdObdobje = 1
list_hold_obdobja = [1, 7, 31, 365]
begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('sma strategy po klicu inicializacije objekta')

# trejdajNaPodjetju('^DJI', short_sma=50, long_sma=200, stockPricesDBPodjetje=stockPricesDB, hold_obdobje=1)

# trejdajNaCelotnemIndexu(short_sma=70, long_sma=175, stockPricesDBIndex=stockPricesDB, hold_obdobje=1)

# pozeniTestiranjeNaSamemIndeksu(hold_obdobja_list=list_hold_obdobja, stockPricesDBIndex=stockPricesDB)

# najdi opitmalne parametre na portfoliu za hold obdobja
# najdiOptimalneParametreNaPotrfoliuZaHoldObdobja(list_hold_obdobja)

# testirajOptimalneNaTestniMnoziciZaHoldObdobja(dowTickers=dowJonesIndexData, testnaStockPricesDB=stockPricesDB, hold_obdobja_list=list_hold_obdobja)

# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2017-02-02", short_sma=85, long_sma=200, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=1)

# testna mnozica 30%
# testirajNaPortfoliuEnoKombinacijo(start_date="2017-02-02", end_date="2021-11-21", short_sma=85, long_sma=160, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=1)

# testna mnozica 20%
# testirajNaPortfoliuEnoKombinacijo(start_date="2018-09-09", end_date="2021-11-21", short_sma=85, long_sma=160, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=1)

# testna mnozica 10%
# testirajNaPortfoliuEnoKombinacijo(start_date="2020-04-16", end_date="2021-11-21", short_sma=100, long_sma=200, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje_kombinacija_portfolio=365)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
