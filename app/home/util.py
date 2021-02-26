import quandl
import os
import requests
import json
import sys
import pandas as pd
import yfinance as yf
import datetime
from currency_symbols import CurrencySymbols
from pytrends.request import TrendReq
import pyEX as p

os.environ['HTTP_PROXY'] = ""
os.environ['HTTPS_PROXY'] = ""

quandl.ApiConfig.api_key = "2RieC3BYU62Z4Z-koxRX"
IEX_API_KEY = "pk_67178ec015c04eae909c3308f69ebf09"
FINNHUB_API_KEY = "bqjbmjvrh5r89luqu650"
# IEX_API_KEY = "Tsk_85befaa9d13f4f0c82cdf7e183c201f2"

TICK_UNIFY = [
    {'EURONEXT': {
        'yahoo': 'PA',
        'iex': 'FP',
    }},
    {'NYSE': {
        'yahoo': '',
        'iex': '',
    }},
    {'NASDAQ': {
        'yahoo': '',
        'iex': '',
    }}
]

TICK_SEP = {
    'yahoo': '.',
    'iex': '-',
}


def get_df_history(df, days=365, dt='Date'):
    df = df.reset_index()
    date = datetime.datetime.now() - datetime.timedelta(days=days)
    #print(df, file=sys.stderr)
    if days > 365: df.groupby(pd.Grouper(freq='1W', key=dt)).mean()
    df = df.loc[df[dt] > date]

    return df.to_json(orient='records')


def get_historic_values(ticker, period='max'):
    tick = yf.Ticker(ticker)
    df = tick.history(period="10y")
    # df['Date'] = pd.to_datetime(df['Date'])
    df_10y = df.groupby(pd.Grouper(freq="1W")).mean()

    date_5y = datetime.datetime.now() - datetime.timedelta(days=5 * 365)
    df_5y = df.loc[df.index > date_5y]
    df_5y = df_5y.groupby(pd.Grouper(freq='1W')).mean()

    date_1y = datetime.datetime.now() - datetime.timedelta(days=365)
    df_1y = df.loc[df.index > date_1y]
    print(df_1y, file=sys.stderr)
    data = {
        'info': tick.info,
        'hist_10y': df_10y.reset_index().to_json(orient='records'),
        'hist_5y': df_5y.reset_index().to_json(orient='records'),
        'hist_1y': df_1y.reset_index().to_json(orient='records')
    }

    return data


def get_currency_symbol(currency_code):
    return CurrencySymbols.get_symbol(currency_code)


def request_finnhub_data(url, **kwargs):
    url = '%s?token=%s&' % (url, FINNHUB_API_KEY) + '&'.join(key + '=' + value for key, value in kwargs.items())
    print(url, file=sys.stderr)
    req = requests.get(url)

    return req.json()


def request_iex_data(url):
    try:
        req = requests.get('%s?token=%s' % (url, IEX_API_KEY))
    except:
        print("An Error occured while processins IEX request")
    return req.json()


def get_iex_ticker(ticker):
    c = p.Client(api_token=IEX_API_KEY)
    data = c.quote(ticker)

    return data


def get_series_math(df):
    mean = df.mean()
    min = df.min()
    max = df.max()
    previous = df.iloc[-2]
    last = df.iloc[-1]

    datas = {
        'mean': mean,
        'min': min,
        'max': max,
        'previous': previous,
        'last': last
    }
    return datas


def get_pytrends_data(string):
    pytrends = TrendReq(hl='en-US', tz=360)
    query = string.split(' ')[0]
    print(query, file=sys.stderr)
    kw_list = [query]
    pytrends.build_payload(kw_list, cat=7, timeframe='today 12-m', geo='', gprop='')
    df = pytrends.interest_over_time().reset_index()
    df.columns = ['Date', 'Value', 'Complete']

    data = get_series_math(df['Value'])
    data['df'] = df.to_json(orient='records')

    return data


def convert_ticker(src, dst, symbol):
    find = False
    for sep in TICK_SEP:
        if len(symbol.split(TICK_SEP[sep])) > 1:
            tick = symbol.split(TICK_SEP[sep])
            find = True

    if find:
        for e in TICK_UNIFY:
            for s in e:
                # print(tick[1], file=sys.stderr)
                # print(e[s][src], file=sys.stderr)
                if e[s][src] == tick[1]:
                    return tick[0] + TICK_SEP[dst] + e[s][dst]

    return symbol
