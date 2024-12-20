import datetime as datetime
# import dow_jones_companies as dow
import requests
from dateutil.relativedelta import relativedelta

testni_all = ['AIG', 'AXP', 'BA', 'C', 'CAT', 'DD', 'DIS', 'GE', 'HD', 'HON', 'HPQ', 'HWM', 'IBM', 'INTC', 'JNJ', 'JPM', #'GM',
              'KO', 'MCD', 'MMM', 'MO', 'MRK', 'MSFT', 'PFE', 'PG', 'RTX', 'T', 'VZ', 'WMT', 'XOM']

vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS',  'GE', #'GM',
                'GS', 'HD', 'HON', 'HPQ', 'HWM', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',
                'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']

api_key = "950c6e208107d01d9616681a4cf99685"
years = 30

# funkcija za zračunat povprečja

# funkcija za zračunat eno podjetje

# vrne naslednji delovni datum ce trenutni datum ni delovni dan, uazme date time in vrne datum v string formatu
def to_week_day(date):
    if date.isoweekday() in set((6, 7)):
        date += datetime.timedelta(days=-date.isoweekday() + 8)
    return date.strftime("%Y-%m-%d")

def obdelaj_podatke(data):

    return_data = []

    preskoci_indeks = -1
    for i in range(len(data)):

        if i < (len(data) - 1):
            trenutni = datetime.datetime.strptime(data[i]["date"], "%Y-%m-%d").year
            naslednji = datetime.datetime.strptime(data[i + 1]["date"], "%Y-%m-%d").year
            if trenutni == naslednji: # ce sta dva zapisa za isto leto uzami samo enega
                preskoci_indeks = i # taprvega preskocimo ker je manjsi datum

        if i != preskoci_indeks:
            return_data.append(data[i])

    return return_data



def pridobiLanskiDatum(start_date, end_date, data):

    lanski_datum = ""
    for x in data:

        if datetime.datetime.strptime(start_date, "%Y-%m-%d") > datetime.datetime.strptime(x["date"], "%Y-%m-%d"):
            lanski_datum = x["date"]

    #print("LANSKI", lanski_datum)

    return lanski_datum

