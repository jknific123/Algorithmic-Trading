"""
Tukaj pridobim podatke o dow jones index-u, ki so shranjeni v DowJonesCompaniesData.csv datoteki. Za offline uporabo oz. zato, da se izognemo api klicu.

Podatki so najprej pridobljeni preko api klica iz financialmodelingprep, ter nato obdelani v dow_jones_companies_api.py datoteki nato pa shranjeni na disk
v DowJonesCompaniesData.csv datoteko.
"""

import os
from pathlib import Path

import pandas as pd


def readCsvToDataFrame():
    # set the path to the files
    p = Path(f'D:\Faks\Algorithmic-Trading\dow_index_data')

    # find the files; this is a generator, not a list
    files = p.glob('*.csv')
    # read the files into a dictionary of dataframes
    for file in files:
        tmpFileName = os.path.basename(file)
        if tmpFileName == 'DowJonesCompaniesData.csv':
            return pd.read_csv(file, index_col=[0])


def dataFrameToDictOfDicts(dataframe):
    dictOfDicts = {}

    for i in dataframe:
        # print(i)
        # print(dataframe[i])
        dictOfDicts[i] = {}
        dictOfDicts[i]["removed"] = []
        dictOfDicts[i]["added"] = []
        dictOfDicts[i]["all"] = []

        dictOfDicts[i]["removed"] = urediString(dataframe, i, "removed")
        dictOfDicts[i]["added"] = urediString(dataframe, i, "added")
        dictOfDicts[i]["all"] = urediString(dataframe, i, "all")

    return dictOfDicts


def urediString(df, leto, beseda):
    tmp0 = df[leto][beseda]
    tmp1 = tmp0.replace('[', "")
    tmp2 = tmp1.replace(']', "")
    tmp3 = tmp2.replace('\'', '')
    tmp4 = tmp3.replace(' ', '')
    tmp5 = tmp4.split(',')
    # print(tmp5)

    return tmp5


dowJonesIndexData = dataFrameToDictOfDicts(readCsvToDataFrame())
