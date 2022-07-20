from datetime import datetime
from datetime import timedelta
import pandas as pd
from pandas.tseries.offsets import BDay  # BDay je bussines day
from dow_index_data import dow_jones_index_data_csv as dowIndexData


vsa_leta = [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
            2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]

avg_leta = [[2005, 2006, 2007], [2008], [2009, 2010, 2011], [2012], [2013], [2014, 2015], [2016, 2017, 2018], [2019], [2020, 2021]]


# vrne naslednji delovni datum ce trenutni datum ni delovni dan, vzame date time in vrne datum v string formatu
def to_week_day(date):
    if date.isoweekday() in {6, 7}:
        next_week_day_datum = date + BDay(1)  # pridobimo naslednji delovni dan
        # preverimo, da se slucajno nov delovni dan ni v naslednjem letu, ce je tako iscemo delavni dan za nazaj
        if next_week_day_datum.year > date.year:
            previous_week_day = date - BDay(1)
            return previous_week_day.strftime("%Y-%m-%d")
        else:
            return next_week_day_datum.strftime("%Y-%m-%d")
    return date.strftime("%Y-%m-%d")


def pridobiDatumeVsehLet(dictData):
    dictOfDates = {}
    for dokument in dictData:  # najprej poberem vsa leta iz dictData
        if dokument != 'company_profile':
            for zapis in dictData[dokument]:
                dictOfDates[zapis] = {}

    leta_keys = [datetime.strptime(leto, "%Y-%m-%d").year for leto in dictOfDates.keys()]
    for manjkajoce_leto in vsa_leta:
        if manjkajoce_leto not in leta_keys:
            new_leto_key = str(manjkajoce_leto) + '-12-28'
            dictOfDates[new_leto_key] = {}

    dictOfDates = dict(sorted(dictOfDates.items()))
    return dictOfDates


# preveri ce si datumi sledijo pravilno po vrsti po letih brez lukenj
def preveriPravilnostZaporedjaDatumov(df):
    for index in range(len(df)):
        if index != 0:
            preveriRazlikoDatumov(datetime.strptime(df.index[index], "%Y-%m-%d").year, datetime.strptime(df.index[index - 1], "%Y-%m-%d").year)


def preveriRazlikoDatumov(trenutni_datum, prejsnji_datum):
    # preverimo ce je pravilna razlika med leti datumov
    difference_in_years = trenutni_datum - prejsnji_datum
    if difference_in_years == 0:
        print('NAPAKA pri primerjavi let datumov, razlika je 0, datuma imata isto leto. trenutni_datum: ', trenutni_datum, ' prejsnji_datum: ', prejsnji_datum)
    elif difference_in_years < 0:
        print('NAPAKA pri primerjavi let datumov, razlika je negativna. trenutni_datum: ', trenutni_datum, ' prejsnji_datum: ', prejsnji_datum)
    elif difference_in_years != 1:
        print('NAPAKA razlika let datumov je vecja od 1!!  trenutni_datum: ', trenutni_datum, ' prejsnji_datum: ', prejsnji_datum)


def pridobiZapisIstegaLeta(x, vir):

    leto = datetime.strptime(x, "%Y-%m-%d").year
    tmp = ''  # v tmp si shranim en key iz vira da lahko v primeru da ni zapisa istega leta vseeno vrnem slovar z nicelnimi vrednostmi fundamentalnih kazalcev
    for y in vir:
        tmp = y
        if datetime.strptime(y, "%Y-%m-%d").year == leto:  # zapisa istega leta
            return y
    # ce ne najdem leta v viru, naredim nov zapis z nicelnimi vrednostmi
    vir[x] = nastaviVseVrednostiNaNic(vir[tmp])
    return x


def nastaviVseVrednostiNaNic(dataDict):
    copyDataDict = dataDict.copy()
    for x in copyDataDict:
        if isinstance(copyDataDict[x], int):
            copyDataDict[x] = 0
        elif isinstance(copyDataDict[x], float):
            copyDataDict[x] = 0.0
        elif isinstance(copyDataDict[x], str):
            copyDataDict[x] = ''
    return copyDataDict


