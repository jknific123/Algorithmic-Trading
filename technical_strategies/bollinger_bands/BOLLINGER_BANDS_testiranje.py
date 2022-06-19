import datetime as datetime


from technical_strategies.bollinger_bands.bollinger_bands_backtester import backtest
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    # key = sma_lenght, value = std_multiplier
    slovar_parametrov = {}
    slovar_parametrov[10] = 1.9
    slovar_parametrov[20] = 2
    slovar_parametrov[30] = 2
    slovar_parametrov[40] = 2.1
    slovar_parametrov[50] = 2.1
    for sma_length in slovar_parametrov: # 10 - 50
        # print("Trenutna Long vrednost: ", long)

        #for std_multiplier in range(40, 110 , 10): # 110

            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = {}
            print(f"Kombinacija: SMA length = {sma_length} , std_multiplier = {slovar_parametrov[sma_length]}")
            # print debug
            #print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
            temp = backtest(start_period, end_period, sma_length, slovar_parametrov[sma_length], dowTickers, stock_data, hold_obdobje)
            # backtest(start, end, sma_period, bands_multiplayer, dowTickers, stock_data, holdObdobje)
            #print("Data: ", temp)
            ucni_rezultati[f"[{sma_length},{slovar_parametrov[sma_length]}]"] = temp
            # print("Trenutna Short vrednost: ", short)
            print()
            counter += 1

    print("Counter: ", counter)

    return ucni_rezultati


def testirajNaPortfoliu(dowTickers, stock_data, hold_obdobje):

    rez_ucni = najdiOptimalneParametreNaPotrfoliu("2005-11-21", "2016-5-21", dowTickers, stock_data, hold_obdobje)
    print("Koncal testiranej na ucni: ", datetime.datetime.now() - begin_time)

    rez_total_ucni = {}
    for x in rez_ucni:
        rez_total_ucni[x] = {}
        # print debug
        print("Kombinacija : ", x)
        #print("Before in rez_total_ucni: ", rez_total_ucni[x])
        #print("Before in rez_total_ucni type: ", type(rez_total_ucni[x]))
        #print("Before in rez_ucni[x][Total].iat[-1]: ", rez_total_ucni[x])
        #print("Before in rez_ucni[x][Total].iat[-1] type: ", type(rez_total_ucni[x]))
        rez_total_ucni[x] = rez_ucni[x]['Total'].iat[-1]
        #print("After: ", rez_total_ucni[x])
        print()

    print()
    print("Sorted ucni!")
    print()

    sorted_rez_total_ucni = {k: v for k, v in sorted(rez_total_ucni.items(), key=lambda item: item[1])}

    for x in sorted_rez_total_ucni:
        print(x, ": ", sorted_rez_total_ucni[x])