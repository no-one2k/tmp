#!/usr/bin/python

import sys, getopt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

HALF_SPREAD = 0.0

helpline = """Usage:
simple_strategy.py -i <input csv>
default input csv is "usdrub.csv"

simple_strategy.py -h print this helpline"""

def main(argv):
    input_file = 'usdrub.csv'
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="])
    except getopt.GetoptError:
        print
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpline)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
    test_simple_strategy(input_file)

def plot_results(results):
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
         'Friday', 'Saturday', 'Sunday']
    ax = sns.heatmap(results, annot=True, fmt='.2f',
                    mask=np.tril(np.ones((7,7)), 0),
                    xticklabels=day_labels, yticklabels=day_labels)
    ax.set_xlabel('Weekday of Sell')
    ax.set_ylabel('Weekday of Buy')
    ax.set_title('Strategy results for pairs of days\n in $');

def results_by_sum(df_alldays):
    by_weekday = df_alldays.groupby(df_alldays.index.weekday)['BuyPrice',
                                                            'SellPrice'].sum()
    return [[(by_weekday.SellPrice[day_sell] - by_weekday.BuyPrice[day_buy])
            for day_sell in range(7)] for day_buy in range(7)]

def results_by_signals(df_alldays):
    results = []
    for day_buy in range(7):
        tmp_res = []
        for day_sell in range(7):
            if day_buy < day_sell:
                df_alldays['SignalBuy'] = (df_alldays.index.weekday==day_buy).astype(int)
                df_alldays['SignalSell'] = (df_alldays.index.weekday==day_sell).astype(int)
                df_alldays['result'] = (df_alldays.SignalSell * df_alldays.SellPrice) - (df_alldays.SignalBuy * df_alldays.BuyPrice)
                tmp_res.append(df_alldays.result.sum())
            else:
                tmp_res.append(0)
        results.append(tmp_res)
    return results

def test_simple_strategy(fname):
    df = pd.read_csv('usdrub.csv', index_col=0, parse_dates=True)
    df_alldays = df.resample('D').ffill()[:-1]
    df_alldays['BuyPrice'] = df_alldays.Open * (1 + HALF_SPREAD)
    df_alldays['SellPrice'] = df_alldays.Open * (1 - HALF_SPREAD)

    by_sum = results_by_sum(df_alldays)
    by_signals = results_by_signals(df_alldays)

    plot_results(by_sum)
    plt.savefig('results_by_sum.png')
    plt.clf()
    plot_results(by_signals)
    plt.savefig('results_by_signals.png')


if __name__ == "__main__":
    main(sys.argv[1:])
