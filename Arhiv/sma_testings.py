import pandas as pd
import datetime as datetime
import numpy as np
from IPython.core.display import display

from stock_ohlc_data import get_stock_data as getStocks

range1 = pd.date_range('2005-11-21', '2016-5-21')
# range2 = pd.date_range('2021-10-6','2021-10-11')

# range1 = ["2021-10-01", "2021-10-02", "2021-11-03", "2021-10-04"]
# range2 = ["2021-10-01", "2021-10-02", "2021-10-04", "2021-10-03", "2021-10-04", "2021-10-04"]

dictToDf = {'Date': ["2021-10-01", "2021-10-02", "2021-10-04", "2021-10-03", "2021-10-04", "2021-10-04"],
            'value': [1, 1, 1, 1, 1, 1],
            'apple': [1, 1, 1, 1, 1, 1],
            'orange': [1, 1, 1, 1, 1, 1]}

df1 = pd.DataFrame(data=dictToDf)
# df2 = pd.DataFrame(1, columns=['value', 'apple', 'orange'], index=range2)

display(df1)
# print('df1: ', df1)
print()
# print()
# print('df2: ', df2)


begin_time = datetime.datetime.now()
print('testing itteration: ')
counter = 0
for i in range(0, 30):
    for x in range(0, len(df1)):
        # print(df1['value'].iat[x])
        df1['value'].iat[x] = df1['value'].iat[x] + df1['apple'].iat[x]
        counter += 1
print(counter)
print(datetime.datetime.now() - begin_time)

print('testing itteration drugacen dostop: ')
begin_time10 = datetime.datetime.now()
counter10 = 0
for k in range(0, 30):
    for x in range(0, len(df1)):
        # print(df1['value'].iat[x])
        df1['value'].to_numpy()[x] = df1['value'].to_numpy()[x] + df1['apple'].to_numpy()[x]
        counter10 += 1
print(counter10)
print(datetime.datetime.now() - begin_time10)

print('testiram itterrows')
begin_time2 = datetime.datetime.now()
counter = 0
for i in range(0, 30):
    for index, row in df1.iterrows():
        row['value'] = row['value'] + row['apple']
        counter += 1  # print(row['value'])
print(counter)
print(datetime.datetime.now() - begin_time2)

print('testiram dict loop')
begin_time3 = datetime.datetime.now()
counter = 0
tmp_dict = df1.to_dict('records')
for i in range(0, 30):
    for r in tmp_dict:
        r['value'] = r['value'] + r['apple']
        counter += 1

print(counter)
print(datetime.datetime.now() - begin_time3)





# stocksDB = getStocks.StockOHLCData()
#
# testDF = stocksDB.getCompanyStockDataInRangeTabela("2005-11-21", "2005-11-28", "AAPL")
# print()
# display(testDF)

# preveriPravilnostDatumov(df1)
