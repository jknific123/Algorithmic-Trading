import math
import pandas as pd
import numpy as np
from utility import utils as util

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30

million = 1000000
hundred_million = 100 * million


def dividend_investing_sma_crossover_strategy(start_date, end_date, sPeriod, lPeriod, df, ticker, starting_index, status, odZacetkaAliNe, fundamental_data, potrebnoRezatiGledeNaDatum):
    print('Zacetek strategije za podjetje: ', ticker, 'obdobje: ', start_date, ' - ', end_date)
    # naredimo/napolnimo nova stolpca za oba SMA
    df[f'SMA-{sPeriod}'] = df['Close'].rolling(window=sPeriod, min_periods=1, center=False).mean()
    df[f'SMA-{lPeriod}'] = df['Close'].rolling(window=lPeriod, min_periods=1, center=False).mean()
    # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo
    if odZacetkaAliNe is True and ticker != 'DOW':
        if potrebnoRezatiGledeNaDatum:
            indx_rezanja = util.poisciIndexZaRezanjeDf(df)
            df = df[indx_rezanja:]
        else:
            df = df[lPeriod:]
        if starting_index != 0:
            starting_index = starting_index - lPeriod  # treba je posodobiti tudi starting_index, ko se reze df
    # za fundamentalne indikatorje
    lista_datumov_porocil = fundamental_data.getListOfDatesOfCompanyDataDict(ticker)
    company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, df.index[starting_index])  # pridobim zacetno letno porocilo in njegovo leto3
    print('pridobivanje prvega letnega porocila za podjetje: ', ticker, 'datum novega porocila: ', company_report['datum'])
    company_data = company_report['porocilo']
    prvo_porocilo = True
    fundamentalni_tradin_signal = -1  # nan vrednost, se ni dolocen
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

        # preverim, da trenutni datum ni isti kot datum trenutnega porocila in da je trenutni datum v listi datumov letnih porocil podjetja, nato posodobim podatke indikatorjev
        trenutni_datum = df.index[x]
        if trenutni_datum != company_report['datum'] and trenutni_datum in lista_datumov_porocil:
            company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, trenutni_datum)
            print('zamenjava letnega porocila za podjetje: ', ticker, 'datum novega porocila: ', company_report['datum'])
            company_data = company_report['porocilo']
            # if prvo_porocilo:  # ko se zamenja porocilo popravim to vrendost
            #     prvo_porocilo = False

        df["dividendYield"].to_numpy()[x] = company_data["dividendYield"]
        # df["fiveYearDividendGrowthRate"].to_numpy()[x] = company_data["fiveYearDividendGrowthRate"]
        df["fiveYDividendperShareGrowth"].to_numpy()[x] = company_data["fiveYDividendperShareGrowth"]
        df["dividendPayoutRatio"].to_numpy()[x] = company_data["dividendPayoutRatio"]

        if prvo_porocilo or trenutni_datum == company_report['datum']:
            fundamentalni_tradin_signal = dolociFundamentalniTradinSignal(currCompany_data=company_data, df=df, x=x)
            if prvo_porocilo:  # ko se prvic pogleda prvo porocilo popravim to vrendost
                prvo_porocilo = False

        tehnical_trading_signal = dolociTehnicalTradinSignal(df=df, x=x, sPeriod=sPeriod, lPeriod=lPeriod)

        # manjka -> BUY signal
        if fundamentalni_tradin_signal == 3 and tehnical_trading_signal == 5 and df["Close"].to_numpy()[x] != 0:
            print('SEM V BUY IN PROBAM KUPITI, datum: ', df.index[x])
            # preverimo ceno ene delnice in ce imamo dovolj denarja, da lahko kupimo delnice
            cena_ene_delnice = df['Close'].to_numpy()[x] + util.percentageFee(util.feePercentage, df['Close'].to_numpy()[x])
            stDelnic = math.floor(df['Cash'].to_numpy()[x] / cena_ene_delnice)  # stevilo delnic, ki jih lahko kupimo z nasim denarjem
            if check != 2 and stDelnic > 0:  # zadnji signal ni bil buy in imamo dovolj denarja za nakup
                print('SEM V BUY IN BOM KUPIL, datum: ', df.index[x])
                # kupi kolikor je možno delnic glede na cash
                buyPrice = stDelnic * cena_ene_delnice  # stDelnic * njihova cena -> dejanski denar potreben za nakup
                df['Buy'].to_numpy()[x] = buyPrice  # zapisemo buy price
                df['Sell'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je bil zadnji signal buy
                df['Sell-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je bil zadnji signal buy

                # za graf trgovanja
                df['Buy-Signal-Technical'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Buy-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] - buyPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = stDelnic
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x] + buyPrice

                check = 2

        # manjka -> Sell signal
        elif fundamentalni_tradin_signal == 4 and tehnical_trading_signal == 6:

            if check != 1 and check != 0:  # zadnji signal ni bil sell in nismo na zacetku
                print("SEM V SELL IN BOM PORODAL", df.index[x])

                # prodaj vse delnic izracunaj profit in placaj davek
                sellPrice = util.fees(df['Shares'].to_numpy()[x] * df['Close'].to_numpy()[x])  # delnice v denar, obracunamo fees
                profitPredDavkom = util.profit(df['Buy'].to_numpy()[x], sellPrice)  # izracunamo profit pred davkom

                # ce je dobicek pred davkom pozitiven zaracunamo davek na dobicek in ga odstejemo od sellPrice, da dobimo ostanek
                if profitPredDavkom > 0:
                    sellPrice = sellPrice - util.taxes(profitPredDavkom)  # popravimo sellPrice, tako da obracunamo davek

                df['Sell'].to_numpy()[x] = sellPrice  # zapisemo sell price
                df['Profit'].to_numpy()[x] = util.profit(df['Buy'].to_numpy()[x], sellPrice)
                # za graf trgovanja
                df['Sell-Signal-Technical'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Sell-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Buy'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                df['Buy-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] + sellPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = 0
                # updejtamo total
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x]

                check = 1

    print('Konec strategije za podjetje: ', ticker)
    return df


