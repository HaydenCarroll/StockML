from pandas_datareader import data as web
import pandas as pd
import datetime as date
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
import json
from scipy import stats
from multiprocessing.dummy import Pool as ThreadPool
import tqdm
import time

sy = 2010
def main():
    global sy
    symbols = get_nasdaq_symbols()
    print("Number of companies: "+str(len(symbols)))
    print('input the year you would like to start from:')
    start_year = input()
    try:
        start_year = int(start_year)
    except:
        print('Invalid input exiting program')
        exit(1)
    sy = start_year
    data = {'stocks': []}
    pool = ThreadPool(30)
    #results = []
    #for _ in tqdm.tqdm(pool.map(get_data, symbols['NASDAQ Symbol']), total=len(symbols['NASDAQ Symbol'])):
        #pass
    results = list(tqdm.tqdm(pool.imap(get_data, symbols['NASDAQ Symbol']), total=len(symbols['NASDAQ Symbol'])))

    result_data = []
    for r in results:
        result_data.append(r)
    # NASDAQ Symbol
    for symbol in symbols['NASDAQ Symbol']:
        if result_data.index(0) is None:
            result_data.pop(0)
            continue
        try:
            # Security Name
            name = symbols.loc[symbol]['Security Name']
            print('Getting data for '+str(symbol) + " - " + str(symbols.loc[symbol]['Security Name']))
            data['stocks'].append({
                'name': name,
                'symbol': symbol,
                'info': result_data.pop(0)
            })

        except:
            continue

    for stock in data['stocks']:
        values = []
        dates = []
        for val in stock['info']['data']:
            values.append(val['value'])
        for dat in stock['info']['data']:
            dates.append(dat['date'])
        description = stats.describe(values)
        stock['stats'] = []
        stock['stats'].append({
            'nobs': description[0],
            'min': description[1][0],
            'max': description[1][1],
            'mean': description[2],
            'variance': description[3],
            'skewness': description[4],
            'kurtosis': description[5]
        })
        print()
        print(stock['name'])
        print(description)
        print()
    with open('stock_data.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True, default=str)




def test_main():
    global sy
    start_year = input('input the year you would like to start from')
    try:
        start_year = int(start_year)
    except:
        print('Invalid input exiting program')
        exit(1)
    sy = start_year
    data = {'stocks': []}
    symbols = get_nasdaq_symbols()
    small_symbols = []
    for i in range(5):
        small_symbols.append(symbols['NASDAQ Symbol'][i])
    pool = ThreadPool(5)
    results = pool.map(get_data, small_symbols)
    result_data = []
    for r in results:
        result_data.append(r)
    for i in range(5):
        symbol = symbols['NASDAQ Symbol'][i]
        try:
            name = symbols.loc[symbol]['Security Name']
            print('Getting data for ' + str(symbol) + " - " + str(symbols.loc[symbol]['Security Name']))
            data['stocks'].append({
                'name': name,
                'symbol': symbol,
                'info': result_data.pop(0)
            })

        except:
            continue



    for stock in data['stocks']:
        values = []
        dates = []
        for val in stock['info']['data']:
            values.append(val['value'])
        for dat in stock['info']['data']:
            dates.append(dat['date'])
        description = stats.describe(values)
        stock['stats'] = []
        stock['stats'].append({
            'nobs': description[0],
            'min': description[1][0],
            'max': description[1][1],
            'mean': description[2],
            'variance': description[3],
            'skewness': description[4],
            'kurtosis': description[5]
        })
        print()
        print(stock['name'])
        print(description)
        print()
    with open('stock_data.json', 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True, default=str)


def get_data(symbol):
    global sy
    #sy = 2010
    sm = 1
    sd = 4

    ey = 2018
    em = 1
    ed = 1
    start = date.datetime(sy, sm, sd)

    # end = date.datetime(ey, em, ed)
    end = date.datetime.now()
    try:
        f = web.DataReader(symbol, 'yahoo', start, end)
    except:
        return None
    incro = date.timedelta(days=1)
    cur_day = start
    data = {'data': []}
    while cur_day <= end:

        try:
            value = f.loc[cur_day.strftime("%Y-%m-%d")]['Close']
            cdate = cur_day
            data['data'].append({
                'date': cdate,
                'value': value
            })
            #print(symbol + ' - ' +str(cur_day.strftime("%Y-%m-%d"))+": "+str(f.loc[str(cur_day)]['Close']))
            cur_day = cur_day + incro
        except Exception:
            cur_day = cur_day + incro
    return data
    # print("date length "+str(len(date_array)))
    # print("data length "+str(len(data_array)))
    # plt.plot(date_array,data_array)
    # plt.show()


main()
