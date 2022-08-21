from stock_fundamental_data.fundamental_indicators_util import fundamental_indicators_util as fUtil
from datetime import datetime

vsa_leta = [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
            2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]

vse_industrije_podjetja = {'Technology': ['AAPL', 'CRM', 'CSCO', 'HPQ', 'IBM', 'INTC', 'MSFT'],
                           'Financial Services': ['AIG', 'AXP', 'BAC', 'C', 'GS', 'JPM', 'TRV', 'V'],
                           'Healthcare': ['AMGN', 'JNJ', 'MRK', 'PFE', 'UNH', 'WBA'],
                           'Industrials': ['BA', 'CAT', 'GE', 'HON', 'AA', 'MMM', 'RTX'],
                           'Energy': ['CVX', 'XOM'],
                           'Basic Materials': ['DD', 'DOW'],
                           'Communication Services': ['DIS', 'T', 'VZ'],
                           'Consumer Cyclical': ['GM', 'HD', 'MCD', 'NKE'],
                           'Consumer Defensive': ['KO', 'MDLZ', 'MO', 'PG', 'WMT']}


def pridobiPodatkePodjetjaIndustryZaLeto(podjetje, leto, podjetja_data):
    for x in podjetja_data:
        if x == podjetje:
            for podjetje_leto in podjetja_data[podjetje]:
                if datetime.strptime(podjetje_leto, "%Y-%m-%d").year == leto:
                    return podjetja_data[podjetje][podjetje_leto]

    print('NAPAKA nisem nasel istega zapisa leta v podjetju za izracun avg data!')
    return {}


def izracunajAvgZaIndustrijoVLetu(podjetja_industrije, leto, podjetja_data):
    # kreiramo slovar za leto in podslovarje za avg vrednosti
    leto_industrija_avg_data = {}
    leto_industrija_avg_data["avgROE"] = 0
    leto_industrija_avg_data["avgProfitMargin"] = 0
    # leto_industrija_avg_data["avgGoodwill"] = 0
    leto_industrija_avg_data["avgRevenue"] = 0
    leto_industrija_avg_data["avgP/E"] = 0
    leto_industrija_avg_data["avgP/B"] = 0
    leto_industrija_avg_data["avgD/E"] = 0

    # leto_industrija_avg_data["avgROA"] = 0

    for podjetje in podjetja_industrije:
        print('podjetje: ', podjetje)
        podjetje_data = pridobiPodatkePodjetjaIndustryZaLeto(podjetje, leto, podjetja_data)
        leto_industrija_avg_data["avgROE"] += podjetje_data["ROE"]
        # leto_industrija_avg_data["avgROA"] += podjetje_data["ROA"]
        leto_industrija_avg_data["avgProfitMargin"] += podjetje_data["profitMargin"]
        # leto_industrija_avg_data["avgEbitdaMargin"] = podjetje_data["ebitdaMargin"]
        leto_industrija_avg_data["avgP/E"] += podjetje_data["P/E"]
        leto_industrija_avg_data["avgP/B"] += podjetje_data["P/B"]
        leto_industrija_avg_data["avgD/E"] += podjetje_data["D/E"]
        # leto_industrija_avg_data["avgGoodwill"] += podjetje_data["goodwill"]
        leto_industrija_avg_data["avgRevenue"] += podjetje_data["revenue"]

    # delimo z st podjetji v industriji za povprecje
    stPodjetjiIndustrije = len(podjetja_industrije)
    leto_industrija_avg_data["avgROE"] = round(leto_industrija_avg_data["avgROE"] / stPodjetjiIndustrije, 2)
    # leto_industrija_avg_data["avgROA"] = round(leto_industrija_avg_data["avgROA"] / stPodjetjiIndustrije, 2)
    leto_industrija_avg_data["avgProfitMargin"] = round(leto_industrija_avg_data["avgProfitMargin"] / stPodjetjiIndustrije, 2)
    # leto_industrija_avg_data["avgEbitdaMargin"] = round(leto_industrija_avg_data["avgEbitdaMargin"] / stPodjetjiIndustrije, 2)
    leto_industrija_avg_data["avgP/E"] = round(leto_industrija_avg_data["avgP/E"] / stPodjetjiIndustrije, 2)
    leto_industrija_avg_data["avgP/B"] = round(leto_industrija_avg_data["avgP/B"] / stPodjetjiIndustrije, 2)  # na 2 zaokrozi
    leto_industrija_avg_data["avgD/E"] = round(leto_industrija_avg_data["avgD/E"] / stPodjetjiIndustrije, 2)  # na 2 zaokrozi
    # leto_industrija_avg_data["avgGoodwill"] = round(leto_industrija_avg_data["avgGoodwill"] / stPodjetjiIndustrije, 2)
    leto_industrija_avg_data["avgRevenue"] = round(leto_industrija_avg_data["avgRevenue"] / stPodjetjiIndustrije, 2)  # na 2 zaokrozi

    return leto_industrija_avg_data


def getAllFundamentalIndustryAvgData(podjetja_data):
    allIndustryAvgData = {}
    # leta_podjetja = fUtil.getObdobjaInPodjetja()
    for industrija in vse_industrije_podjetja:
        print('industrija avg: ', industrija)
        allIndustryAvgData[industrija] = {}
        podjetja_industrije = vse_industrije_podjetja[industrija]
        for leto in vsa_leta:
            print('leto industrija avg: ', leto)
            allIndustryAvgData[industrija][leto] = {}
            allIndustryAvgData[industrija][leto] = izracunajAvgZaIndustrijoVLetu(podjetja_industrije, leto, podjetja_data)

    return allIndustryAvgData