def zmanjsajObsegPodatkovCsv(data):
    return_data = []
    for x in data:  # vzamem samo tiste zapise ki so mlajši od 1997
        if datetime.strptime(x["date"], "%Y-%m-%d").year >= datetime.strptime("1997-10-10", "%Y-%m-%d").year:
            return_data.append(x)

    return return_data


def obdelaj_podatke_csv(data, company, porocilo):
    # funkcija sfiltrira podatke ce sta slucajno dve letni porocili za isto leto, in vzame samo enega
    return_data = []
    preskoci_indeks = -1
    if company == 'JNJ':
        urediPodatkeLetnegaPorocilaZaPodjetjeJNJ(data)
    elif company == 'HD':
        urediPodatkeLetnegaPorocilaZaPodjetjeHD(data)
    elif company == 'WMT':
        urediPodatkeLetnegaPorocilaZaPodjetjeWMT(data)
    elif company == 'DIS':
        urediPodatkeLetnegaPorocilaZaPodjetjeDIS(data)
    elif company == 'GS':
        urediPodatkeLetnegaPorocilaZaPodjetjeGS(data)

    for i in range(len(data)):

        if i < (len(data) - 1):
            trenutni = datetime.strptime(data[i]["date"], "%Y-%m-%d").year
            naslednji = datetime.strptime(data[i + 1]["date"], "%Y-%m-%d").year
            if trenutni == naslednji:  # ce sta dva zapisa za isto leto uzami samo enega,
                print('dva zapisa letnih porocil v istem letu za porocilo: ', porocilo, ' , prilagajam za company: ', company, ' trenutni: ', trenutni, ' naslednji: ', naslednji)
                preskoci_indeks = i  # taprvega preskocimo ker je manjsi datum

        if i != preskoci_indeks:
            return_data.append(data[i])

    return return_data


def urediPodatkeLetnegaPorocilaZaPodjetjeGS(data):
    for x in data:
        if x["date"] == '2008-12-26':
            print('urejam: 2008-12-26')
            new_date = '2008-11-28'
            x["date"] = new_date


def urediPodatkeLetnegaPorocilaZaPodjetjeDIS(data):
    for x in data:
        if x["date"] == '2005-10-01':
            print('urejam: 2005-10-01')
            new_date = '2005-09-30'
            x["date"] = new_date
        elif x["date"] == '2009-10-03':
            print('urejam: 2009-10-03')
            new_date = '2009-09-30'
            x["date"] = new_date
        elif x["date"] == '2010-10-02':
            print('urejam: 2010-10-02')
            new_date = '2010-09-30'
            x["date"] = new_date
        elif x["date"] == '2011-10-01':
            print('urejam: 2011-10-01')
            new_date = '2011-09-30'
            x["date"] = new_date
        elif x["date"] == '2012-09-29':
            print('urejam: 2012-09-29')
            new_date = '2012-09-30'
            x["date"] = new_date
        elif x["date"] == '2013-09-28':
            print('urejam: 2013-09-28')
            new_date = '2013-09-30'
            x["date"] = new_date
        elif x["date"] == '2014-09-27':
            print('urejam: 2014-09-27')
            new_date = '2014-09-30'
            x["date"] = new_date
        elif x["date"] == '2015-10-03':
            print('urejam: 2015-10-03')
            new_date = '2015-09-30'
            x["date"] = new_date
        elif x["date"] == '2016-10-01':
            print('urejam: 2016-10-01')
            new_date = '2016-09-30'
            x["date"] = new_date
        elif x["date"] == '2018-09-29':
            print('urejam: 2018-09-29')
            new_date = '2018-09-30'
            x["date"] = new_date


def urediPodatkeLetnegaPorocilaZaPodjetjeHD(data):
    for x in data:
        if x["date"] == '2001-01-31':
            print('urejam: 2001-01-31')
            new_date = '2001-01-28'
            x["date"] = new_date


def urediPodatkeLetnegaPorocilaZaPodjetjeWMT(data):
    for x in data:
        if x["date"] == '2009-04-01':
            print('urejam: 2009-04-01')
            new_date = '2009-01-31'
            x["date"] = new_date
        elif x["date"] == '2021-03-22':
            print('urejam: 2021-03-22')
            new_date = '2021-01-31'
            x["date"] = new_date


