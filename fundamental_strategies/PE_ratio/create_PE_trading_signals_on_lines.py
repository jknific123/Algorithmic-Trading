from datetime import datetime


def create_fundamental_buy_sell_signals(df, trading_dates, fundamental_data):

    df['P/E'] = 0.0
    df['avgP/E'] = 0.0

    # zapišemo stanje indikatorjev za trading datume
    for trading_date in trading_dates:

        ticker = df['Ticker'].loc[trading_date]
        company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, trading_date)
        industrija_podjetja = company_report['porocilo']['sector']
        year_avg_data = fundamental_data.getAvgIndustryFundamentalDataForYear(industrija_podjetja, datetime.strptime(company_report['datum'], '%Y-%m-%d').year)
        df['P/E'].loc[trading_date] = company_report['porocilo']["P/E"]
        df['avgP/E'].loc[trading_date] = year_avg_data['avgP/E']

    return df


def getTradingSignalsForAllTimeLines(time_lines, trading_dates, fDB):
    trading_time_lines = {}
    last_line = ''
    for line in time_lines:
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

