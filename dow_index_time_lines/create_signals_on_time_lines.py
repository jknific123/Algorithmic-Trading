import datetime as datetime
import get_time_lines as time_lines_db
import talib as ta
from functools import cache


@cache
def days_between(d1, d2):
    if d1 == "":
        return 0
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def create_buy_sell_signals(df, sSma_period, lSma_period, hold_obdobje):

    df[f"SMA-{sSma_period}"] = ta.SMA(df['Close'], sSma_period)
    df[f"SMA-{lSma_period}"] = ta.SMA(df['Close'], lSma_period)
    df = df[lSma_period:]

    df['Buy'] = ((df[f"SMA-{sSma_period}"] >= df[f"SMA-{lSma_period}"]) & (df[f"SMA-{sSma_period}"].shift(1) <= df[f"SMA-{lSma_period}"].shift(1)))
    df['Sell'] = ((df[f"SMA-{sSma_period}"] <= df[f"SMA-{lSma_period}"]) & (df[f"SMA-{sSma_period}"].shift(1) >= df[f"SMA-{lSma_period}"].shift(1)))
    df['Shares'] = 0
    df['Status'] = ''
    # df['Buy-date'] = ''
    # df['Sell-date'] = ''
    # df.loc[df['Buy'], 'Buy-date'] = df.loc[df['Buy']].index.tolist()
    # df['Cas holdanja'] = 0
    # df.loc[df['Buy'], 'Cas holdanja'] = hold_obdobje

    # uredimo pogoj hold obdobja
    zadnji_buy_date = ''
    for x in range(0, len(df)):
        if df["Buy"].to_numpy()[x]:
            zadnji_buy_date = df.index[x]
        if df['Sell'].to_numpy()[x]:
            # df['Cas holdanja'].to_numpy()[x] = days_between(zadnji_buy_date, df.index[x])
            cas_holdanja = days_between(zadnji_buy_date, df.index[x])
            if cas_holdanja < hold_obdobje:
                df['Sell'].to_numpy()[x] = False

        if x != len(df) - 1 and df['Ticker'].to_numpy()[x] != df['Ticker'].to_numpy()[x + 1]:
            df['Sell'].to_numpy()[x] = True  # za takrat ko gre za zamenjavo podjetji v indexu

    # print(df)

    return df


def getTradingSignalsForAllTimeLines(time_lines, shortSma, longSma, holdObdobje):
    trading_time_lines = {}
    for line in time_lines:
        trading_time_lines[line] = create_buy_sell_signals(time_lines[line], shortSma, longSma, holdObdobje)

    return trading_time_lines


# iz dataframe portfolia naredi dict portfolio
def createDictPortfolioFromDF(time_lines):
    portfolio = {}
    for line in time_lines:
        portfolio[line] = {}
        portfolio[line] = time_lines[line][['Close', 'Buy', 'Sell', 'Shares', 'Status', 'Ticker']].to_dict(orient='index')

    return portfolio


begin_time = datetime.datetime.now()

TimeLinesDB = time_lines_db.TimeLinesData()
# trading_signals_lines = getTradingSignalsForAllTimeLines(time_lines=TimeLinesDB.time_lines, shortSma=20, longSma=50, holdObdobje=1)

# df_AAPL = TimeLinesDB.time_lines['AAPL']
#
# df_trading_AAPL = create_buy_sell_signals(df_AAPL, 20, 50, 31)

# time_lines = TimeLinesDB.time_lines
# for line in time_lines:
#     time_lines[line] = create_buy_sell_signals(time_lines[line], 20, 50, 1)


# portfolio_df = time_lines['AAPL']
# aapl_df_dict = time_lines['AAPL'][['Close', 'Buy', 'Sell', 'Shares', 'Status', 'Ticker']].to_dict(orient='index')
# for x in range(0, len(portfolio_df)):
#     for company in time_lines:
#         datum = portfolio_df.index[x]
#         buy_signal = time_lines[company].loc[[datum]]['Buy'].to_numpy()[0]
#         sell_signal = time_lines[company].loc[[datum]]['Sell'].to_numpy()[0]


# portfolio = {}
# for line in time_lines:
#     portfolio[line] = {}
#     portfolio[line] = time_lines[line][['Close', 'Buy', 'Sell', 'Shares', 'Status', 'Ticker']].to_dict(orient='index')

# print('pri simulaciji portfolio')
# for datum in portfolio['AAPL']:  # gremo po datumih najprej
#     for time_line in portfolio:
#         buy_signal = False
#         sell_signal = False
#         if portfolio[time_line][datum]['Buy']:
#             buy_signal = True
#             price_five_shares = portfolio[time_line][datum]['Close'] * 5
#             portfolio[time_line][datum]['Shares'] = 5
#         if portfolio[time_line][datum]['Sell']:
#             sell_signal = True
#             cash_from_sale = portfolio[time_line][datum]['Close'] * 5
#             portfolio[time_line][datum]['Shares'] = 0


print('KONEC!!! ', datetime.datetime.now() - begin_time)
