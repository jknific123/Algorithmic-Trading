from stock_fundamental_data.fundamental_indicators_util import fundamental_indicators_util as fUtil
from datetime import datetime


def pridobiPodatkePodjetjaZaLeto(podjetje, leto, podjetja_data):
    for x in podjetja_data:
        if x == podjetje:
            for podjetje_leto in podjetja_data[podjetje]:
                if datetime.strptime(podjetje_leto, "%Y-%m-%d").year == leto:
                    return podjetja_data[podjetje][podjetje_leto]

    print('NAPAKA nisem nasel istega zapisa leta v podjetju za izracun avg data!')
    return {}


def izracunajAvgZaPodjetjaVLetu(all_podjetja, leto, podjetja_data):
    # kreiramo slovar za leto in podslovarje za avg vrednosti
    leto_avg_data = {}
    leto_avg_data["avgROE"] = 0
    leto_avg_data["avgProfitMargin"] = 0
    leto_avg_data["avgGoodwill"] = 0
    leto_avg_data["avgRevenue"] = 0

    # gremo cez podjetja tega leta in zanje pridobimo podatke ter jih pristejemo trenutnim avg vrednostim
    for podjetje in all_podjetja:
        print('podjetje: ', podjetje)
        podjetje_data = pridobiPodatkePodjetjaZaLeto(podjetje, leto, podjetja_data)
        leto_avg_data["avgROE"] += podjetje_data["ROE"]
        leto_avg_data["avgProfitMargin"] += podjetje_data["profitMargin"]
        leto_avg_data["avgGoodwill"] += podjetje_data["goodwill"]
        leto_avg_data["avgRevenue"] += podjetje_data["revenue"]

    # delimo z 30 za povprečje TODO povprečenje uredit še za, ko manjka GM
    leto_avg_data["avgROE"] = round(leto_avg_data["avgROE"] / 30, 4)
    leto_avg_data["avgProfitMargin"] = round(leto_avg_data["avgProfitMargin"] / 30, 4)
    leto_avg_data["avgGoodwill"] = round(leto_avg_data["avgGoodwill"] / 30, 4)
    leto_avg_data["avgRevenue"] = round(leto_avg_data["avgRevenue"] / 30, 4)

    return leto_avg_data


def getAllFundamentalAvgData(podjetja_data):
    allAvgData = {}
    leta_podjetja = fUtil.getObdobjaInPodjetja()
    for leto in leta_podjetja:
        print('leto avg: ', leto)
        podjetja_tega_leta = leta_podjetja[leto]
        allAvgData[leto] = izracunajAvgZaPodjetjaVLetu(podjetja_tega_leta, leto, podjetja_data)

    return allAvgData
