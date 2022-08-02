import os
from pathlib import Path
import pandas as pd
import yfinance as yf
import datetime as datetime
from dow_index_data import dow_jones_index_data_csv as dowIndexData
from stock_ohlc_data import get_stock_data as getStocks
import generate_time_lines as generateTL
pd.options.mode.chained_assignment = None  # default='warn'


class TimeLinesData:

    time_lines = {}

    def __init__(self):
        print('Inicializacija objekta TimeLinesData')
        # TimeLinesData.createTimeLines(self)
        # StockOHLCData.downloadAllStockDataToCsv(self)  # rabimo samo v primeru ko je treba downloadat cene delnic
        TimeLinesData.readCsvTimeLinesToDataFrame(self)
        print('Inicializacija končana!')

    def createTimeLines(self):
        lines_dict = generateTL.backtest(start="2005-11-21", end="2021-11-21", dowTickers=dowIndexData.dowJonesIndexData, stockPricesDB=getStocks.StockOHLCData())
        for line in lines_dict:
            lines_dict[line].to_csv(f'D:\Faks\Algorithmic-Trading\dow_index_time_lines\/time_lines\/time_line_{line}.csv')  # \/ je zato ker je tam r in če je samo \r ne dela

    # Metoda za branje podatkov iz .csv datotek v dataframe, ki so shranjeni v slovarju objekta
    def readCsvTimeLinesToDataFrame(self):
        # set the path to the files
        p = Path('D:\Faks\Algorithmic-Trading\dow_index_time_lines\/time_lines')

        # find the files; this is a generator, not a list
        files = p.glob('time_line_*.csv')
        # read the files into a dictionary of dataframes
        for file in files:
            tmpFileName = os.path.basename(file)
            tmpSplitArgs = tmpFileName.split('_')
            tmpSplitDotArgs = tmpSplitArgs[2].split('.')
            TimeLinesData.time_lines[tmpSplitDotArgs[0]] = pd.read_csv(file, index_col=[0])

    # # Metoda vrne slovar datafrejmov, ki vsebujejo cene delnic podjetji
    # def getAllStockData(self):
    #     return StockOHLCData.stock_prices_data



# TimeLinesData().createTimeLines()
test_df = TimeLinesData().time_lines
print(test_df)