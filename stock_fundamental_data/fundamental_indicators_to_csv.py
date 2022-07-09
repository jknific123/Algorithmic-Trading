from datetime import datetime

import pandas as pd
import requests
from stock_fundamental_data.fundamental_indicators_util import fundamental_indicators_util as fUtil
from stock_fundamental_data.fundamental_indicators_util import average_data_calculation as avgUtil, dividend_calculation as dividendUtil

# AA ni tu not ker fundamentalen api za njega nima podatkov zato se uporablja HWM ticker
vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS',  'GE', 'GM',
                'GS', 'HD', 'HON', 'HPQ', 'HWM', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',
                'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30


# vrne slovar kjer so vsi podatki za neko podjetje
def doAllAPIcallsForCsv(company):

    slovar_podjetja = {}

    financial_ratios = requests.get(f'https://financialmodelingprep.com/api/v3/financial-ratios/{company}?limit={years}&apikey={api_key}')
    balance_sheet = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?limit={years}&apikey={api_key}')
    discounted_cash_flow = requests.get(f'https://financialmodelingprep.com/api/v3/historical-discounted-cash-flow-statement/{company}?limit={years}&apikey={api_key}')
    company_profile = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{company}?limit={years}&apikey={api_key}')
    enterprise_value = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-values/{company}?limit={years}&apikey={api_key}')
    income_statement = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?limit={years}&apikey={api_key}')

    # financials
    financial_ratios = financial_ratios.json()
    ratios = financial_ratios["ratios"]
    ratios = fUtil.zmanjsajObsegPodatkovCsv(ratios)  # skrajsaj
    ratios = list(reversed(ratios))
    ratios = fUtil.obdelaj_podatke_csv(ratios, company, 'financial_ratios')
    ratios = fUtil.pridobiPomembneFinancial(ratios)
    slovar_podjetja["financial_ratios"] = ratios

    # balance sheet
    balance_sheet = balance_sheet.json()
    balance_sheet = fUtil.zmanjsajObsegPodatkovCsv(balance_sheet)  # skrajsaj
    balance_sheet = list(reversed(balance_sheet))
    balance_sheet = fUtil.obdelaj_podatke_csv(balance_sheet, company, 'balance_sheet')
    balance_sheet = fUtil.pridobiPomembneBalanceSheet(balance_sheet)
    slovar_podjetja["balance_sheet"] = balance_sheet

    # discounted cash flow
    discounted_cash_flow = discounted_cash_flow.json()
    discounted_cash_flow = fUtil.zmanjsajObsegPodatkovCsv(discounted_cash_flow)  # skrajsaj
    discounted_cash_flow = list(reversed(discounted_cash_flow))
    discounted_cash_flow = fUtil.obdelaj_podatke_csv(discounted_cash_flow, company, 'discounted_cash_flow')
    discounted_cash_flow = fUtil.pridobiPomembneDFC(discounted_cash_flow)
    slovar_podjetja["discounted_cash_flow"] = discounted_cash_flow

    # company profile
    company_profile = company_profile.json()
    company_profile = fUtil.pridobiPomembneCompanyProfile(company_profile)
    slovar_podjetja["company_profile"] = company_profile

    # enterprise value
    enterprise_value = enterprise_value.json()
    enterprise_value = fUtil.zmanjsajObsegPodatkovCsv(enterprise_value)  # skrajsaj
    enterprise_value = list(reversed(enterprise_value))
    enterprise_value = fUtil.obdelaj_podatke_csv(enterprise_value, company, 'enterprise_value')
    enterprise_value = fUtil.pridobiPomembneEnterpriseValue(enterprise_value)
    slovar_podjetja["enterprise_value"] = enterprise_value

    # income statement
    income_statement = income_statement.json()
    income_statement = fUtil.zmanjsajObsegPodatkovCsv(income_statement)  # skrajsaj
    income_statement = list(reversed(income_statement))
    income_statement = fUtil.obdelaj_podatke_csv(income_statement, company, 'income_statement')
    income_statement = fUtil.pridobiPomembneIncomeStatement(income_statement)
    slovar_podjetja["income_statement"] = income_statement

    return slovar_podjetja


