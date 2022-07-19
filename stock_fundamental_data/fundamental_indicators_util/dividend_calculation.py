from datetime import datetime


def izracunajSePodatkeZaDividende(fundamentalDataDict):
    # najprej izracunamo letne rasti dividend -> letosnja dividenda / lanska dividenda - 1
    leto_dividenda_keys = list(fundamentalDataDict.keys())
    for index, leto_dividenda in enumerate(fundamentalDataDict):
        fundamentalDataDict[leto_dividenda]['oneYearDividendGrowthRate'] = 0
        if datetime.strptime(leto_dividenda, "%Y-%m-%d").year > 1997:  # za ta leta lahko izracunamo letno rast dividende
            lansko_leto = leto_dividenda_keys[index - 1]
            if fundamentalDataDict[lansko_leto]['dividendPerShare'] != 0:  # da ni napake zaradi deljenja z 0
                fundamentalDataDict[leto_dividenda]['oneYearDividendGrowthRate'] = round(
                    fundamentalDataDict[leto_dividenda]['dividendPerShare'] / fundamentalDataDict[lansko_leto]['dividendPerShare'] - 1, 4)
            # ce lani ni bilo dividende in letos je potem je zrasla za 100%
            elif fundamentalDataDict[lansko_leto]['dividendPerShare'] == 0 and fundamentalDataDict[leto_dividenda]['dividendPerShare'] != 0:
                fundamentalDataDict[leto_dividenda]['oneYearDividendGrowthRate'] = 1

    # nato izracunamo se 5 letno povprecje letnih rasti dividend
    for index2, leto_dividenda_2 in enumerate(fundamentalDataDict):
        fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] = 0
        if datetime.strptime(leto_dividenda_2, "%Y-%m-%d").year >= 2002:  # ta leta imajo za sabo ze 5 let zapisov tako da lahko izracunamo 5 letno povprecje
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] += fundamentalDataDict[leto_dividenda_keys[index2 - 4]]['oneYearDividendGrowthRate']
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] += fundamentalDataDict[leto_dividenda_keys[index2 - 3]]['oneYearDividendGrowthRate']
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] += fundamentalDataDict[leto_dividenda_keys[index2 - 2]]['oneYearDividendGrowthRate']
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] += fundamentalDataDict[leto_dividenda_keys[index2 - 1]]['oneYearDividendGrowthRate']
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] += fundamentalDataDict[leto_dividenda_keys[index2]]['oneYearDividendGrowthRate']
            # izracunamo povprecje
            fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] = round(fundamentalDataDict[leto_dividenda_2]['fiveYearDividendGrowthRate'] / 5, 4)

    return fundamentalDataDict
