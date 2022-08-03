import pandas as pd
from utility import utils as util


def backtestPortfolio(portfolio):

    df_totals = pd.DataFrame(0.0, columns=['Total'])
    # pridobim list vseh datumov
    all_dates = list(portfolio['NKE'].keys())
    all_cash = util.getMoney('') * 30

    # gledamo stanje za vsak dan posebaj
    for date in all_dates:

        # pridobimo tiste, ki imajo danes buy/sell signal
        buy_signals = []
        sell_signals = []
        for line in portfolio:
            line_company = portfolio[line]
            ticker = portfolio[line]['Ticker']
            if line[date]['Buy']:
                buy_signals.append((line, ticker))
            elif line[date]['Sell']:
                sell_signals.append((line, ticker))

        sell_cash = prodajSellLinije(portfolio=portfolio, sell_linije=sell_signals, datum=date)
        cash_per_line = all_cash / len(buy_signals)




def prodajSellLinije(portfolio, sell_linije, datum):
    sell_money = 0.0

    for company in sell_linije:
        None