def get_financials(financial_ratios_vrednosti, x):

    financial_ratios_vrednosti[x["date"]] = {}
    if x["profitabilityIndicatorRatios"]["netProfitMargin"] is not None:

        if x["profitabilityIndicatorRatios"]["netProfitMargin"] == "":
            financial_ratios_vrednosti[x["date"]]["profitMargin"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["profitMargin"] = float(x["profitabilityIndicatorRatios"]["netProfitMargin"])


    if x["investmentValuationRatios"]["priceEarningsRatio"] is not None:

        if x["investmentValuationRatios"]["priceEarningsRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["P/E"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["P/E"] = float(x["investmentValuationRatios"]["priceEarningsRatio"])


    if x["investmentValuationRatios"]["priceToBookRatio"] is not None:
        financial_ratios_vrednosti[x["date"]]["P/B"] = float(x["investmentValuationRatios"]["priceToBookRatio"])

    if x["debtRatios"]["debtEquityRatio"] is not None:

        if x["debtRatios"]["debtEquityRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["D/E"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["D/E"] = float(x["debtRatios"]["debtEquityRatio"])


    if x["profitabilityIndicatorRatios"]["returnOnEquity"] is not None:

        if x["profitabilityIndicatorRatios"]["returnOnEquity"] == "":
            financial_ratios_vrednosti[x["date"]]["ROE"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["ROE"] = float(x["profitabilityIndicatorRatios"]["returnOnEquity"])


    if x["investmentValuationRatios"]["dividendYield"] is not None:

        if x["investmentValuationRatios"]["dividendYield"] == "":
            financial_ratios_vrednosti[x["date"]]["dividendYield"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["dividendYield"] = float(x["investmentValuationRatios"]["dividendYield"])

    if x["cashFlowIndicatorRatios"]["dividendPayoutRatio"] is not None:

        if x["cashFlowIndicatorRatios"]["dividendPayoutRatio"] == "":
            financial_ratios_vrednosti[x["date"]]["dividendPayoutRatio"] = 0
        else:
            financial_ratios_vrednosti[x["date"]]["dividendPayoutRatio"] = float(x["cashFlowIndicatorRatios"][
                "dividendPayoutRatio"])

    return financial_ratios_vrednosti



# Net profit margin, P/E, P/B, D/E, ROE, dividendYield, dividend payouth growth
def financial_ratios(company, start_date, end_date, fundamental_data_all):

    #financial_ratios = requests.get(f'https://financialmodelingprep.com/api/v3/financial-ratios/{company}?limit={years}&apikey={api_key}')
    #print(financial_ratios)
    #financial_ratios = financial_ratios.json()

    financial_ratios_vrednosti = {}

    #ratios = financial_ratios["ratios"]
    #ratios = list(reversed(ratios))
    #ratios = obdelaj_podatke(ratios)
    ratios = fundamental_data_all[company]["financial_ratios"]

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, ratios)

    for x in ratios:

        #print(x)
        #print()

        # za lanski datum
        if lanski_datum != "" and datetime.datetime.strptime(x["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            financial_ratios_vrednosti = get_financials(financial_ratios_vrednosti, x)

        ## za obdobje med start in end date
        if datetime.datetime.strptime(x["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d")  and datetime.datetime.strptime(x["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            financial_ratios_vrednosti = get_financials(financial_ratios_vrednosti, x)

    return financial_ratios_vrednosti

# samo za dividend payouth growth
def fGrowth(company, start_date, end_date, fundamental_data_all):


    growth_ratios_vrednosti = {}

    financial_growth = fundamental_data_all[company]["financial_growth"]

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, financial_growth)

    for i in range(len(financial_growth)):

        #print(x)
        #print()

        # za lanski datum
        if lanski_datum != "" and datetime.datetime.strptime(financial_growth[i]["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            if financial_growth[i]["fiveYDividendperShareGrowthPerShare"] is not None:
                growth_ratios_vrednosti[financial_growth[i]["date"]] = {}

                if financial_growth[i]["fiveYDividendperShareGrowthPerShare"] == "":
                    growth_ratios_vrednosti[financial_growth[i]["date"]]["dividendPayoutGrowth"] = 0
                else:
                    growth_ratios_vrednosti[financial_growth[i]["date"]]["dividendPayoutGrowth"] = float(financial_growth[i]["fiveYDividendperShareGrowthPerShare"])

        ## za obdobje med start in end date
        if datetime.datetime.strptime(financial_growth[i]["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d")  and datetime.datetime.strptime(financial_growth[i]["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            if financial_growth[i]["fiveYDividendperShareGrowthPerShare"] is not None:
                growth_ratios_vrednosti[financial_growth[i]["date"]] = {}

                if financial_growth[i]["fiveYDividendperShareGrowthPerShare"] == "":
                    growth_ratios_vrednosti[financial_growth[i]["date"]]["dividendPayoutGrowth"] = 0
                else:
                    growth_ratios_vrednosti[financial_growth[i]["date"]]["dividendPayoutGrowth"] = float(financial_growth[i]["fiveYDividendperShareGrowthPerShare"])

    return growth_ratios_vrednosti


# goodwill
def balance_sheet(company, start_date, end_date, fundamental_data_all):

    #balance_sheet = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?limit={years}&apikey={api_key}')
    #balance_sheet = balance_sheet.json()
    #balance_sheet = list(reversed(balance_sheet))
    #balance_sheet = obdelaj_podatke(balance_sheet)
    balance_sheet = fundamental_data_all[company]["balance_sheet"]
    balance_sheet_vrednosti = {}

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, balance_sheet)
    #print("BALANCE LANSKI", lanski_datum)

    for i in range(len(balance_sheet)):

        #print(balance_sheet[i])
        #print()
        if lanski_datum != "" and datetime.datetime.strptime(balance_sheet[i]["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            balance_sheet_vrednosti[balance_sheet[i]["date"]] = {}
            balance_sheet_vrednosti[balance_sheet[i]["date"]]["goodwill"] = float(balance_sheet[i]["goodwill"])

        ## za obdobje med start in end date
        if datetime.datetime.strptime(balance_sheet[i]["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d")  and datetime.datetime.strptime(balance_sheet[i]["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            balance_sheet_vrednosti[balance_sheet[i]["date"]] = {}
            balance_sheet_vrednosti[balance_sheet[i]["date"]]["goodwill"] = float(balance_sheet[i]["goodwill"])

    return balance_sheet_vrednosti

# discounted cash flow za zadnjih 5 let
def DCF(company, start_date, end_date, fundamental_data_all):

    #discounted_cash_flow = requests.get(f'https://financialmodelingprep.com/api/v3/historical-discounted-cash-flow-statement/{company}?limit={years}&apikey={api_key}')
    #discounted_cash_flow = discounted_cash_flow.json()
    #discounted_cash_flow = list(reversed(discounted_cash_flow))
    #discounted_cash_flow = obdelaj_podatke(discounted_cash_flow)
    discounted_cash_flow = fundamental_data_all[company]["discounted_cash_flow"]
    discounted_cash_flow_vrednosti = {}

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, discounted_cash_flow)
    #print("DCF lanski", lanski_datum)
    #print(keys)

    for i in range(len(discounted_cash_flow)):

        #print(balance_sheet[i])
        #print()
        if lanski_datum != "" and datetime.datetime.strptime(discounted_cash_flow[i]["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            if discounted_cash_flow[i]["dcf"] is not None:

                discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]] = {}
                if discounted_cash_flow[i]["dcf"] == "":
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["dcf"] = 0
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["price"] = 0
                else:
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["dcf"] = float(discounted_cash_flow[i]["dcf"])
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["price"] = float(discounted_cash_flow[i]["price"])


        ## za obdobje med start in end date
        if datetime.datetime.strptime(discounted_cash_flow[i]["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d") and datetime.datetime.strptime(discounted_cash_flow[i]["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            if discounted_cash_flow[i]["dcf"] is not None:

                discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]] = {}
                if discounted_cash_flow[i]["dcf"] == "":
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["dcf"] = 0
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["price"] = 0
                else:
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["dcf"] = float(discounted_cash_flow[i]["dcf"])
                    discounted_cash_flow_vrednosti[discounted_cash_flow[i]["date"]]["price"] = float(discounted_cash_flow[i]["price"])

    return discounted_cash_flow_vrednosti


# starost podjetja ipo-date
def company_profile(company, fundamental_data_all):

    #company_profile = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{company}?limit={years}&apikey={api_key}')
    #company_profile = company_profile.json()
    # company_profile = list(reversed(company_profile))
    company_profile_values = {}
    company_profile_values["ipoDate"] = fundamental_data_all[company]["company_profile"][0]["ipoDate"]
    company_profile_values["sector"] = fundamental_data_all[company]["company_profile"][0]["sector"]

    return company_profile_values

# market cap, stock price
def enterprise_value(company, start_date, end_date, fundamental_data_all):

    #enterprise_value = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-values/{company}?limit={years}&apikey={api_key}')
    #enterprise_value = enterprise_value.json()
    #enterprise_value = list(reversed(enterprise_value))
    #enterprise_value = obdelaj_podatke(enterprise_value)
    enterprise_value = fundamental_data_all[company]["enterprise_value"]
    enterprise_value_vrednosti = {}

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, enterprise_value)

    for i in range(len(enterprise_value)):

        #print(balance_sheet[i])
        #print()
        if lanski_datum != "" and datetime.datetime.strptime(enterprise_value[i]["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            enterprise_value_vrednosti[enterprise_value[i]["date"]] = {}
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["stockPrice"] = float(enterprise_value[i]["stockPrice"])
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["numberOfShares"] = float(enterprise_value[i]["numberOfShares"])
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["marketCapitalization"] = float(enterprise_value[i]["marketCapitalization"])


        ## za obdobje med start in end date
        if datetime.datetime.strptime(enterprise_value[i]["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d") and datetime.datetime.strptime(enterprise_value[i]["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            enterprise_value_vrednosti[enterprise_value[i]["date"]] = {}
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["stockPrice"] = float(enterprise_value[i]["stockPrice"])
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["numberOfShares"] = float(enterprise_value[i]["numberOfShares"])
            enterprise_value_vrednosti[enterprise_value[i]["date"]]["marketCapitalization"] = float(enterprise_value[i]["marketCapitalization"])

    return enterprise_value_vrednosti



# revenue
def income_statement(company, start_date, end_date, fundamental_data_all):

    #income_statement = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?limit={years}&apikey={api_key}')
    #income_statement = income_statement.json()
    #income_statement = list(reversed(income_statement))
    #income_statement = obdelaj_podatke(income_statement)
    income_statement = fundamental_data_all[company]["income_statement"]
    income_statement_vrednosti = {}

    lanski_datum = ""
    if company != "DOW":
        lanski_datum = pridobiLanskiDatum(start_date, end_date, income_statement)

    for i in range(len(income_statement)):

        #print(balance_sheet[i])
        #print()
        if lanski_datum != "" and datetime.datetime.strptime(income_statement[i]["date"], "%Y-%m-%d") == datetime.datetime.strptime(lanski_datum, "%Y-%m-%d"):

            income_statement_vrednosti[income_statement[i]["date"]] = {}
            income_statement_vrednosti[income_statement[i]["date"]]["revenue"] = float(income_statement[i]["revenue"])


        ## za obdobje med start in end date
        if datetime.datetime.strptime(income_statement[i]["date"], "%Y-%m-%d") >= datetime.datetime.strptime(start_date, "%Y-%m-%d") and datetime.datetime.strptime(income_statement[i]["date"], "%Y-%m-%d")  <= datetime.datetime.strptime(end_date, "%Y-%m-%d"):

            income_statement_vrednosti[income_statement[i]["date"]] = {}
            income_statement_vrednosti[income_statement[i]["date"]]["revenue"] = float(income_statement[i]["revenue"])

    return income_statement_vrednosti


def zmanjsajObsegPodatkov(data):

    return_data = []
    for x in data:

        if datetime.datetime.strptime(x["date"], "%Y-%m-%d") >= datetime.datetime.strptime("1997-10-10", "%Y-%m-%d"):
            return_data.append(x)

    return return_data

# samo za dividende
def doDividendeAPIcalls(company):

    slovar_podjetja = {}

    financial_ratios = requests.get(f'https://financialmodelingprep.com/api/v3/financial-ratios/{company}?apikey={api_key}')
    company_profile = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{company}?apikey={api_key}')
    discounted_cash_flow = requests.get(f'https://financialmodelingprep.com/api/v3/historical-discounted-cash-flow-statement/{company}?apikey={api_key}')
    financial_growth = requests.get(f"https://financialmodelingprep.com/api/v3/financial-growth/{company}?apikey={api_key}")


    # financials
    financial_ratios = financial_ratios.json()
    ratios = financial_ratios["ratios"]
    ratios = zmanjsajObsegPodatkov(ratios)  # skrajsaj
    ratios = list(reversed(ratios))
    ratios = obdelaj_podatke(ratios)
    slovar_podjetja["financial_ratios"] = ratios

    # company profile
    company_profile = company_profile.json()
    slovar_podjetja["company_profile"] = company_profile

    # discounted cash flow
    discounted_cash_flow = discounted_cash_flow.json()
    discounted_cash_flow = zmanjsajObsegPodatkov(discounted_cash_flow)  # skrajsaj
    discounted_cash_flow = list(reversed(discounted_cash_flow))
    discounted_cash_flow = obdelaj_podatke(discounted_cash_flow)
    slovar_podjetja["discounted_cash_flow"] = discounted_cash_flow

    # financial growth
    financial_growth = financial_growth.json()
    financial_growth = zmanjsajObsegPodatkov(financial_growth)  # skrajsaj
    financial_growth = list(reversed(financial_growth))
    financial_growth = obdelaj_podatke(financial_growth)
    slovar_podjetja["financial_growth"] = financial_growth

    return slovar_podjetja

# samo za pe in pb
def doPEinPBAPIcalls(company):

    slovar_podjetja = {}

    financial_ratios = requests.get(f'https://financialmodelingprep.com/api/v3/financial-ratios/{company}?limit={years}&apikey={api_key}')
    company_profile = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{company}?limit={years}&apikey={api_key}')

    # financials
    financial_ratios = financial_ratios.json()
    ratios = financial_ratios["ratios"]
    ratios = zmanjsajObsegPodatkov(ratios)  # skrajsaj
    ratios = list(reversed(ratios))
    ratios = obdelaj_podatke(ratios)
    slovar_podjetja["financial_ratios"] = ratios

    # company profile
    company_profile = company_profile.json()
    slovar_podjetja["company_profile"] = company_profile

    return slovar_podjetja

# vrne slovar kjer so vsi podatki za neko podjetje
def doAllAPIcalls(company):

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
    ratios = zmanjsajObsegPodatkov(ratios)  # skrajsaj
    ratios = list(reversed(ratios))
    ratios = obdelaj_podatke(ratios)
    slovar_podjetja["financial_ratios"] = ratios

    # balance sheet
    balance_sheet = balance_sheet.json()
    balance_sheet = zmanjsajObsegPodatkov(balance_sheet)  # skrajsaj
    balance_sheet = list(reversed(balance_sheet))
    balance_sheet = obdelaj_podatke(balance_sheet)
    slovar_podjetja["balance_sheet"] = balance_sheet

    # discounted cash flow
    discounted_cash_flow = discounted_cash_flow.json()
    discounted_cash_flow = zmanjsajObsegPodatkov(discounted_cash_flow)  # skrajsaj
    discounted_cash_flow = list(reversed(discounted_cash_flow))
    discounted_cash_flow = obdelaj_podatke(discounted_cash_flow)
    slovar_podjetja["discounted_cash_flow"] = discounted_cash_flow

    # company profile
    company_profile = company_profile.json()
    slovar_podjetja["company_profile"] = company_profile

    # enterprise value
    enterprise_value = enterprise_value.json()
    enterprise_value = zmanjsajObsegPodatkov(enterprise_value)  # skrajsaj
    enterprise_value = list(reversed(enterprise_value))
    enterprise_value = obdelaj_podatke(enterprise_value)
    slovar_podjetja["enterprise_value"] = enterprise_value

    # income statement
    income_statement = income_statement.json()
    income_statement = zmanjsajObsegPodatkov(income_statement)  # skrajsaj
    income_statement = list(reversed(income_statement))
    income_statement = obdelaj_podatke(income_statement)
    slovar_podjetja["income_statement"] = income_statement

    return slovar_podjetja

def pridobiZapisIstegaLeta(x, vir):

    leto = datetime.datetime.strptime(x, "%Y-%m-%d").year

    for y in vir:

        if datetime.datetime.strptime(y, "%Y-%m-%d").year == leto: # zapisa istega leta
            return y

    return -111

def getBeforeData(company, start_date, end_date, fundamentals):

    financial_data = financial_ratios(company, start_date, end_date, fundamentals)
    company_age_sector = company_profile(company, fundamentals)
    dfc_data = DCF(company, start_date, end_date, fundamentals)

    #print(dfc_data)
    #print("Podejteje: ", company)
    for x in financial_data:
        #print("samo before dividende X je: ", x)
        age = abs((datetime.datetime.strptime(x, "%Y-%m-%d") - datetime.datetime.strptime(company_age_sector["ipoDate"], "%Y-%m-%d")).days)
        #print("COMPANY AGE", int(age / 364))
        financial_data[x]["company_age"] = int(age / 364)
        financial_data[x]["sector"] = company_age_sector["sector"]
        financial_data[x].update(dfc_data[pridobiZapisIstegaLeta(x, dfc_data)])
        financial_data[x]["dividendPerShare"] = financial_data[x]["dividendYield"] * financial_data[x]["price"]

    print(f"start: {start_date}, end: {end_date}")
    print(list(financial_data.keys()))
    if datetime.datetime.strptime(list(financial_data.keys())[-1], "%Y-%m-%d").year == datetime.datetime.strptime(end_date, "%Y-%m-%d").year:
        del financial_data[list(financial_data.keys())[-1]]

    return financial_data

# podatki samo o dividendah
def getDataCompanySamoDividende(company, start_date, end_date, fundamentals):

    #print("Zacetek za podjetje: ", company)
    #print("Zacetni datum original: ", start_date)
    start_years_ago = datetime.datetime.strptime(start_date, "%Y-%m-%d") - relativedelta(years=5) # start_date spremenimo tako da mu odstejemo 5 let
    #print("Zacetni datum - 4 leta: ", start_years_ago)

    start_years_ago = datetime.datetime.strftime(start_years_ago, "%Y-%m-%d") # nato ga spremenimo nazaj v string
    before_data = {}
    if company != "DOW":
        before_data = getBeforeData(company, start_years_ago, start_date, fundamentals)
    #print("Before data")
    #printData(before_data)
    #print("end before data")

    financial_data = financial_ratios(company, start_date, end_date, fundamentals)
    company_age_sector = company_profile(company, fundamentals)
    dfc_data = DCF(company, start_date, end_date, fundamentals)
    # financial_growth = fGrowth(company, start_date, end_date, fundamentals)

    printData(financial_data)
    #print()
    #print(company_age_sector)
    #print()

    before_keys = list(before_data.keys())
    for x in financial_data:
        # print("samo dividende X je: ", x)
        age = abs((datetime.datetime.strptime(x, "%Y-%m-%d") - datetime.datetime.strptime(company_age_sector["ipoDate"], "%Y-%m-%d")).days)
        #print("COMPANY AGE", int(age / 364))
        financial_data[x]["company_age"] = int(age / 364)
        financial_data[x]["sector"] = company_age_sector["sector"]
        financial_data[x].update(dfc_data[pridobiZapisIstegaLeta(x, dfc_data)])
        financial_data[x]["dividendPerShare"] = financial_data[x]["dividendYield"] * financial_data[x]["price"]

    before_data.update(financial_data)
    updated_before = before_data
    #print("updated before")
    #printData(updated_before)
    #print("updated end")

    for x in updated_before:

        if x in financial_data: # gledamo samo datume, za katere racunamo speravi od start date naprej

            financial_data[x]["dividendPayoutGrowth"] = 0 # default vrednost
            five_ago = datetime.datetime.strptime(x, "%Y-%m-%d") - relativedelta(years=5)
            #print("racunam stiri za nazaj", five_ago)
            #print("Zacel racunat za: ", x)

            check = 0
            keys = list(updated_before.keys())
            payoutGrowth = 0
            for i in range(len(updated_before)):

                if check == 1: # sestevamo vse eno letne rasti

                    if updated_before[keys[i]]["dividendPerShare"] != 0 and updated_before[keys[i - 1]]["dividendPerShare"] != 0:

                        currPayoutGrowth = updated_before[keys[i]]["dividendPerShare"] / updated_before[keys[i - 1]]["dividendPerShare"]
                        #print("Enoletna rast: ", currPayoutGrowth - 1)
                        payoutGrowth += currPayoutGrowth - 1

                    if keys[i] == x:  # pridemo do leta za katero racunamo

                        avgPayoutGrowth = payoutGrowth / 5
                        #print("sestevek rasti: ", payoutGrowth)
                        #print("avg rasti: ", avgPayoutGrowth)
                        financial_data[x]["dividendPayoutGrowth"] = avgPayoutGrowth
                        payoutGrowth = 0
                        check = 0
                        #print("Zracunal za leto: ", x)
                        break

                #print(f"prvi: {keys[i]} drugi: {five_ago}, rez: {keys[i] == five_ago}")
                #print()
                if datetime.datetime.strptime(keys[i], "%Y-%m-%d").year == five_ago.year:
                    #print("check bo 1 za leto", x)
                    check = 1 # od tu naprej racunam


    return_data = {}
    # pretvorimo se v datume, ki predstavljajo delovne dni
    for datum in financial_data:

        delovni_date = to_week_day(datetime.datetime.strptime(datum, "%Y-%m-%d"))
        return_data[delovni_date] = {}
        return_data[delovni_date] = financial_data[datum]

    return return_data

# pridobi samo financial data in company age in sector
def getDataCompanySamoPEinPB(company, start_date, end_date, fundamentals):

    financial_data = financial_ratios(company, start_date, end_date, fundamentals)
    company_age_sector = company_profile(company, fundamentals)

    printData(financial_data)
    print()
    print(company_age_sector)
    print()

    for x in financial_data:
        print("samo pepb X je: ", x)
        age = abs((datetime.datetime.strptime(x, "%Y-%m-%d") - datetime.datetime.strptime(company_age_sector["ipoDate"], "%Y-%m-%d")).days)
        #print("COMPANY AGE", int(age / 364))
        financial_data[x]["company_age"] = int(age / 364)
        financial_data[x]["sector"] = company_age_sector["sector"]

    return_data = {}
    # pretvorimo se v datume, ki predstavljajo delovne dni
    for datum in financial_data:

        delovni_date = to_week_day(datetime.datetime.strptime(datum, "%Y-%m-%d"))
        return_data[delovni_date] = {}
        return_data[delovni_date] = financial_data[datum]

    return return_data


def getDataCompany(company, start_date, end_date, fundamentals, prilagodiDatum):

    data = balance_sheet(company, start_date, end_date, fundamentals)

    data_keys = data.keys()
    # print("KEYS: ", data_keys)

    financial_data = financial_ratios(company, start_date, end_date, fundamentals)

    dfc_data = DCF(company, start_date, end_date, fundamentals)

    company_age_sector = company_profile(company, fundamentals)

    enterprise_data = enterprise_value(company, start_date, end_date, fundamentals)

    income_data = income_statement(company, start_date, end_date, fundamentals)

    # TODO naredi se za 5 let nazaj profit margin in ROE

    """
    printData(data)
    print()
    printData(financial_data)
    print()
    printData(dfc_data)
    print()
    print(company_age_sector)
    print()
    printData(enterprise_data)
    print()
    printData(income_data)
    
    """

    for x in data:
        #print(f"updejtanje {company} X je: ", x)
        data[x].update(financial_data[pridobiZapisIstegaLeta(x, financial_data)])
        data[x].update(dfc_data[pridobiZapisIstegaLeta(x, dfc_data)])
        data[x].update(enterprise_data[pridobiZapisIstegaLeta(x, enterprise_data)])
        data[x].update(income_data[pridobiZapisIstegaLeta(x, income_data)])
        age = abs((datetime.datetime.strptime(x, "%Y-%m-%d") - datetime.datetime.strptime(company_age_sector["ipoDate"], "%Y-%m-%d")).days)
        #print("COMPANY AGE", int(age / 364))
        data[x]["company_age"] = int(age / 364)
        data[x]["sector"] = company_age_sector["sector"]

    #print()
    #print("Before:")
    #printData(data)
    #print()
    return_data = {}

    # pretvorimo se v datume, ki predstavljajo delovne dni, za normalen klic, za izracn avg pa ne
    if prilagodiDatum == True:
        for datum in data:

            delovni_date = to_week_day(datetime.datetime.strptime(datum, "%Y-%m-%d"))
            return_data[delovni_date] = {}
            return_data[delovni_date] = data[datum]
        return return_data
    else:
        return data

def printData(data):

    for x in data:
        print(x)
        print(data[x])
        print()

def getDataAllEverPEinPB(allCompanies):

    data = {}
    count = 0
    for x in allCompanies:

        data[x] = doPEinPBAPIcalls(x)
        count += 1
        print(f"DOWNLOADED data for {x}. {count}/{len(allCompanies)}")

    return data

def getDataAllEverDividende(allCompanies):

    data = {}
    count = 0
    for x in allCompanies:

        data[x] = doDividendeAPIcalls(x)
        count += 1
        print(f"DOWNLOADED data for {x}. {count}/{len(allCompanies)}")

    return data

def getDataAllEver(allCompanies):

    data = {}
    count = 0
    for x in allCompanies:

        data[x] = doAllAPIcalls(x)
        count += 1
        print(f"DOWNLOADED data for {x}. {count}/{len(allCompanies)}")

    return data

def printAll(list, start_date, end_date):

    for company in testni_all:

        print(company)
        company_data = getDataCompany(company, start_date, end_date)
        printData(company_data)
        print()

# za pridobit vse fundamentalne podatke vseh 44 podjetji
def getAllFundamentals(seznam_tickerjev):

    fundamental_data = getDataAllEver(seznam_tickerjev)

    return fundamental_data

def avgAllFundamentalsObdobja(zacento_obdobje, koncno_obdobje, fundamentals, company_list):

    # ROE, goodwill, revenue avg za usa podjejta
    index_avg = {}
    #print("V avg fundamentals")

    od = datetime.datetime.strptime(zacento_obdobje, "%Y-%m-%d").year
    do = datetime.datetime.strptime(koncno_obdobje, "%Y-%m-%d").year

    #print(f"prej OD: {od} , DO: {do}")

    #if od == do:  # ce je slucajno isto leto
     #   do += 1
    #print(f"pol OD: {od} , DO: {do}")
    # prej je blo tko: for x in range(od - 1, do + 1):
    od = od - 1
    do = do + 1

    # naredimo slovar za vsako leto
    for x in range(od, do):
        #print(datetime.datetime.strptime(str(x), "%Y").year)
        index_avg[str(x)] = {}
        index_avg[str(x)]["avgROE"] = 0
        index_avg[str(x)]["avgProfitMargin"] = 0
        index_avg[str(x)]["avgGoodwill"] = 0
        index_avg[str(x)]["avgRevenue"] = 0
        #print(index_avg[str(x)])

    for company in company_list:

        if company != "GM":
            #print(f"ZACENJAM AVG ZA {company}")
            if zacento_obdobje == "2005-11-21":
                zacento_obdobje = "2004-11-21"
            company_data = getDataCompany(company, zacento_obdobje, koncno_obdobje, fundamentals, False)
            #printData(company_data)

            for datum in company_data:

                leto = datetime.datetime.strptime(datum, "%Y-%m-%d").year
                #print("LETO je: ", leto)
                if leto >= od:
                    #print(f"LETO notri je {leto} company je {company} ")
                    index_avg[str(leto)]["avgROE"] += company_data[datum]["ROE"]
                    index_avg[str(leto)]["avgProfitMargin"] += company_data[datum]["profitMargin"]
                    index_avg[str(leto)]["avgGoodwill"] += company_data[datum]["goodwill"]
                    index_avg[str(leto)]["avgRevenue"] += company_data[datum]["revenue"]

    # delimo z 30 da dobimo povprecje
    for x in index_avg:

        # dodamo popravek ker GM  nimamo not
        if x in ["2004", "2005", "2006", "2007", "2008"]:
            print(f"Delim samo z 29, x: {x} ")
            index_avg[x]["avgROE"] /= 29
            index_avg[x]["avgProfitMargin"] /= 29
            index_avg[x]["avgGoodwill"] /= 29
            index_avg[x]["avgRevenue"] /= 29
        else:
            index_avg[x]["avgROE"] /= 30
            index_avg[x]["avgProfitMargin"] /= 30
            index_avg[x]["avgGoodwill"] /= 30
            index_avg[x]["avgRevenue"] /= 30

    return index_avg


#start = "2007"
#start = "2005-11-21"
#end = "2008-2-19"


#fundamental_data = getAllFundamentals(testni_all)
#avg_data = avgAllFundamentalsObdobja(start, end, fundamental_data)
#printData(avg_data)



#end = "2020-11-21"
#end = "2020-11-21"
# printAll(testni_all,start,end)
#start = "2019-4-2"
#end = "2020-10-1"

"""
begin_time = datetime.datetime.now()
fundamental_data = getDataAllEverDividende(vsi_tickerji)
#company_data = getDataCompanySamoPEinPB("DIS", start, end, fundamental_data)
for x in fundamental_data:
    print("Podjetje je: ", x)
    company_data = getDataCompanySamoDividende(x, start, end, fundamental_data)
    print("Rezultati:")
    printData(company_data)

print(datetime.datetime.now() - begin_time)

"""
#company = "DOW"

#company_data = getDataCompany("MSFT", start, end)
#begin_time = datetime.datetime.now()
#fundamental_data = getDataAllEver(["DIS"])
#print(datetime.datetime.now() - begin_time)
#company_data = getDataCompany("DIS", start, end, fundamental_data)
#printData(company_data)

"""
fundamental_data = getDataAllEver(testni_all)

for x in fundamental_data:
    print("Podjetje je: ", x)
    company_data = getDataCompany(x, start, end, fundamental_data)
    printData(company_data)
"""
#print(fundamental_data)
#print(datetime.datetime.now() - begin_time)

#print()
#printData(company_data)







