from matplotlib import pyplot as plt
import pandas as pd

def MACD_trading_graph(sPeriod, lPeriod, signal_period, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(f"{company}, trgovalni signali")
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    fig2 = plt.figure(figsize=(8, 6), dpi=200)
    fig2.suptitle(f"{company}: MACD in signalna črta")
    ax2 = fig2.add_subplot(111, ylabel='Vrednost MACD in Signalne črte')
    # cena
    df['Close'].plot(ax=ax1, color='black', label="Cena", alpha=0.5)

    # MACD in signal line
    df[["MACD", f'Signal-{signal_period}']].plot(ax=ax2, linestyle="--")
    # df[["MACD", f'Signal-{signal_period}']].plot(ax=ax1, linestyle="--", secondary_y=True)
    # df['Close'].plot(ax=ax2, alpha=0.25, secondary_y=True)


    # buy/sell signali
    ax1.plot(df['Buy-Signal'], '^', markersize=6, color='green', label='Buy signal', lw=2)
    ax1.plot(df['Sell-Signal'], 'v', markersize=6, color='red', label='Sell signal', lw=2)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def profit_graph(df, mode, company, cash):
    # prikaz grafa sredstev
    # mode = 0 -> prikaz podjetja
    # mode = 1 -> prikaz portfolia

    fig = plt.figure(figsize=(8, 6), dpi=200)
    if (mode == 0):
        fig.suptitle(f'Končna vrednost podjetja {company}: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost sredstev v $')
        df['Total'].plot(ax=ax1, label="Vrednost sredstev", color='black', alpha=0.5)
    elif (mode == 1):
        fig.suptitle(f'Končna vrednost portfolia: {cash} $')
        ax1 = fig.add_subplot(111, ylabel='Vrednost portfolia v $')
        df['Total'].plot(ax=ax1, label="Vrednost portfolia", color='black', alpha=0.5)

    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def plotShares(df, company):
    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Num of shares')
    df['Shares'].plot(ax=ax1, color='black', alpha=0.5)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()

    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(df['Shares'])