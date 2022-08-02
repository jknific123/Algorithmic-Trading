import pandas as pd
import datetime as datetime
import numpy as np

from utility import utils as util


pd.options.mode.chained_assignment = None  # default='warn'


# def zacetniDf(data):
#     # v nadaljevanju uporabljamo samo podatke od takrat, ko je dolgi sma že na voljo, prav tako
#     # kreiramo nova stolpca za buy/sell signale
#     data['Buy'] = np.nan
#     data['Sell'] = np.nan
#     data['Cash'] = 0.0
#     data['Shares'] = 0
#     data['Profit'] = 0.0
#     data['Total'] = 0.0
#     data['Ticker'] = ""
#     data['Buy-Signal'] = np.nan
#     data['Sell-Signal'] = np.nan
#     data["Buy-date"] = ""
#     data["Sell-date"] = ""
#     data['Ostali Cash'] = 0.0
#
#     return data


def setObdobja(startObdobja, endObdobja, dowTickersObdobja):
    # hardcodam za testno mnozico
    obdobja = []

    if startObdobja == "2017-02-02" or startObdobja == "2018-09-09" or startObdobja == '2020-04-16':
        obdobja.append(startObdobja)

    for x in dowTickersObdobja:

        if startObdobja <= x < endObdobja:  # zna bit da je tuki treba se = dat
            obdobja.append(x)

    zadnjeObdobje = obdobja[len(obdobja) - 1]
    if endObdobja > zadnjeObdobje:
        obdobja.append(endObdobja)  # appendamo end date ker skoraj nikoli ne bo čisto točno eno obdobje iz dowTickers

    # print("Obdobja: ", obdobja)
    return obdobja


def backtest(start, end, dowTickers, stockPricesDB):
    # nastavimo obdobja
    obdobja = setObdobja(startObdobja=start, endObdobja=end, dowTickersObdobja=dowTickers)

    portfolio = {}
    starting_companies = []

    for i in range(0, len(obdobja) - 1):  # gremo cez vsa obdobja in jih imamo po parih startDATE -> endDATE

        zacetnoObdobje = obdobja[i]
        koncnoObdobje = obdobja[i + 1]

        # zacetek
        if zacetnoObdobje == start:
            # hardcodam za zacetno od ucne in testne mnozice
            # print("V zacetnem")

            # dolocanje zacetnih podjetji in zacetnega datuma za download
            ohlc_download_start_date = ''
            # 70% - 30%
            if zacetnoObdobje == "2005-11-21":
                starting_companies = dowTickers[zacetnoObdobje]["all"]
                ohlc_download_start_date = '2005-02-07'  # za max long sma na ucni mnozici
            elif zacetnoObdobje == "2017-02-02":
                starting_companies = dowTickers["2015-03-19"]["all"]
                ohlc_download_start_date = '2016-04-19'  # za max sma na testni mnozci
            # 80% - 20%
            elif zacetnoObdobje == '2018-09-09':
                starting_companies = dowTickers['2018-06-26']['all']
                ohlc_download_start_date = '2017-11-21'  # za max sma na testni mnozci
            # 90% - 10%
            elif zacetnoObdobje == '2020-04-16':
                starting_companies = dowTickers['2019-04-02']['all']
                ohlc_download_start_date = '2019-07-01'  # za max sma na testni mnozci

            # trejdamo z all od zacetnegaObdobja
            for x in starting_companies:

                # izjema za podjetje GM, za katerega nimam podatkov, zato samo naredim prazen dataframe
                if x == "GM":
                    # pridobim df od podjetja HD in zbrišem podatke tako da je potem prazen
                    prazen = stockPricesDB.getCompanyStockDataInRange(date_from=ohlc_download_start_date, date_to=koncnoObdobje, companyTicker="HD")
                    prazen = prazen[['Close', 'High', 'Low']].copy()
                    # prazen = zacetniDf(prazen)
                    prazen["Close"] = 0
                    prazen["Ticker"] = x
                    # prazen["test"] = 1
                    portfolio[x] = prazen

                elif x != "GM":
                    data = stockPricesDB.getCompanyStockDataInRange(date_from=ohlc_download_start_date, date_to=koncnoObdobje, companyTicker=x)
                    data = data[['Close', 'High', 'Low']].copy()
                    data["Ticker"] = x
                    # data['test'] = 1
                    # data = zacetniDf(data)  # dodamo stolpce
                    portfolio[x] = data

        # ce nismo na zacetku gremo cez removed in added in naredimo menjave ter trejdamo za naslednje obdobje
        elif zacetnoObdobje != start:

            dodani = []
            # gremo najprej cez removed in opravimo zamenjave
            for odstranjenTicker in dowTickers[zacetnoObdobje]["removed"]:

                starting_companies = portfolio.keys()

                if odstranjenTicker in starting_companies:  # odstranjenTicker je v trenutnem portfoliu -> ga zamenjamo z isto ležečim tickerjem iz added

                    # pridobimo df od odstranjenega tickerja
                    ex_df = portfolio[odstranjenTicker]

                    # zamenjamo odstranjenTicker z isto ležečim tickerjem iz added
                    nov_ticker = dowTickers[zacetnoObdobje]["added"][dowTickers[zacetnoObdobje]["removed"].index(odstranjenTicker)]
                    real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                    plus_one_start_date = (real_start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # adding one day
                    new_df = stockPricesDB.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=nov_ticker)
                    new_df = new_df[['Close', 'High', 'Low']].copy()
                    new_df["Ticker"] = nov_ticker
                    # new_df["test"] = 1

                    concat_df = pd.concat([ex_df, new_df])
                    # naredimo nov slovar-portfolio iz prejsnjega s tem, da je key trenutnega df nov_ticker namesto odstranjenTicker
                    new_portfolio = {nov_ticker if k == odstranjenTicker else k: v for k, v in portfolio.items()}
                    new_portfolio[nov_ticker] = concat_df  # shranimo nov podaljšan dataframe v nov portfolio
                    portfolio = new_portfolio
                    dodani.append(nov_ticker)

            # smo updejtali vse removed, zdej pa samo nadaljujemo trejdanej z usemi ostalimi

            ostali = set(portfolio.keys()) - set(dodani)
            ostali = sorted(list(ostali))
            # print("Ostali tickerji: ", sorted(ostali))
            for ostaliTicker in ostali:

                real_start_date = datetime.datetime.strptime(zacetnoObdobje, "%Y-%m-%d")
                plus_one_start_date = (real_start_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")  # adding one day

                ostaliTickerDataframe = portfolio[ostaliTicker]

                # print("Trenutni ostali ticker: ", ostaliTicker)
                company = ostaliTicker
                if ostaliTicker == "GM":
                    company = "HD"  # ce se prav spomnem se uzame HD samo zato, da se dobi ok velik df, ker za GM ne morem
                new_data = stockPricesDB.getCompanyStockDataInRange(date_from=plus_one_start_date, date_to=koncnoObdobje, companyTicker=company)
                if ostaliTicker == "GM":
                    new_data["Close"] = 0
                new_data = new_data[['Close', 'High', 'Low']].copy()
                new_data["Ticker"] = ostaliTicker
                # new_data["Ticker"] = f"new{ostaliTicker}"
                # new_data["test"] = 1
                # new_data = zacetniDf(new_data)  # dodamo stolpce

                concat_data = pd.concat([ostaliTickerDataframe, new_data])

                portfolio[ostaliTicker] = concat_data

    return portfolio

