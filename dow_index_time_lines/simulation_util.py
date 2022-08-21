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
    if len(ustrezna_podjetja) < 10:
        print('PROBLEM, letos je manj kot 10 podjetji ustreznih: ', datum)
    if len(ustrezna_podjetja) > 10:
        return ustrezna_podjetja[0:10]
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
    elif trgovalna_strategija == 'VALUE':
        return sortirajGledeNaPrimernostValue(portfolio, datum)


# za P/E strategijo
def sortirajGledeNaPrimernostPE(portfolio, datum):
    ustrezni = []
    # neustrezni = []
    for linija in portfolio:
        pe = portfolio[linija][datum]['P/E']
        avgPE = portfolio[linija][datum]['avgP/E']
        podjetje = portfolio[linija][datum]['Ticker']
        close = portfolio[linija][datum]['Close']
        if 0 < pe < avgPE:
            # linija,  podjetje, Close, P/E
            ustrezni.append((linija, podjetje, round(close, 4), pe, avgPE))
    #     elif 0 < pe:
    #         neustrezni.append((linija, podjetje, round(close, 4), pe, avgPE))
    #
    # sorted_by_pe_neustrezni = sorted(neustrezni, key=lambda tup: tup[3])

    sorted_by_pe = sorted(ustrezni, key=lambda tup: tup[3])

    # if len(sorted_by_pe) < 10:
    #     concat_list = sorted_by_pe + sorted_by_pe_neustrezni
    #     # sorted_by_pe.extend(sorted_by_pe_neustrezni)
    #     sorted_by_pe = concat_list

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


# za strategijo Value investing
def sortirajGledeNaPrimernostValue(portfolio, datum):
    ustrezni = []
    for linija in portfolio:
        roe = portfolio[linija][datum]['ROE']
        profitMargin = portfolio[linija][datum]['ProfitMargin']
        de = portfolio[linija][datum]['D/E']
        avgDE = portfolio[linija][datum]['avgD/E']
        pb = portfolio[linija][datum]['P/B']
        avgPB = portfolio[linija][datum]['avgP/B']
        fcfMargin = portfolio[linija][datum]['freeCashFlowMargin']
        dcf = portfolio[linija][datum]['DCF']
        price = portfolio[linija][datum]['price']

        podjetje = portfolio[linija][datum]['Ticker']
        close = portfolio[linija][datum]['Close']
        # if roe and profitMargin and preveriDE(de, avgDE) and preveriPB(pb, avgPB) and preveriFcfMargin(fcfMargin) and preveriDCF(dcf, price):
        # linija,  podjetje, Close, ...
        ocenaPodjetja, napake = pridobiValueOceno(roe, profitMargin, de, avgDE, pb, avgPB, fcfMargin, dcf, price)
        # print('Podjetje: ', podjetje, 'ocena: ', ocenaPodjetja)
        ustrezni.append((linija, podjetje, round(close, 4), ocenaPodjetja, napake))

    sorted_by_value_ocena = sorted(ustrezni, key=lambda tup: tup[3], reverse=True)

    return sorted_by_value_ocena


def pridobiValueOceno(roe, profitMargin, de, avgDE, pb, avgPB, fcfMargin, dcf, price):
    ocena = 0
    napake = []
    if roe:
        ocena += 1
    else:
        # print('neustrezen ROE')
        napake.append('ROE')

    if profitMargin:
        ocena += 1
    else:
        # print('neustrezen PM')
        napake.append('PM')

    if preveriDE(de, avgDE):
        ocena += 1
    else:
        # print('neustrezen de')
        napake.append('de')

    if preveriPB(pb, avgPB):
        ocena += 1
    else:
        # print('neustrezen pb')
        napake.append('pb')

    if preveriFcfMargin(fcfMargin):
        ocena += 1
    else:
        # print('neustrezen fcfMargin')
        napake.append('fcfMargin')

    if preveriDCF(dcf, price):
        ocena += 1
    else:
        # print('neustrezen dcf')
        napake.append('dcf')

    return ocena, napake


def preveriDE(de, avgDe):
    if 0 < de <= avgDe:
        return True

    return False


def preveriPB(pb, avgPb):
    if 0 < pb <= avgPb:
        return True

    return False


def preveriFcfMargin(fcfMargin):
    if fcfMargin >= 0.1:
        return True

    return False


def preveriDCF(dcf, price):
    if dcf > price:
        return True

    return False
