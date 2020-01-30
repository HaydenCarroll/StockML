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
from tqdm import tqdm
import time
import matplotlib.dates as mdates
from scipy.cluster.hierarchy import dendrogram


years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')
sy = 2010  # default starting year


# main starting method
def main():
    # request user input for method selection
    print("Enter a number")
    print("(1) start gathering data")
    print("(2) use current data")
    print("(3) view graphs")
    selection = input()
    if(str.isdigit(selection)):
        selection = int(selection)
        if selection == 1:
            start_data_gather()
        if selection == 2:
            use_current_data()
        if selection == 3:
            view_graphs()
        else:
            print("Invalid selection")
            return
    else:
        print("Invalid selection")
        return


# method used to gather initial data for stocks
def start_data_gather():
    global sy
    symbols = get_nasdaq_symbols()
    print("Number of companies: "+str(len(symbols)))
    print('input the year you would like to start from:')
    start_year = input()
    print('input the number of threads you would like to use:')
    num_threads = input()
    try:
        start_year = int(start_year)
        num_threads = int(num_threads)
    except:
        print('Invalid input exiting program')
        exit(1)
    sy = start_year
    data = {'stocks': []}
    pool = ThreadPool(num_threads)
    results = list(tqdm(pool.imap(get_data, symbols['NASDAQ Symbol']), total=len(symbols['NASDAQ Symbol'])))
    json_results = {'Data Results': []}
    for tr in results:
        json_results['Data Results'].append(tr)
    print("Storing data please wait...")
    with open('first_data.json', 'w') as f:
        json.dump(json_results, f, indent=4, sort_keys=True, default=str)

    # NASDAQ Symbol
    for s in json_results['Data Results']:
        try:
            # Security Name
            symbol = s['symbol'][0]
            name = symbols.loc[symbol]['Security Name']

            data['stocks'].append({
                'name': name,
                'symbol': symbol,
                'info': s['data']
            })
            print('Getting data for ' + str(symbol) + " - " + str(symbols.loc[symbol]['Security Name']))

        except:
            continue
    # print(json.dumps(data))
    for stock in data['stocks']:
        values = []
        dates = []
        for val in stock['info']:
            values.append(val['value'])
        for dat in stock['info']:
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
    print("Storing data please wait...")
    with open('stock_data.json', 'w') as stock_data:
        json.dump(data, stock_data, indent=4, sort_keys=True, default=str)


# method for using local data
def use_current_data():
    global sy
    symbols = get_nasdaq_symbols()

    data = {'stocks': []}
    with open('first_data.json') as test_data:
        json_results = json.load(test_data)

    results = []
    for d in json_results:
        results.append(d)
    # print(json.dumps(json_results['Data Results']))
    # NASDAQ Symbol
    for s in json_results['Data Results']:
        try:
            # Security Name
            symbol = s['symbol'][0]
            name = symbols.loc[symbol]['Security Name']

            data['stocks'].append({
                'name': name,
                'symbol': symbol,
                'info': s['data']
            })
            print('Getting data for ' + str(symbol) + " - " + str(symbols.loc[symbol]['Security Name']))

        except:
            continue
    # print(json.dumps(data))
    for stock in data['stocks']:
        values = []
        dates = []
        for val in stock['info']:
            values.append(val['value'])
        for dat in stock['info']:
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
    with open('stock_data.json', 'w') as stock_data:
        json.dump(data, stock_data, indent=4, sort_keys=True, default=str)


# method to retrieve data from yahoo finance
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
    data = {'data': [], 'symbol': []}
    data['symbol'].append(symbol)
    for t in f.itertuples():
        data['data'].append({
            'date': t[0].strftime("%Y-%m-%d"),
            'value': t[-1]
        })

    return data


# method used to display data
def view_graphs():
    print("Loading please wait...")
    f = open('stock_data.json')
    json_results = json.load(f)
    # with open('stock_data.json') as stock_data:
    #     json_results = json.load(stock_data, object_hook=hook)
    keep_running = True
    while (keep_running):
        print("Enter symbol or q to quit")
        inpt = input()
        if str(inpt) is 'q':
            quit(0)
        selected_stock = None
        if str.isdigit(inpt):
            index = int(inpt)
            selected_stock = json_results['stocks'][index]
        else:
            for stock in json_results['stocks']:
                #print(stock['symbol'])
                if stock['symbol'].lower() == inpt.lower():
                    selected_stock = stock
                    break
        if selected_stock is None:
            print('invalid symbol')
            quit(1)
        fig, ax = plt.subplots()

        X = []
        Y = []
        for info in selected_stock['info']:
            d = info['date']
            date_value = date.datetime.strptime(d, "%Y-%m-%d")
            X.append(date_value)

            value = info['value']
            Y.append(value)
        yi = Y[0]
        yf = Y[-1]
        mid = yf/2
        for i in range(len(Y)):
            if i == 0:
                Y[i] = Y[i]+mid
                continue
            print("before adjustment "+str(Y[i]))
            Y[i] = Y[i]+mid
            Y[i] = Y[i]-yi
            print("after adjustment "+str(Y[i]))
            print("adjusted amount "+str(mid-yi))
        #ax.plot('date', 'adj_close', data=X)
        ax.plot(X,Y)
        # format the ticks
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        # round to nearest years.
        datemin = np.datetime64(X[0], 'Y')
        datemax = np.datetime64(X[-1], 'D')
        ax.set_xlim(datemin, datemax)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.grid(True)
        ax.set_title(selected_stock['name'])


        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()
        plt.show()


main()
