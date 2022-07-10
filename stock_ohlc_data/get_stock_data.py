import os
from pathlib import Path
import pandas as pd
import yfinance as yf
import datetime as datetime
pd.options.mode.chained_assignment = None  # default='warn'


class StockOHLCData:
    vsi_tickerji = ['AAPL', 'AIG', 'AMGN', 'AXP', 'BA', 'BAC', 'C', 'CAT', 'CRM', 'CSCO', 'CVX', 'DD', 'DOW', 'DIS', 'GE', 'GM',
                    'GS', 'HD', 'HON', 'HPQ', "AA", 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MDLZ', 'MMM', 'MO', 'MRK', 'MSFT',  # 'HWM' -> "AA" ->
                    'NKE', 'PFE', 'PG', 'RTX', 'T', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT', 'XOM']

    stock_prices_data = {}

    def __init__(self):
        print('Inicializacija objekta StockOHLCData')
        # StockOHLCData.downloadAllStockDataToCsv(self)  # rabimo samo v primeru ko je treba downloadat cene delnic
        StockOHLCData.readCsvToDataFrame(self)
        print('Inicializacija končana!')

    # Metoda vrne slovar datafrejmov, ki vsebujejo cene delnic podjetji
    def getAllStockData(self):
        return StockOHLCData.stock_prices_data

    # Metoda za downloadanje cen delnic iz yfinance API-ja
    def getAllStockDataFromAPI(self, start_date, end_date):
        data = {}
        count = 0
        for x in StockOHLCData.vsi_tickerji:

            if x == "DOW":
                temp_start_date = '2019-03-20'
                temp_data = yf.download(x, start=temp_start_date, end=end_date, progress=False)  # downloadam podatke za doticno podjetje in jih shranim v slovar
            else:
                temp_data = yf.download(x, start=start_date, end=end_date, progress=False)  # downloadam podatke za doticno podjetje in jih shranim v slovar,

            temp_data = temp_data[["High", "Low", "Close", "Adj Close"]].copy()  # da vzamemo samo ceno
            data[x] = temp_data

            count += 1
            print(f"DOWNLOADED stock data for {x}. {count}/{len(StockOHLCData.vsi_tickerji)}")

        return data

    # Metoda za pridobitev dataframa (cene delnic) v določenem obdobju - datum je index
    def getCompanyStockDataInRange(self, date_from, date_to, companyTicker):
        return_dataframe = pd.DataFrame
        # startTime = datetime.datetime.now()
        # print("date_from type: ", type(date_from))
        # print("date_to type: ", type(date_to))
        # print("date from: ", date_from)
        # print("date to: ", date_to)
        return_dataframe = self.stock_prices_data[companyTicker].loc[date_from:date_to]
        # print("Čas getCompanyStockDataInRange", datetime.datetime.now() - startTime)
        return return_dataframe

    # Metoda za pridobitev dataframa (cene delnic) v določenem obdobju – datum je del tabele, index je int
    def getCompanyStockDataInRangeTabela(self, date_from, date_to, companyTicker):
        return_dataframe = pd.DataFrame
        tmpDF = self.stock_prices_data[companyTicker]
        tmpDF["Date"] = pd.to_datetime(tmpDF["Date"])
        mask = (tmpDF["Date"] >= date_from) & (tmpDF["Date"] <= date_to)
        return_dataframe = tmpDF.loc[mask]
        # print("Čas getCompanyStockDataInRange", datetime.datetime.now() - startTime)
        return return_dataframe

    # Metoda za downloadanje cen delnic iz yfinance API-ja, ki se nato shranijo lokalno v .csv datotekah
    def downloadAllStockDataToCsv(self, start_date="2005-02-07", end_date="2022-01-01"):  # start date se spremeni na 2005-02-07, to je 201 delovnih dni pred 2005-11-21
        count = 0
        for ticker in StockOHLCData.vsi_tickerji:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            data.to_csv(f'D:\Faks\Algorithmic-Trading\stock_ohlc_data\/raw_data_ohlc\stock_data_{ticker}.csv')  # \/ je zato ker je tam r in če je samo \r ne dela
            count += 1
            print(f"DOWNLOADED stock data for {ticker}. {count}/{len(StockOHLCData.vsi_tickerji)}")
        print('done downloading csv data!')

    # Metoda za branje podatkov iz .csv datotek v dataframe, ki so shranjeni v slovarju objekta
    def readCsvToDataFrame(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\stock_ohlc_data\/raw_data_ohlc')

        # find the files; this is a generator, not a list
        files = p.glob('stock_data_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmpFileName = os.path.basename(file)
            tmpSplitArgs = tmpFileName.split('_')
            tmpSplitDotArgs = tmpSplitArgs[2].split('.')
            if tmpSplitDotArgs[0] in ['DOW', 'GM', 'V']:
                data = pd.read_csv(file, index_col=[0])
                data = self.dopolniDataZaPodjetje(tmpSplitDotArgs[0], data)
                StockOHLCData.stock_prices_data[tmpSplitDotArgs[0]] = data
            else:
                StockOHLCData.stock_prices_data[tmpSplitDotArgs[0]] = pd.read_csv(file, index_col=[0])

    # Metoda za branje podatkov iz .csv datotek v dataframe, ki so shranjeni v slovarju objekta - datum je del tabele, index je int
    def readCsvToDataFrameTabela(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\stock_ohlc_data\/raw_data_ohlc')

        # find the files; this is a generator, not a list
        files = p.glob('stock_data_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmpFileName = os.path.basename(file)
            tmpSplitArgs = tmpFileName.split('_')
            tmpSplitDotArgs = tmpSplitArgs[2].split('.')
            StockOHLCData.stock_prices_data[tmpSplitDotArgs[0]] = pd.read_csv(file)  # index_col=[0]

    def dopolniDataZaPodjetje(self, ticker, data):
        if ticker == 'V':
            prazen_df_V = self.getCompanyStockDataInRange('2005-02-07', '2008-03-18', 'AAPL')
            self.dajVrednostStolpcevVDfNaNic(prazen_df_V)
            return pd.concat([prazen_df_V, data])
        elif ticker == 'GM':
            prazen_df_GM = self.getCompanyStockDataInRange('2005-02-07', '2010-11-17', 'AAPL')
            self.dajVrednostStolpcevVDfNaNic(prazen_df_GM)
            return pd.concat([prazen_df_GM, data])
        elif ticker == 'DOW':
            prazen_df_DOW = self.getCompanyStockDataInRange('2005-02-07', '2019-03-19', 'AAPL')
            self.dajVrednostStolpcevVDfNaNic(prazen_df_DOW)
            return pd.concat([prazen_df_DOW, data])

    def dajVrednostStolpcevVDfNaNic(self, df):
        df['Open'] = 0
        df['High'] = 0
        df['Low'] = 0
        df['Close'] = 0
        df['Adj Close'] = 0
        df['Volume'] = 0


    def preveriKateraPodjetjajePotrebnoDostukati(self):
        for company in self.stock_prices_data:
            company_df = self.stock_prices_data[company]
            if company_df.index[0] != '2005-02-07':
                print('Copmany to correct', company)
                print('first date is: ', company_df.index[0])


    def preveriKateraPodjetjajePotrebnoDostukati2(self):
        for company in self.stock_prices_data:
            company_df = self.stock_prices_data[company]
            if '2005-11-21' not in company_df.index:
                print('Copmany to correct', company)
                print('first date is: ', company_df.index[0])


    """
    test_ticker = "HD"
    test_data_ucna = yf.download(test_ticker, start="2005-11-21", end="2021-1-1", progress=False)
    test_data_ucna = test_data_ucna[['Adj Close']].copy()
    
    skrajsan = getCompanyStockDataInRange("2016-5-21", "2020-1-1", test_ticker, test_data_ucna)
    
    skrajsan_yfinance = yf.download(test_ticker, start="2016-5-21", end="2020-1-1", progress=False)
    skrajsan_yfinance = skrajsan_yfinance[['Adj Close']].copy()
    
    print("finito")
    """