def urediPodatkeLetnegaPorocilaZaPodjetjeJNJ(data):
    for x in data:
        if x["date"] == '1995-01-01':
            print('urejam: 1995-01-01')
            new_date = '1994-12-28'
            x["date"] = new_date
        elif x["date"] == '1999-01-03':
            print('urejam: 1999-01-03')
            new_date = '1998-12-28'
            x["date"] = new_date
        elif x["date"] == '2000-01-02':
            print('urejam: 2000-01-02')
            new_date = '1999-12-28'
            x["date"] = new_date
        elif x["date"] == '2005-01-02':
            print('urejam: 2005-01-02')
            new_date = '2004-12-28'
            x["date"] = new_date
        elif x["date"] == '2006-01-01':
            print('urejam: 2006-01-01')
            new_date = '2005-12-28'
            x["date"] = new_date
        elif x["date"] == '2010-01-03':
            print('urejam: 2010-01-03')
            new_date = '2009-12-28'
            x["date"] = new_date
        elif x["date"] == '2011-01-02':
            print('urejam: 2011-01-02')
            new_date = '2010-12-28'
            x["date"] = new_date
        elif x["date"] == '2012-01-01':
            print('urejam: 2012-01-01')
            new_date = '2011-12-28'
            x["date"] = new_date
        elif x["date"] == '2016-01-03':
            print('urejam: 2016-01-03')
            new_date = '2015-12-28'
            x["date"] = new_date
        elif x["date"] == '2017-01-01':
            print('urejam: 2017-01-01')
            new_date = '2016-12-28'
            x["date"] = new_date
        elif x["date"] == '2018-12-31':
            print('urejam: 2018-12-31')
            new_date = '2018-12-30'
            x["date"] = new_date
        elif x["date"] == '2021-01-03':
            print('urejam: 2021-01-03')
            new_date = '2020-12-28'
            x["date"] = new_date
        elif x["date"] == '2022-01-02':
            print('urejam: 2022-01-02')
            new_date = '2021-12-28'
            x["date"] = new_date



def getObdobjaInPodjetja():
    dowJonesIndexData = dowIndexData.dowJonesIndexData
    vsa_leta_podjetja_avg = {}

    vsa_leta_podjetja_avg[1997] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[1998] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[1999] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2000] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2001] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2002] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2003] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2004] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2005] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2006] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2007] = dowJonesIndexData['2005-11-21']['all']
    vsa_leta_podjetja_avg[2008] = dowJonesIndexData['2008-02-19']['all']
    vsa_leta_podjetja_avg[2009] = dowJonesIndexData['2009-06-08']['all']
    vsa_leta_podjetja_avg[2010] = dowJonesIndexData['2009-06-08']['all']
    vsa_leta_podjetja_avg[2011] = dowJonesIndexData['2009-06-08']['all']
    vsa_leta_podjetja_avg[2012] = dowJonesIndexData['2012-09-24']['all']
    vsa_leta_podjetja_avg[2013] = dowJonesIndexData['2013-09-23']['all']
    vsa_leta_podjetja_avg[2014] = dowJonesIndexData['2013-09-23']['all']
    vsa_leta_podjetja_avg[2015] = dowJonesIndexData['2015-03-19']['all']
    vsa_leta_podjetja_avg[2016] = dowJonesIndexData['2015-03-19']['all']
    vsa_leta_podjetja_avg[2017] = dowJonesIndexData['2015-03-19']['all']
    vsa_leta_podjetja_avg[2018] = dowJonesIndexData['2018-06-26']['all']
    vsa_leta_podjetja_avg[2019] = dowJonesIndexData['2019-04-02']['all']
    vsa_leta_podjetja_avg[2020] = dowJonesIndexData['2020-08-31']['all']
    vsa_leta_podjetja_avg[2021] = dowJonesIndexData['2020-08-31']['all']

    return vsa_leta_podjetja_avg


def pridobiPomembneFinancial(data):
    dictOfFinancials = {}
    for x in data:
        dictOfFinancials = get_financials_csv(dictOfFinancials, x)
    return dictOfFinancials


def pridobiPomembneBalanceSheet(data):
    dictOfBalanceSheet = {}
    for x in data:
        dictOfBalanceSheet = get_balance_sheet_csv(dictOfBalanceSheet, x)
    return dictOfBalanceSheet


