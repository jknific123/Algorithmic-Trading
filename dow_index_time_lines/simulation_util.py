from datetime import datetime
from utility import utils as util


def filtrirajTradingDates(startDate, trading_dates):
    new_dates = []
    for date in trading_dates:
        if datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(startDate, '%Y-%m-%d'):
            new_dates.append(date)

    # odstranimo zacetne date od testnih mnozic
    if startDate == '2017-02-02':
        new_dates.remove('2018-09-10')
        new_dates.remove('2020-04-16')

    if startDate == '2018-09-10':
        new_dates.remove('2020-04-16')

    return new_dates


def pridobiIndexStartDate(startDate, vsi_datumi):
    for x in range(0, len(vsi_datumi)):
        if vsi_datumi[x] == startDate:
            return x


def trimUstreznaPodjetja(ustrezna_podjetja, datum):
    if len(ustrezna_podjetja) < 7:
        print('PROBLEM, letos je manj kot 7 podjetji ustreznih: ', datum)
    if len(ustrezna_podjetja) > 13:
        return ustrezna_podjetja[0:13]
    else:
        return ustrezna_podjetja


def preveriSpremembeHoldingov(holdings, ustrezna_podjetja):
    listUstreznih = []
    for ustrezni in ustrezna_podjetja:
        listUstreznih.append(ustrezni[1])

    # damo oboje v list in ju sortiramo nato pa primerjamo
    trenutni_holdings = list(holdings.keys())
    trenutni_holdings.sort()
    listUstreznih.sort()

    if trenutni_holdings == listUstreznih:
        return False

    return True


def sortirajGledeNaPrimernost(portfolio, datum, trgovalna_strategija):

    if trgovalna_strategija == 'P/E':
        return sortirajGledeNaPrimernostPE(portfolio, datum)
    elif trgovalna_strategija == 'P/B':
        return sortirajGledeNaPrimernostPB(portfolio, datum)
    elif trgovalna_strategija == 'DIVIDEND':
        return sortirajGledeNaPrimernostDividend(portfolio, datum)


# za P/E strategijo
def sortirajGledeNaPrimernostPE(portfolio, datum):
    ustrezni = []
    for linija in portfolio:
        pe = portfolio[linija][datum]['P/E']
        avgPE = portfolio[linija][datum]['avgP/E']
        podjetje = portfolio[linija][datum]['Ticker']
        close = portfolio[linija][datum]['Close']
        if 0 < pe < avgPE:
            # linija,  podjetje, Close, P/E
            ustrezni.append((linija, podjetje, round(close, 4), pe, avgPE))

    sorted_by_pe = sorted(ustrezni, key=lambda tup: tup[3])

    return sorted_by_pe


# za P/B strategijo
def sortirajGledeNaPrimernostPB(portfolio, datum):
    ustrezni = []
    for linija in portfolio:
        pb = portfolio[linija][datum]['P/B']
        avgPB = portfolio[linija][datum]['avgP/B']
        podjetje = portfolio[linija][datum]['Ticker']
        close = portfolio[linija][datum]['Close']
        if 0 < pb < avgPB:
            # linija,  podjetje, Close, P/B
            ustrezni.append((linija, podjetje, round(close, 4), pb, avgPB))

    sorted_by_pb = sorted(ustrezni, key=lambda tup: tup[3])

    return sorted_by_pb


# za strategijo Dividendnega donosa
def sortirajGledeNaPrimernostDividend(portfolio, datum):
    ustrezni = []
    for linija in portfolio:
        dividendYield = portfolio[linija][datum]['dividendYield']
        dividendPayoutRatio = portfolio[linija][datum]['dividendPayoutRatio']
        podjetje = portfolio[linija][datum]['Ticker']
        close = portfolio[linija][datum]['Close']
        if dividendPayoutRatio:
            # linija,  podjetje, Close, dividendYield, dividendPayoutRatio
            ustrezni.append((linija, podjetje, round(close, 4), dividendYield, dividendPayoutRatio))

    sorted_by_dividend_yield = sorted(ustrezni, key=lambda tup: tup[3])

    return sorted_by_dividend_yield
