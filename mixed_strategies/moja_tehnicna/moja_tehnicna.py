import math
import pandas as pd
import datetime as datetime
import numpy as np

from functools import cache

from utility import utils as util

pd.options.mode.chained_assignment = None  # default='warn'


@cache
def days_between(d1, d2):
    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def pogojBollingerBands(x, df):
    if df["Close"].to_numpy()[x] < df[f'Lower band'].to_numpy()[x]:
        return "Buy"
    elif df["Close"].to_numpy()[x] > df[f'Upper band'].to_numpy()[x]:
        return "Sell"


def pogojStohascticOscilator(x, df):
    if df["%K"].to_numpy()[x] < 20 and df[f'%D'].to_numpy()[x] < 20 and df["%K"].to_numpy()[x] > df[f'%D'].to_numpy()[x]:   # and df["%K"].to_numpy()[x] > df[f'%D'].to_numpy()[x]
        return "Buy"
    elif df["%K"].to_numpy()[x] > 80 and df[f'%D'].to_numpy()[x] > 80 and df["%K"].to_numpy()[x] < df[f'%D'].to_numpy()[x]:  # and df["%K"].to_numpy()[x] < df[f'%D'].to_numpy()[x]
        return "Sell"


def pogojMACD(x, df):
    if df["MACD"].to_numpy()[x] > df[f"Signal MACD"].to_numpy()[x]:
        return "Buy"
    elif df["MACD"].to_numpy()[x] < df[f"Signal MACD"].to_numpy()[x]:
        return "Sell"


def pogojBuy(x, df):
    bol = pogojBollingerBands(x, df)
    osc = pogojStohascticOscilator(x, df)
    # macd = pogojMACD(x, df)

    if bol == "Buy" and osc == "Buy":  #  and macd == "Buy":
        return True
    else:
        return False


def pogojSell(x, df):
    bol = pogojBollingerBands(x, df)
    osc = pogojStohascticOscilator(x, df)
    # macd = pogojMACD(x, df)

    if bol == "Sell" and osc == "Sell":  # and macd == "Sell":
        return True
    else:
        return False