def pridobiPomembneDFC(data):
    dictOfDFC = {}
    for x in data:
        get_dfc_csv(dictOfDFC, x)
    return dictOfDFC


def pridobiPomembneCompanyProfile(data):
    dictOfCompanyProfile = {}
    for x in data:
        get_company_profile_csv(dictOfCompanyProfile, x)
    return dictOfCompanyProfile


def pridobiPomembneEnterpriseValue(data):
    dictOfFEnterpriseValue = {}
    for x in data:
        get_enterprise_value_csv(dictOfFEnterpriseValue, x)
    return dictOfFEnterpriseValue


def pridobiPomembneIncomeStatement(data):
    dictOfIncomeStatement = {}
    for x in data:
        get_income_statement_csv(dictOfIncomeStatement, x)
    return dictOfIncomeStatement


def pridobiPomembneFinancialGrowth(data):
    dictOfFinancialGrowth = {}
    for x in data:
        get_financial_growth(dictOfFinancialGrowth, x)
    return dictOfFinancialGrowth


def get_financials_csv(financial_ratios_vrednosti, x):

    financial_ratios_vrednosti[x["date"]] = {}
    if x["profitabilityIndicatorRatios"]["netProfitMargin"] is not None:

        if x["profitabilityIndicatorRatios"]["netProfitMargin"] == "":
            financial_ratios_vrednosti[x["date"]]["profitMargin"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["profitMargin"] = round(float(x["profitabilityIndicatorRatios"]["netProfitMargin"]), 3)

    if x["investmentValuationRatios"]["priceEarningsRatio"] is not None:

        if x["investmentValuationRatios"]["priceEarningsRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["P/E"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["P/E"] = round(float(x["investmentValuationRatios"]["priceEarningsRatio"]), 3)

    if x["investmentValuationRatios"]["priceToBookRatio"] is not None:
        financial_ratios_vrednosti[x["date"]]["P/B"] = round(float(x["investmentValuationRatios"]["priceToBookRatio"]), 3)

    if x["investmentValuationRatios"]["priceEarningsToGrowthRatio"] is not None:
        if x["investmentValuationRatios"]["priceEarningsToGrowthRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["PEG"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["PEG"] = round(float(x["investmentValuationRatios"]["priceEarningsToGrowthRatio"]), 3)

    if x["debtRatios"]["debtEquityRatio"] is not None:

        if x["debtRatios"]["debtEquityRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["D/E"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["D/E"] = round(float(x["debtRatios"]["debtEquityRatio"]), 3)

    if x["profitabilityIndicatorRatios"]["returnOnEquity"] is not None:

        if x["profitabilityIndicatorRatios"]["returnOnEquity"] == "":
            financial_ratios_vrednosti[x["date"]]["ROE"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["ROE"] = round(float(x["profitabilityIndicatorRatios"]["returnOnEquity"]), 3)

    if x["profitabilityIndicatorRatios"]["returnOnAssets"] is not None:

        if x["profitabilityIndicatorRatios"]["returnOnAssets"] == "":
            financial_ratios_vrednosti[x["date"]]["ROA"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["ROA"] = round(float(x["profitabilityIndicatorRatios"]["returnOnAssets"]), 3)

    # if x["profitabilityIndicatorRatios"]["grossProfitMargin"] is not None:
    #
    #     if x["profitabilityIndicatorRatios"]["grossProfitMargin"] == "":
    #         financial_ratios_vrednosti[x["date"]]["grossProfitMargin"] = 0
    #     else:
    #         financial_ratios_vrednosti[x["date"]]["grossProfitMargin"] = round(float(x["profitabilityIndicatorRatios"]["grossProfitMargin"]), 3)

    if x["investmentValuationRatios"]["dividendYield"] is not None:

        if x["investmentValuationRatios"]["dividendYield"] == "":
            financial_ratios_vrednosti[x["date"]]["dividendYield"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["dividendYield"] = round(float(x["investmentValuationRatios"]["dividendYield"]), 3)

    if x["cashFlowIndicatorRatios"]["dividendPayoutRatio"] is not None:

        if x["cashFlowIndicatorRatios"]["dividendPayoutRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["dividendPayoutRatio"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["dividendPayoutRatio"] = round(float(x["cashFlowIndicatorRatios"]["dividendPayoutRatio"]), 3)

    if x["cashFlowIndicatorRatios"]["freeCashFlowPerShare"] is not None:

        if x["cashFlowIndicatorRatios"]["freeCashFlowPerShare"] == "":
            financial_ratios_vrednosti[x["date"]]["freeCashFlowPerShare"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["freeCashFlowPerShare"] = round(float(x["cashFlowIndicatorRatios"]["freeCashFlowPerShare"]), 3)

    if x["cashFlowIndicatorRatios"]["operatingCashFlowSalesRatio"] is not None:

        if x["cashFlowIndicatorRatios"]["operatingCashFlowSalesRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["freeCashFlowMargin"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["freeCashFlowMargin"] = round(float(x["cashFlowIndicatorRatios"]["operatingCashFlowSalesRatio"]), 3)

    if x["liquidityMeasurementRatios"]["quickRatio"] is not None:

        if x["liquidityMeasurementRatios"]["quickRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["quickRatio"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["quickRatio"] = round(float(x["liquidityMeasurementRatios"]["quickRatio"]), 3)

    return financial_ratios_vrednosti


def get_balance_sheet_csv(balance_sheet_vrednosti, x):
    balance_sheet_vrednosti[x["date"]] = {}
    balance_sheet_vrednosti[x["date"]]["goodwill"] = round(float(x["goodwill"]), 3)
    return balance_sheet_vrednosti


def get_dfc_csv(discounted_cash_flow_vrednosti, x):
    if x["dcf"] is not None:
        discounted_cash_flow_vrednosti[x["date"]] = {}
        if x["dcf"] == "":
            discounted_cash_flow_vrednosti[x["date"]]["dcf"] = 0
            discounted_cash_flow_vrednosti[x["date"]]["price"] = 0
        else:
            discounted_cash_flow_vrednosti[x["date"]]["dcf"] = round(float(x["dcf"]), 3)
            discounted_cash_flow_vrednosti[x["date"]]["price"] = round(float(x["price"]), 3)

    return discounted_cash_flow_vrednosti


def get_company_profile_csv(company_profile_values, x):
    company_profile_values["ipoDate"] = x["ipoDate"]
    company_profile_values["sector"] = x["sector"]
    return company_profile_values


def get_enterprise_value_csv(enterprise_value_vrednosti, x):
    enterprise_value_vrednosti[x["date"]] = {}
    enterprise_value_vrednosti[x["date"]]["stockPrice"] = round(float(x["stockPrice"]), 3)
    enterprise_value_vrednosti[x["date"]]["numberOfShares"] = round(float(x["numberOfShares"]), 3)
    enterprise_value_vrednosti[x["date"]]["marketCapitalization"] = round(float(x["marketCapitalization"]), 3)
    return enterprise_value_vrednosti


def get_income_statement_csv(income_statement_vrednosti, x):
    income_statement_vrednosti[x["date"]] = {}
    income_statement_vrednosti[x["date"]]["revenue"] = round(float(x["revenue"]), 3)
    # income_statement_vrednosti[x["date"]]["ebitda"] = round(float(x["ebitda"]), 3)
    return income_statement_vrednosti


def get_financial_growth(financial_growth_vrednosti, x):
    financial_growth_vrednosti[x["date"]] = {}
    financial_growth_vrednosti[x["date"]]["revenueGrowth"] = round(float(x["revenueGrowth"]), 3)
    financial_growth_vrednosti[x["date"]]["netIncomeGrowth"] = round(float(x["netIncomeGrowth"]), 3)
    financial_growth_vrednosti[x["date"]]["freeCashFlowGrowth"] = round(float(x["freeCashFlowGrowth"]), 3)
    financial_growth_vrednosti[x["date"]]["dividendsperShareGrowth"] = round(float(x["dividendsperShareGrowth"]), 3)
    financial_growth_vrednosti[x["date"]]["fiveYDividendperShareGrowth"] = round(float(x["fiveYDividendperShareGrowthPerShare"]), 3)

    return financial_growth_vrednosti