def fundamentalniPogojBuy(currCompany_data):
    print('Pogoj buy')
    #print(currCompany_data)
    #print()

    buy_flags = {}
    buy_flags["dividendYield"] = True if 0.02 <= currCompany_data["dividendYield"] <= 0.06 else False  # med 2% in 6%
    # buy_flags["fiveYearDividendGrowthRate"] = True if currCompany_data["fiveYearDividendGrowthRate"] > 0.05 else False  # nad 5%
    buy_flags["fiveYDividendperShareGrowth"] = True if currCompany_data["fiveYDividendperShareGrowth"] > 0.05 else False  # nad 5%
    buy_flags["dividendPayoutRatio"] = True if 0.35 <= currCompany_data["dividendPayoutRatio"] <= 0.55 else False  # med 35% in 55%

    should_buy = True
    napacni_flagi = ''
    for flag in buy_flags:
        if buy_flags[flag] == False:
            should_buy = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(buy_flags[flag]) + ', '

    if not should_buy:
        print(napacni_flagi)

    return should_buy


def fundamentalniPogojSell(currCompany_data):
    print('Pogoj sell')
    sell_flags = {}
    sell_flags["dividendYield"] = True if 0.02 > currCompany_data["dividendYield"] or currCompany_data["dividendYield"] > 0.06 else False  # manjsi od 2% ali vecji od 6%
    # sell_flags["fiveYearDividendGrowthRate"] = True if currCompany_data["fiveYearDividendGrowthRate"] <= 0.05 else False  # manjse enako 5%
    sell_flags["fiveYDividendperShareGrowth"] = True if currCompany_data["fiveYDividendperShareGrowth"] <= 0.05 else False  # nad 5%
    sell_flags["dividendPayoutRatio"] = True if 0.35 > currCompany_data["dividendPayoutRatio"] or currCompany_data["dividendPayoutRatio"] >= 0.7 else False  # manjse od 35%, vecje od 70%

    should_sell = True
    napacni_flagi = ''
    for flag in sell_flags:
        if sell_flags[flag] == False:
            should_sell = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(sell_flags[flag]) + ', '

    if not should_sell:
        print(napacni_flagi)

    return should_sell


def dolociFundamentalniTradinSignal(currCompany_data, df, x):
    # fundamentalni BUY signal => 3
    # fundamentalni SELL signal => 4
    if fundamentalniPogojBuy(currCompany_data=currCompany_data):
        df['Buy-Signal-Fundamental'].to_numpy()[x] = df["Close"].to_numpy()[x]
        return 3
    elif fundamentalniPogojSell(currCompany_data=currCompany_data):
        df['Sell-Signal-Fundamental'].to_numpy()[x] = df["Close"].to_numpy()[x]
        return 4

    return -2  # NAPAKA ne zgenerira se fundamentalni signal


def dolociTehnicalTradinSignal(df, x, sPeriod, lPeriod):
    # tehnical BUY signal => 5
    # tehnical SELL signal => 6
    # sSMA > lSMA -> buy signal
    if df[f'SMA-{sPeriod}'].to_numpy()[x] > df[f'SMA-{lPeriod}'].to_numpy()[x]:
        return 5
    elif df[f'SMA-{sPeriod}'].to_numpy()[x] < df[f'SMA-{lPeriod}'].to_numpy()[x]:
        return 6

    return -3  # NAPAKA ne zgenerira se tehnical signal
