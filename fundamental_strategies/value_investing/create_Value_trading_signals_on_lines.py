from datetime import datetime
import numpy as np


def create_fundamental_buy_sell_signals(df, trading_dates, fundamental_data):

    df["ROE"] = np.nan
    df["D/E"] = np.nan
    df["avgD/E"] = np.nan
    df["P/B"] = np.nan
    df["avgP/B"] = np.nan
    df["ProfitMargin"] = np.nan
    df["freeCashFlowMargin"] = np.nan
    df["DCF"] = np.nan
    df["price"] = np.nan

    # zapišemo stanje indikatorjev za trading datume
    for trading_date in trading_dates:
        # zaenkrat samo za datume, ki so vecji od 30% testne start date
        if datetime.strptime(trading_date, '%Y-%m-%d') >= datetime.strptime('2017-02-02', '%Y-%m-%d'):

            ticker = df['Ticker'].loc[trading_date]
            company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, trading_date)
            industrija_podjetja = company_report['porocilo']['sector']
            year_avg_data = fundamental_data.getAvgIndustryFundamentalDataForYear(industrija_podjetja, datetime.strptime(company_report['datum'], '%Y-%m-%d').year)

            df['ROE'].loc[trading_date] = preveriROE(ticker, trading_date, fundamental_data, industrija_podjetja)
            df['ProfitMargin'].loc[trading_date] = preveriProfitMargin(ticker, trading_date, fundamental_data, industrija_podjetja)

            df['D/E'].loc[trading_date] = company_report['porocilo']["D/E"]
            df['avgD/E'].loc[trading_date] = year_avg_data['avgD/E']
            df['P/B'].loc[trading_date] = company_report['porocilo']["P/B"]
            df['avgP/B'].loc[trading_date] = year_avg_data['avgP/B']
            df['freeCashFlowMargin'].loc[trading_date] = company_report['porocilo']["freeCashFlowMargin"]
            df['DCF'].loc[trading_date] = company_report['porocilo']["dcf"]
            df['price'].loc[trading_date] = company_report['porocilo']["price"]

            # if df['ROE'].loc[trading_date] and df['ProfitMargin'].loc[trading_date]:
            #     print('ROE in PM ok: ', trading_date, ticker)

    return df


def preveriROE(companyTicker, datum, fundamental_data, industrija):
    period_company_data = fundamental_data.getCompanyFundamentalDataForPeriodOfYears(companyTicker, datum, 2)
    period_avg_industry_data = fundamental_data.getAvgIndustryFundamentalDataForPeriodOfYears(industrija, datetime.strptime(datum, '%Y-%m-%d').year, 2)

    roeOk = True
    for zapis in period_company_data:
        # ne sme bit pod 10% ali pod povprecjem industrije
        if period_company_data[zapis]['ROE'] < 0.1 or period_company_data[zapis]['ROE'] < period_avg_industry_data[datetime.strptime(zapis, '%Y-%m-%d').year]['avgROE']:
            roeOk = False

    # if roeOk:
    #     print('ROE OK: ', datum, companyTicker)

    return roeOk


def preveriProfitMargin(companyTicker, datum, fundamental_data, industrija):
    period_company_data = fundamental_data.getCompanyFundamentalDataForPeriodOfYears(companyTicker, datum, 2)
    period_avg_industry_data = fundamental_data.getAvgIndustryFundamentalDataForPeriodOfYears(industrija, datetime.strptime(datum, '%Y-%m-%d').year, 2)

    pmOK = True
    for zapis in period_company_data:
        # ne sme bit pod 10% ali pod povprecjem industrije
        if period_company_data[zapis]['profitMargin'] < 0.1 or period_company_data[zapis]['profitMargin'] < period_avg_industry_data[datetime.strptime(zapis, '%Y-%m-%d').year]['avgProfitMargin']:
            pmOK = False

    # if pmOK:
    #     print('PM OK: ', datum, companyTicker)

    return pmOK


def getTradingSignalsForAllTimeLines(time_lines, trading_dates, fDB):
    trading_time_lines = {}
    last_line = ''
    for line in time_lines:
        # print('Linija: ', line)
        trading_time_lines[line] = create_fundamental_buy_sell_signals(time_lines[line], trading_dates, fDB)
        last_line = line

    return trading_time_lines, trading_time_lines[last_line].index


# iz dataframe portfolia naredi dict portfolio
def createDictPortfolioFromDF(time_lines):
    portfolio = {}
    st_linije = 1
    for line in time_lines:
        portfolio[f'linija_{st_linije}'] = {}
        del time_lines[line]['High']
        del time_lines[line]['Low']
        portfolio[f'linija_{st_linije}'] = time_lines[line].to_dict(orient='index')
        st_linije += 1

    return portfolio

