from datetime import datetime


def create_fundamental_buy_sell_signals(df, trading_dates, fundamental_data):

    df['dividendYield'] = 0.0
    df['dividendPayoutRatio'] = ''

    # zapišemo stanje indikatorjev za trading datume
    for trading_date in trading_dates:

        ticker = df['Ticker'].loc[trading_date]
        company_report = fundamental_data.getCompanyFundamentalDataForDate(ticker, trading_date)

        df['dividendYield'].loc[trading_date] = company_report['porocilo']["dividendYield"]
        df['dividendPayoutRatio'].loc[trading_date] = preveriPayoutRatio(ticker, trading_date, fundamental_data)

        # dividendDic = {}
        # for company in fundamental_data.vsi_tickerji:
        #     dividendDic[company] = preveriPayoutRatio(company, trading_date, fundamental_data)

    return df


def preveriPayoutRatio(companyTicker, datum, fundamental_data):
    period_company_data = fundamental_data.getCompanyFundamentalDataForPeriodOfYears(companyTicker, datum, 3)

    # mora biti vsa tri leta med 35% in 55%
    payoutRatioOk = True
    for zapis in period_company_data:

        # ce je kdaj manjsi od 35% ali pa vecji od 70% potem ni ok
        if 0.35 > period_company_data[zapis]['dividendPayoutRatio'] or period_company_data[zapis]['dividendPayoutRatio'] > 0.7:
            payoutRatioOk = False

    return payoutRatioOk


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

