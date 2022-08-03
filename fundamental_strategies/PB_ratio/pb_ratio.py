import math
import pandas as pd
from datetime import datetime
import numpy as np
from utility import utils as util

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30

million = 1000000
hundred_million = 100 * million


def pb_ratio_strategy(start_date, end_date, df, ticker, starting_index, status, odZacetkaAliNe, fundamental_data):
    print('Zacetek strategije za podjetje: ', ticker, 'obdobje: ', start_date, ' - ', end_date)
    # za fundamentalne indikatorje in njihovo povprecje v letu
    lista_datumov_porocil = fundamental_data.getListOfDatesOfCompanyDataDict(ticker)
    company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, df.index[starting_index])  # pridobim zacetno letno porocilo in njegovo leto
    print('pridobivanje prvega letnega porocila za podjetje: ', ticker, 'datum novega porocila: ', company_report['datum'])
    company_data = company_report['porocilo']
    industrija_podjetja = company_report['porocilo']['sector']
    year_avg_data = fundamental_data.getAvgIndustryFundamentalDataForYear(industrija_podjetja, datetime.strptime(company_report['datum'], '%Y-%m-%d').year)  # pridobim povprecne indikatorje za zacetno leto
    prvo_porocilo = True
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

        # preverim da trenutni datum ni isti kot datum trenutnega porocila in da je trenutni datum v listi datumov letnih porocil podjetja, nato posodobim podatke indikatorjev
        trenutni_datum = df.index[x]
        if trenutni_datum != company_report['datum'] and trenutni_datum in lista_datumov_porocil:
            company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, trenutni_datum)
            print('zamenjava letnega porocila za podjetje: ', ticker, 'datum novega porocila: ', company_report['datum'])
            company_data = company_report['porocilo']
            year_avg_data = fundamental_data.getAvgIndustryFundamentalDataForYear(company_data['sector'], datetime.strptime(company_report['datum'], '%Y-%m-%d').year)
            if prvo_porocilo:  # ko se zamenja porocilo popravim to vrendost
                prvo_porocilo = False

        df["P/B"].to_numpy()[x] = company_data["P/B"]

        isDatumOk = (prvo_porocilo or trenutni_datum == company_report['datum'])

        # manjka -> BUY signal
        if isDatumOk and pogojBuy(currCompany_data=company_data, currCompanyIndustry_data=year_avg_data) and df["Close"].to_numpy()[x] != 0:
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
                df['Buy-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Buy-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                # samo na zacetku gledamo ostali cash
                if df['Cash'].to_numpy()[x] == 1000.00000:
                    df['Vlozeni Cash'].to_numpy()[x] = buyPrice
                    df['Ostali Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] - buyPrice
                    df['Cash'].to_numpy()[x] = 0
                else:
                    df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] - buyPrice  # posodbi cash

                df['Shares'].to_numpy()[x] = stDelnic
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x] + buyPrice

                if prvo_porocilo:  # ce smo pogledali prvo porocilo ga ne gledamo vec
                    prvo_porocilo = False

                check = 2

        # manjka -> Sell signal
        elif isDatumOk and pogojSell(currCompany_data=company_data, currCompanyIndustry_data=year_avg_data):

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
                df['Sell-Signal'].to_numpy()[x] = df["Close"].to_numpy()[x]
                df["Sell-date"].to_numpy()[x] = df.index[x]  # zapisem datum nakupa

                df['Buy'].to_numpy()[x] = 0  # zapisemo 0 da oznacimo da je zadnji signal bil sell
                df['Buy-date'].to_numpy()[x] = ""  # zapisemo "" da oznacimo da je zadnji signal bil sell

                df['Cash'].to_numpy()[x] = df['Cash'].to_numpy()[x] + sellPrice  # posodbi cash
                df['Shares'].to_numpy()[x] = 0
                # updejtamo total
                df['Total'].to_numpy()[x] = df['Cash'].to_numpy()[x]

                check = 1
        elif prvo_porocilo:  # ce smo pogledali prvo porocilo ga ne gledamo vec
            prvo_porocilo = False

    print('Konec strategije za podjetje: ', ticker)
    return df


def pogojBuy(currCompany_data, currCompanyIndustry_data):
    print('Pogoj buy')

    buy_flags = {}
    # buy_flags["P/B"] = True if currCompany_data["P/B"] < 16 else False  # manjsi od 16
    buy_flags["P/B"] = True if 0 < currCompany_data["P/B"] < currCompanyIndustry_data['avgP/B'] else False  # manjsi od povprecja industrije

    should_buy = True
    napacni_flagi = ''
    for flag in buy_flags:
        if buy_flags[flag] == False:
            should_buy = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(buy_flags[flag]) + ', '

    if not should_buy:
        print(napacni_flagi)

    return should_buy


def pogojSell(currCompany_data, currCompanyIndustry_data):
    print('Pogoj sell')
    sell_flags = {}
    # sell_flags["P/B"] = True if 16 <= currCompany_data["P/B"] else False  # vecji enak 16
    sell_flags["P/B"] = True if currCompany_data["P/B"] > currCompanyIndustry_data['avgP/B'] or 0 > currCompany_data["P/B"] else False  # vecji enak 16

    should_sell = True
    napacni_flagi = ''
    for flag in sell_flags:
        if sell_flags[flag] == False:
            should_sell = False
            napacni_flagi = napacni_flagi + flag + ' : ' + str(sell_flags[flag]) + ', '

    if not should_sell:
        print(napacni_flagi)

    return should_sell
