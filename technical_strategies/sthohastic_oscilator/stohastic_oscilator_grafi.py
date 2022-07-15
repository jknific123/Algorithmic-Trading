from matplotlib import pyplot as plt
import pandas as pd


def stohastic_trading_graph(sma_period, bands_multiplayer, df, company):
    # prikaz grafa gibanja cene in kupovanja ter prodajanja delnice

    fig = plt.figure(figsize=(8, 6), dpi=200)
    fig.suptitle(company)
    ax1 = fig.add_subplot(111, ylabel='Cena v $')

    # cena
    df['Close'].plot(ax=ax1, color='black', label="Cena", alpha=0.5)

    # buy/sell signali
    ax1.plot(df['Buy-Signal'], '^', markersize=6, color='green', label='Buy signal', lw=2)
    ax1.plot(df['Sell-Signal'], 'v', markersize=6, color='red', label='Sell signal', lw=2)
    legend = plt.legend(loc="upper left", edgecolor="black")
    legend.get_frame().set_alpha(None)
    legend.get_frame().set_facecolor((0, 0, 1, 0.1))
    plt.show()


def stohastic_indicator_graf(high_low_period, d_sma_period, df, company):
    # buy_signals = pd.DataFrame(df.index[df['Buy-Signal'] > 0].tolist())
    # sell_signals = pd.DataFrame(df.index[df['Sell-Signal'] > 0].tolist())

    axis = df[['%K', f'%D-{d_sma_period}-days']].plot()
    axis2 = df['Close'].plot(ax=axis, secondary_y=True, color='black')
    axis2.plot(df['Buy-Signal'], '^', markersize=6, color='green', label='Buy signal', lw=2)
    axis2.plot(df['Sell-Signal'], 'v', markersize=6, color='red', label='Sell signal', lw=2)
    axis.axhline(20, linestyle="--", color='r')
    axis.axhline(80, linestyle="--", color='r')
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

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df['Shares'])