def mixed_tehnical_strategy(short_period_macd, long_period_macd, signal_period_macd, high_low_period_stohastic, d_sma_period_stohastic, sma_period_bollinger,
                            bands_multiplayer_bollinger, df, ticker, starting_index, status, odZacetkaAliNe, holdObdobje, potrebnoRezatiGledeNaDatum):
    # # MACD
    # df[f'EMA-{short_period_macd}'] = df['Close'].ewm(span=short_period_macd, adjust=False).mean()
    # df[f'EMA-{long_period_macd}'] = df['Close'].ewm(span=long_period_macd, adjust=False).mean()
    # df["MACD"] = df[f'EMA-{short_period_macd}'] - df[f'EMA-{long_period_macd}']
    # df[f"Signal MACD"] = df["MACD"].ewm(span=signal_period_macd, adjust=False).mean()

    # Stohastic Oscilator
    df[f'Low-{high_low_period_stohastic}-days'] = df['Low'].rolling(window=high_low_period_stohastic, min_periods=1, center=False).min()
    df[f'High-{high_low_period_stohastic}-days'] = df['High'].rolling(window=high_low_period_stohastic, min_periods=1, center=False).max()
    # df['%K'] = (df["Close"] - df[f'Low-{high_low_period_stohastic}-days']) / (df[f'High-{high_low_period_stohastic}-days'] - df[f'Low-{high_low_period_stohastic}-days']) * 100
    # df[f'%D'] = df["%K"].rolling(window=d_sma_period_stohastic, min_periods=1, center=False).mean()
    df['Fast %K'] = (df["Close"] - df[f'Low-{high_low_period_stohastic}-days']) / (df[f'High-{high_low_period_stohastic}-days'] - df[f'Low-{high_low_period_stohastic}-days']) * 100
    df[f'%K'] = df["Fast %K"].rolling(window=d_sma_period_stohastic, min_periods=1, center=False).mean()
    df[f'%D'] = df[f"%K"].rolling(window=d_sma_period_stohastic, min_periods=1, center=False).mean()

    # Bollinger Bands
    df["Typical price"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["STD"] = df["Typical price"].rolling(window=sma_period_bollinger, min_periods=1, center=False).std(ddof=0)
    df[f"TP SMA"] = df["Typical price"].rolling(sma_period_bollinger).mean()
    df['Upper band'] = df[f"TP SMA"] + (bands_multiplayer_bollinger * df["STD"])
    df['Lower band'] = df[f"TP SMA"] - (bands_multiplayer_bollinger * df["STD"])

    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo
    if odZacetkaAliNe is True and ticker != 'DOW':
        if potrebnoRezatiGledeNaDatum:
            indx_rezanja = util.poisciIndexZaRezanjeDf(df)
            df = df[indx_rezanja:]
        else:
            df = df[sma_period_bollinger:]
        if starting_index != 0:
            starting_index = starting_index - sma_period_bollinger  # treba je posodobiti tudi starting_index, ko se reze df

    # za racunanje davka na dobiček
    sellPrice = 0

    # check -> zato da nimamo dveh zapovrstnih buy/sell signalov: 2 = buy, 1 = sell
    # status = 0 -> zacnemo od zacetka

    # 1 -> zacenjamo od tam ko je bil zadnji signal sell
    # 2 -> zacenjamo od tam ko je bil zadnji signal buy
    check = status
    for x in range(starting_index, len(df)):

        # filing shares, cash, total
        if (x - 1) >= 0:  # preverimo ce smo znotraj tabele
            df['Shares'].to_numpy()[x] = np.nan_to_num(df['Shares'].to_numpy()[x - 1])  # prenesemo prejsnje st delnic naprej

            if x != starting_index:  # za izjeme ko dodamo nov ticker in ne smemo zbrisat starting cash
                df['Cash'].to_numpy()[x] = np.nan_to_num(df['Cash'].to_numpy()[x - 1])  # prenesemo prejsnji Cash naprej
            elif x == starting_index and odZacetkaAliNe is False:  # takrat ko je isto podjetje kot prej
                df['Cash'].to_numpy()[x] = np.nan_to_num(df['Cash'].to_numpy()[x - 1])  # prenesemo prejsnji Cash naprej

            df['Total'].to_numpy()[x] = (df['Cash'].to_numpy()[x] + util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x]))  # izracunamo total
            df['Ticker'].to_numpy()[x] = ticker
            df['Buy'].to_numpy()[x] = df['Buy'].to_numpy()[x - 1]
            df['Sell'].to_numpy()[x] = df['Sell'].to_numpy()[x - 1]
            df['Buy-date'].to_numpy()[x] = df['Buy-date'].to_numpy()[x - 1]
            df['Sell-date'].to_numpy()[x] = df['Sell-date'].to_numpy()[x - 1]

        else:  # zacetek tabele -> inicializacija vrednosti
            if df['Cash'].to_numpy()[x] == 0:  # nimamo se denarja
                df['Cash'].to_numpy()[x] = util.getMoney(ticker)
            df['Total'].to_numpy()[x] = (df['Cash'].to_numpy()[x] + util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x]))
            df['Ticker'].to_numpy()[x] = ticker

        pretekli_dnevi_buy = 0
        if df["Buy-date"].to_numpy()[x] != "":
            pretekli_dnevi_buy = days_between(df["Buy-date"].to_numpy()[x], df.index[x])

        # %K < 20 in %D < 20 in %K < %D -> buy signal
        if df["Close"].to_numpy()[x] != 0 and pogojBuy(x, df):

            # preverimo ceno ene delnice in ce imamo dovolj denarja, da lahko kupimo delnice
            cena_ene_delnice = df['Close'].to_numpy()[x] + util.percentageFee(util.feePercentage, df['Close'].to_numpy()[x])
            stDelnic = math.floor(df['Cash'].to_numpy()[x] / cena_ene_delnice)  # stevilo delnic, ki jih lahko kupimo z nasim denarjem
            if check != 2 and stDelnic > 0:  # zadnji signal ni bil buy in imamo dovolj denarja za nakup
                # kupi kolikor je možno delnic glede na cash
                buyPrice = stDelnic * cena_ene_delnice  # stDelnic * njihova cena -> dejanski denar potreben za nakup
                df['Buy'].to_numpy()[x] = buyPrice  # zapisemo buy price
                df['Sell'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je bil zadnji signal buy
                df['Sell-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je bil zadnji signal buy

                # za graf trgovanja
                df['Buy-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Buy-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] - buyPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = stDelnic
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x] + buyPrice

                check = 2

        # %K > 80 in %D > 80 in %K > %D -> sell signal
        elif df["Close"].to_numpy()[x] != 0 and pogojSell(x, df) and pretekli_dnevi_buy >= holdObdobje:

            if check != 1 and check != 0:  # zadnji signal ni bil sell in nismo na zacetku

                # prodaj vse delnic izracunaj profit in placaj davek
                sellPrice = util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x])  # delnice v denar, obracunamo fees
                profitPredDavkom = util.profit(df['Buy'].to_numpy()[x], sellPrice)  # izracunamo profit pred davkom

                # ce je dobicek pred davkom pozitiven zaracunamo davek na dobicek in ga odstejemo od sellPrice, da dobimo ostanek
                if profitPredDavkom > 0:
                    sellPrice = sellPrice - util.taxes(profitPredDavkom)  # popravimo sellPrice, tako da obracunamo davek

                df['Sell'].to_numpy()[x] = sellPrice  # zapisemo sell price
                df['Profit'].to_numpy()[x] = util.profit(df['Buy'].to_numpy()[x], sellPrice)
                # za graf trgovanja
                df['Sell-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Sell-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Buy'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                df['Buy-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] + sellPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = 0
                # updejtamo total
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x]

                check = 1

    return df
