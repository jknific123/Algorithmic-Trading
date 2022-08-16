import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from stock_fundamental_data import fundamental_indicators_to_csv as fundamentalToCsv


class StockFundamentalData:

    vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS', 'GE', 'GM',
                    'GS', 'HD', 'HON', 'HPQ', "AA", 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',  # 'HWM' -> "AA"
                    'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']

    vse_industrije = {'Technology': ['AAPL', 'CRM', 'CSCO', 'HPQ', 'IBM', 'INTC', 'MSFT'],
                      'Financial Services': ['AIG', 'AXP', 'BAC', 'C', 'GS', 'JPM', 'TRV', 'V'],
                      'Healthcare': ['AMGN', 'JNJ', 'MRK', 'PFE', 'UNH', 'WBA'],
                      'Industrials': ['BA', 'CAT', 'GE', 'HON', 'AA', 'MMM', 'RTX'],
                      'Energy': ['CVX', 'XOM'],
                      'Basic Materials': ['DD', 'DOW'],
                      'Communication Services': ['DIS', 'T', 'VZ'],
                      'Consumer Cyclical': ['GM', 'HD', 'MCD', 'NKE'],
                      'Consumer Defensive': ['KO', 'MDLZ', 'MO', 'PG', 'WMT']}

    fundamental_trading_dates = ['2005-06-30', '2006-06-30', '2007-06-29', '2008-06-30', '2009-06-30', '2010-06-30', '2011-06-30', '2012-06-29',
                                 '2013-06-28', '2014-06-30', '2015-06-30', '2016-06-30', '2017-06-30', '2018-06-29', '2019-06-28', '2020-06-30', '2021-06-30',
                                 '2017-02-02', '2018-09-10', '2020-04-16']  # zadnji trije so zacetki testnih mnozic

    stock_fundamental_data = {}
    stock_average_fundamental_data = {}
    stock_industries_average_fundamental_data = {}

    def __init__(self):
        print('Inicializacija objekta StockFundamentalData')
        # fundamentalToCsv.getAllFundamentalDAtaFromAPIsToCsv()  # rabimo samo v primeru ko je treba downloadat fundamentalne indikatorje
        StockFundamentalData.readFundamentalDataCsvToDictOfDicts(self)
        StockFundamentalData.readAvgFundamentalDataCsvToDict(self)
        StockFundamentalData.readIndustiresAvgFundamentalDataCsvToDict(self)
        print('Inicializacija končana!')

    def preveriPrimernostDCF(self):
        for company in self.stock_fundamental_data:
            company_data = self.stock_fundamental_data[company]
            for zapis in company_data:
                if datetime.strptime(zapis, '%Y-%m-%d').year >= 2004:
                    if self.stock_fundamental_data[company][zapis]['dcf'] < self.stock_fundamental_data[company][zapis]['price']:
                        print('Nasel ok DCF za podjetje: ', company, 'zapis: ', zapis, 'DCF: ', self.stock_fundamental_data[company][zapis]['dcf'], 'price: ', self.stock_fundamental_data[company][zapis]['price'])

    def dobiVseIndustrije(self):
        slovar_industrij = {}
        for company in self.stock_fundamental_data:
            company_data = self.stock_fundamental_data[company]
            for zapis in company_data:
                industrija = company_data[zapis]['sector']
                slovar_industrij[industrija] = 1
                if company not in self.vse_industrije[industrija]:
                    self.vse_industrije[industrija].append(company)

        return slovar_industrij

    # Metoda vrne slovar slovarjev, ki vsebujejo fundamentalne indikatorje podjetji
    def getAllStockFundamentalData(self):
        return self.stock_fundamental_data

    # Metoda za pridobitev slovarja fundamentalnih indikatorjev za določeno podjetje
    def getCompanyFundamentalData(self, companyTicker):
        return self.stock_fundamental_data[companyTicker]

    # Metoda za pridobitev slovarja pravilnega letnega porocila fundamentalnih indikatorjev za določeno podjetje
    def getCompanyFundamentalDataForDate(self, companyTicker, datum):
        dict_podjetja = self.stock_fundamental_data[companyTicker]
        iskano_letno_porocilo_in_njegov_datum = {}
        for x in dict_podjetja:
            if datetime.strptime(x, '%Y-%m-%d') <= datetime.strptime(datum, '%Y-%m-%d'):
                iskano_letno_porocilo_in_njegov_datum['datum'] = x
                iskano_letno_porocilo_in_njegov_datum['porocilo'] = dict_podjetja[x]

        return iskano_letno_porocilo_in_njegov_datum

    # Metoda za pridobitev slovarja pravilnega letnega porocila fundamentalnih indikatorjev za določeno podjetje za določen razpon let
    def getCompanyFundamentalDataForPeriodOfYears(self, companyTicker, datum, razpon_let):
        dict_podjetja = self.stock_fundamental_data[companyTicker]
        period_dict = {}
        start_year = datetime.strptime(datum, '%Y-%m-%d').year - razpon_let
        for x in dict_podjetja:
            if start_year <= datetime.strptime(x, '%Y-%m-%d').year <= datetime.strptime(datum, '%Y-%m-%d').year:
                period_dict[x] = dict_podjetja[x]

        return period_dict

    # Metoda za pridobitev slovarja pravilnega povprecja fundamentalnih indikatorjev za določeno leto
    def getAvgFundamentalDataForYear(self, leto):
        return self.stock_average_fundamental_data[leto]

    # Metoda za pridobitev slovarja pravilnega povprecja fundamentalnih indikatorjev za industrijo za določeno leto
    def getAvgIndustryFundamentalDataForYear(self, industrija, leto):
        return self.stock_industries_average_fundamental_data[industrija][leto]

    # Metoda za pridobitev slovarja pravilnega povprecja fundamentalnih indikatorjev za industrijo za določen razpon let
    def getAvgIndustryFundamentalDataForPeriodOfYears(self, industrija, leto, razpon_let):
        period_dict = {}
        start_year = leto - razpon_let
        vsa_leta = list(self.stock_industries_average_fundamental_data[industrija].keys())
        for period_year in vsa_leta:
            if start_year <= period_year <= leto:
                period_dict[period_year] = self.stock_industries_average_fundamental_data[industrija][period_year]

        return period_dict

    # vrne list datumov ki so kljuci slovarja fundamentalnih indikatorjev podjetja
    def getListOfDatesOfCompanyDataDict(self, ticker):
        return list(self.stock_fundamental_data[ticker].keys())

    """ Branje podatkov iz .csv datotek """

    # Metoda za branje podatkov iz .csv datotek v slovar slovarjev, key je ticker, value je slovar podatkov po letih
    def readFundamentalDataCsvToDictOfDicts(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\stock_fundamental_data\/raw_fundamental_data_modified')

        # find the files; this is a generator, not a list
        files = p.glob('fundamental_data_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmpFileName = os.path.basename(file)
            tmpSplitArgs = tmpFileName.split('_')
            tmpSplitDotArgs = tmpSplitArgs[2].split('.')
            tmp_company_df = pd.read_csv(file, index_col=[0])
            self.stock_fundamental_data[tmpSplitDotArgs[0]] = tmp_company_df.to_dict(orient='index')

    # Metoda za branje podatkov iz .csv datotek v dataframe, ki so shranjeni v slovarju objekta
    def readAvgFundamentalDataCsvToDict(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\stock_fundamental_data\/raw_fundamental_average_data')

        # find the files; this is a generator, not a list
        files = p.glob('fundamental_data_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmp_avg_df = pd.read_csv(file, index_col=[0])
            self.stock_average_fundamental_data = tmp_avg_df.to_dict(orient='index')

    # Metoda za branje podatkov iz .csv datotek v dataframe, ki so shranjeni v slovarju objekta
    def readIndustiresAvgFundamentalDataCsvToDict(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\stock_fundamental_data\/raw_industries_average_data')

        # find the files; this is a generator, not a list
        files = p.glob('fundamental_data_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmpFileName = os.path.basename(file)
            tmpSplitArgs = tmpFileName.split('_')
            tmpSplitDotArgs = tmpSplitArgs[2].split('.')
            tmp_industry_df = pd.read_csv(file, index_col=[0])
            self.stock_industries_average_fundamental_data[tmpSplitDotArgs[0]] = tmp_industry_df.to_dict(orient='index')