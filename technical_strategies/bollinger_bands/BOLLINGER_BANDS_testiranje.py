import datetime as datetime

import numpy as np
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
from technical_strategies.bollinger_bands.bollinger_bands_backtester import backtest
from technical_strategies.bollinger_bands.bollinger_bands import bollingerBands
from technical_strategies.bollinger_bands.bollinger_bands_grafi import bollinger_trading_graph, profit_graph


def zacetniDf(data):

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


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    # key = sma_lenght, value = std_multiplier
    slovar_parametrov = {10: 1.9, 20: 2, 30: 2, 40: 2.1, 50: 2.1}  # key-value pari
    for sma_length in slovar_parametrov:  # 10 - 50

            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = {}
            print(f"Kombinacija: SMA length = {sma_length} , std_multiplier = {slovar_parametrov[sma_length]}")
            temp = backtest(start_period, end_period, sma_length, slovar_parametrov[sma_length], dowTickers, stock_data, hold_obdobje)
            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = temp
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


def testirajNaPortfoliuEnoKombinacijo(start_date, end_date, sma_period, bands_multiplayer, dowTickers, stock_prices_db, hold_obdobje):
    tmp = backtest(start=start_date, end=end_date, sma_period=sma_period, bands_multiplayer=bands_multiplayer, dowTickers=dowTickers, stockPricesDB=stock_prices_db,
                   hold_obdobje=hold_obdobje)

    print('Total profit: ', tmp['totals']['Total'].iat[-1])


def trejdajSamoEnoPodjetje(sma_period, bands_multiplayer, stockPricesDBIndex, hold_obdobje):
    company_ticker = "AAPL"
    # testiram od 2017-02-02 do 2021-11-21, za start date dam: '2015-09-02' za max sma na testni mnozci
    # test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2017-02-02", companyTicker=index_ticker)
    test_data = stockPricesDBIndex.getCompanyStockDataInRange(date_from="2005-02-07", date_to="2007-02-07", companyTicker=company_ticker)

    test_data = test_data[['Close', 'High', 'Low']].copy()
    test_data = zacetniDf(test_data)  # dodamo stolpce
    return_df = bollingerBands(sma_period=sma_period, bands_multiplayer=bands_multiplayer, df=test_data, ticker=company_ticker,
                               starting_index=0, status=0, odZacetkaAliNe=True, holdObdobje=hold_obdobje, potrebnoRezatiGledeNaDatum=True)

    bollinger_trading_graph(sma_period=sma_period, bands_multiplayer=bands_multiplayer, df=return_df, company=company_ticker)
    profit_graph(return_df, 0, company_ticker, return_df["Total"].iloc[-1])


"""
 Od tukaj naprej se izvaja testiranje Bollinger bands strategije:
"""

# Bollinger bands strategy
# datetmie = leto, mesec, dan

# sma_period = 20
# bands_multiplayer = 2

holdObdobje = 1

begin_time = datetime.datetime.now()

# dowTickers = dow.endTickers  # podatki o sezonah sprememb dow jones indexa preko apija
dowJonesIndexData = dowIndexData.dowJonesIndexData
stockPricesDB = getStocks.StockOHLCData()
print('sma strategy po klicu inicializacije objekta')

# trejdajSamoEnoPodjetje(sma_period=20, bands_multiplayer=2, stockPricesDBIndex=stockPricesDB, hold_obdobje=1)

# testirajNaEnemPodjetju(hold_obdobje=holdObdobje)
# testirajNaPortfoliu(dowTickers=dowJonesIndexData, stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# ucna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2005-11-21", end_date="2017-02-02", sma_period=20, bands_multiplayer=2, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

# testna mnozica
# testirajNaPortfoliuEnoKombinacijo(start_date="2017-02-02", end_date="2021-11-21", sma_period=50, bands_multiplayer=2.1, dowTickers=dowJonesIndexData,
#                                   stock_prices_db=stockPricesDB, hold_obdobje=holdObdobje)

print('KONEC!!! ', datetime.datetime.now() - begin_time)
