import datetime as datetime

from technical_strategies.macd.macd import backtest


def najdiOptimalneParametreNaPotrfoliu(start_period, end_period, dowTickers, stock_data, hold_obdobje):
    print("Testiram na ucni mnozici")
    ucni_rezultati = {}
    counter = 0
    ema1_vrednosti = [10, 12, 15, 18, 20]
    ema2_vrednosti = [20, 24, 30, 35, 40]
    signal_vrednosti = [3, 6, 9]

    for ema1 in ema1_vrednosti:
        # print("Trenutna Long vrednost: ", long)

        for ema2 in ema2_vrednosti:

            for signal in signal_vrednosti:

                if ema1 != ema2:
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = {}
                    print(f"Kombinacija: Ema1 = {ema1} , Ema2 = {ema2} , Signal = {signal}")
                    # print debug
                    #print("Before: " ,ucni_rezultati[f"[{short},{long}]"])
                    temp = backtest(start_period, end_period, ema1, ema2, signal, dowTickers, stock_data, hold_obdobje)
                    #print("Data: ", temp)
                    ucni_rezultati[f"[{ema1},{ema2},{signal}]"] = temp
                    # print("Trenutna Short vrednost: ", short)
                    print()
                counter += 1

    #print("Counter: ", counter)

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

