import math
import pandas as pd
from dow_index_time_lines import simulation_util as simUtil
from utility import utils as util


def backtestPortfolio(startDate, portfolio, trading_dates, index_column, stockPricesDB, trgovalna_strategija):

    if startDate == '2018-09-09':
        startDate = '2018-09-10'

    vsi_datumi = list(index_column)
    # pridobim ves zacetni denar
    all_cash = util.getMoney('') * 30
    # dict vseh podjetji, ki jih imamo trenutno kupljena
    holdings = {}
    ostali_cash = 0.0

    # filtriraj trading dates in vse datume glede na startDate
    trading_dates = simUtil.filtrirajTradingDates(startDate=startDate, trading_dates=trading_dates)
    startDate_index = simUtil.pridobiIndexStartDate(startDate=startDate, vsi_datumi=vsi_datumi)
    vsi_datumi = vsi_datumi[startDate_index:]
    df_totals = pd.DataFrame(data=0.0, index=vsi_datumi, columns=['Total'], dtype=float)

    # gledamo stanje za vsak dan posebej
    prvi_nakup = False
    indx = 0
    for date in vsi_datumi:

        if date in trading_dates:
            # preglej in sortiraj po primernosti letošnja podjetja glede na indikatorje
            ustrezna_podjetja = []
            ustrezna_podjetja = simUtil.sortirajGledeNaPrimernost(portfolio, date, trgovalna_strategija)
            # pridobi 7 -> 13 najbolj ustreznih podjetji za kupit to leto
            buy_podjetja = []
            buy_podjetja = simUtil.trimUstreznaPodjetja(ustrezna_podjetja, date)
            print()
            print('Buy podjetja: ', len(buy_podjetja), date)
            # če ni razlike z že kupljenimi potem ne naredi nič
            spremembe_holdingov = simUtil.preveriSpremembeHoldingov(holdings, ustrezna_podjetja)
            # če je kakšen nov potem prodaj vse trenutne in na novo razdeli denar in kupi vse, ki so ustrezni
            if spremembe_holdingov and date != startDate:
                print('spremembe holdingov')
                sell_cash = prodajTrenutneHoldinge(holdings, date, stockPricesDB)
                all_cash += sell_cash
                holdings = {}

            # kupi enakomerno vsa buy_podjetja
            holdings, all_cash = kupiBuyLines(holdings, buy_podjetja, all_cash, date)
            print('Kupljena podjetja: ', sorted(list(holdings.keys())))

            # ce je prvi nakup odpisemo ostali cash
            if date == startDate:
                ostali_cash = all_cash
                all_cash = 0.0

        df_totals['Total'].to_numpy()[indx] = izracunajTotalZaDan(holdings, date, all_cash, stockPricesDB)
        indx += 1

    return df_totals, ostali_cash


def prodajTrenutneHoldinge(holdings, datum, stockPricesDB):
    sell_cash = 0.0
    for podjetje in holdings:
        close = stockPricesDB.getCompanyStockDataForDate(datum, podjetje)['Close']
        # prodaj vse delnic izracunaj profit in placaj davek
        sellPrice = util.fees(holdings[podjetje]['Shares'] * close)  # delnice v denar, obracunamo fees
        profitPredDavkom = util.profit(holdings[podjetje]['buyPrice'], sellPrice)  # izracunamo profit pred davkom

        # ce je dobicek pred davkom pozitiven zaracunamo davek na dobicek in ga odstejemo od sellPrice, da dobimo ostanek
        if profitPredDavkom > 0:
            sellPrice = sellPrice - util.taxes(profitPredDavkom)  # popravimo sellPrice, tako da obracunamo davek

        sell_cash += sellPrice

    return sell_cash


def kupiBuyLines(holdings, buy_podjetja, currCash, datum):
    cash_per_line = currCash / len(buy_podjetja)  # razdelimo tretnutni cash med trenutne buy linije
    for podatki_podjetja in buy_podjetja:
        # preverimo ceno ene delnice in ce imamo dovolj denarja, da lahko kupimo delnice
        linija = podatki_podjetja[0]
        ticker = podatki_podjetja[1]
        podjetje_close = podatki_podjetja[2]
        cena_ene_delnice = podjetje_close + util.percentageFee(util.feePercentage, podjetje_close)
        stDelnic = math.floor(cash_per_line / cena_ene_delnice)  # stevilo delnic, ki jih lahko kupimo z nasim denarjem

        if stDelnic > 0:
            buyPrice = stDelnic * cena_ene_delnice
            currCash -= buyPrice
            if currCash < 0:
                print('NAPAKa currCash < 0')
            holdings[ticker] = {}
            holdings[ticker]['linija'] = linija
            holdings[ticker]['buyPrice'] = buyPrice
            holdings[ticker]['Buy_date'] = datum
            holdings[ticker]['Shares'] = stDelnic

    return holdings, currCash


def izracunajTotalZaDan(holdings, date, all_cash, stockPricesDB):

    total_today = 0.0
    total_today += all_cash

    for company in holdings:
        shares = holdings[company]['Shares']
        close_today = stockPricesDB.getCompanyStockDataForDate(date, company)
        company_total_today = util.fees(shares * close_today['Close'])
        total_today += company_total_today

    return total_today