def mergeFundamentalDataCsv(data):
    mergedFundamentalDict = fUtil.pridobiDatumeVsehLet(data)
    for x in mergedFundamentalDict:
        mergedFundamentalDict[x].update(data['financial_ratios'][fUtil.pridobiZapisIstegaLeta(x, data['financial_ratios'])])
        mergedFundamentalDict[x].update(data['balance_sheet'][fUtil.pridobiZapisIstegaLeta(x, data['balance_sheet'])])
        mergedFundamentalDict[x].update(data['discounted_cash_flow'][fUtil.pridobiZapisIstegaLeta(x, data['discounted_cash_flow'])])
        mergedFundamentalDict[x].update(data['enterprise_value'][fUtil.pridobiZapisIstegaLeta(x, data['enterprise_value'])])
        mergedFundamentalDict[x].update(data['income_statement'][fUtil.pridobiZapisIstegaLeta(x, data['income_statement'])])
        mergedFundamentalDict[x]['dividendPerShare'] = round(mergedFundamentalDict[x]['dividendYield'] * mergedFundamentalDict[x]['price'], 4)
        mergedFundamentalDict[x]['dividendPaid'] = round(mergedFundamentalDict[x]['dividendYield'] *
                                                         mergedFundamentalDict[x]['price'] * mergedFundamentalDict[x]['numberOfShares'], 4)
        age = datetime.strptime(x, "%Y-%m-%d").year - datetime.strptime(data['company_profile']["ipoDate"], "%Y-%m-%d").year
        if age > 0:
            mergedFundamentalDict[x]["company_age"] = age
        else:
            mergedFundamentalDict[x]["company_age"] = 0
        mergedFundamentalDict[x]["sector"] = data['company_profile']["sector"]

    mergedFundamentalDict = dividendUtil.izracunajSePodatkeZaDividende(mergedFundamentalDict)
    return_data = {}
    modified_date_data = {}
    # pretvorimo se v datume, ki predstavljajo delovne dni, za normalen klic, za izracun avg pa ne
    for datum in mergedFundamentalDict:
        delovni_date = fUtil.to_week_day(datetime.strptime(datum, "%Y-%m-%d"))
        modified_date_data[delovni_date] = {}
        modified_date_data[delovni_date] = mergedFundamentalDict[datum]

    return_data['original'] = mergedFundamentalDict
    return_data['modified'] = modified_date_data
    return return_data


def dictToDfToCsvFile(dictToModify, company_name, directoryName, optionalString, preveriPravilnost):
    df = pd.DataFrame.from_dict(dictToModify, orient='index')
    if preveriPravilnost:
        fUtil.preveriPravilnostZaporedjaDatumov(df)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    df.to_csv(f'D:\Faks\Algorithmic-Trading\stock_fundamental_data\{directoryName}/fundamental_data_{company_name}{optionalString}.csv', index=False)


def getDataAllEverForCsv(allCompanies):
    count = 0
    allCompiesData = {}
    for x in allCompanies:
        dictToDf = mergeFundamentalDataCsv(doAllAPIcallsForCsv(x))
        if x == 'HWM':
            x = 'AA'  # uredim za izjemo
        allCompiesData[x] = dictToDf['modified']
        # najprej shranimo original v csv
        print('original to csv')
        dictToDfToCsvFile(dictToDf['original'], x, "raw_fundamental_data_original", "_original", True)
        print('modified to csv')
        dictToDfToCsvFile(dictToDf['modified'], x, "raw_fundamental_data_modified", "", True)
        count += 1
        print(f"DOWNLOADED data for {x}. {count}/{len(allCompanies)}")

    fundamentalAvgDict = avgUtil.getAllFundamentalAvgData(allCompiesData)
    print('delam AVG CSV')
    dictToDfToCsvFile(fundamentalAvgDict, 'AVERAGE', 'raw_fundamental_average_data', '', False)
    print('KONEC getDataAllEverForCsv')


def getAllFundamentalDAtaFromAPIsToCsv():
    begin_time = datetime.now()
    getDataAllEverForCsv(vsi_tickerji)
    print('KONEC!!! ', datetime.now() - begin_time)


"""
Tu je za testirat delovanje
"""
# tmp_ticker = 'HWM'
# dfToCsvFile = mergeFundamentalDataCsv(doAllAPIcallsForCsv(tmp_ticker))
# # najprej shranimo original v csv
# print('original to csv')
# dictToDfToCsvFile(dfToCsvFile['original'], tmp_ticker, "raw_fundamental_data_original", "_original3", True)
# print('modified to csv')
# dictToDfToCsvFile(dfToCsvFile['modified'], tmp_ticker, "raw_fundamental_data_modified", "_3", True)
# print('KONEC!!! ', datetime.now() - begin_time)
