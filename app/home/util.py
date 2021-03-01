import quandl
import os
import requests
import json
import sys
import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials
import datetime
from currency_symbols import CurrencySymbols
from pytrends.request import TrendReq
import pyEX as p
import io


os.environ['HTTP_PROXY'] = "http://172.16.99.9:3129"
os.environ['HTTPS_PROXY'] = "http://172.16.99.9:3129"

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

EXCH_INDEX= {
    'NMS': ['^GSPC', '^DJI'],
    'NYQ': ['^GSPC', '^DJI'],
    'PAR': ['^FCHI'],
}

def get_index(exchange):
    return EXCH_INDEX[exchange]


def merge_df(df1, df2, col):
    df: pd.DataFrame() = pd.merge(df1, df2, how='outer', on=col)
    print(df.head, file=sys.stderr)
    return df

def get_industry_info():
    url = "https://finviz.com/grp_export.ashx?g=industry&v=110&o=pe"
    payload = {}
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), header=0, index_col=0)

    return df

def get_quandl(key):
    return quandl.get(key)

def get_df_history(df, days=365, dt='Date'):
    df = df.reset_index()
    date = datetime.datetime.now() - datetime.timedelta(days=days)
    #print(df, file=sys.stderr)
    if days > 365: df.groupby(pd.Grouper(freq='1W', key=dt)).mean()
    df = df.loc[df[dt] > date]

    return df


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
    d50_average = df.tail(50).mean()
    d200_average = df.tail(200).mean()
    previous = df.iloc[-2]
    last = df.iloc[-1]

    datas = {
        'mean': float(mean),
        'min': float(min),
        'max': float(max),
        'previous': float(previous),
        'last': float(last),
        'd50_average': float(d50_average),
        'd200_average': float(d200_average),
    }
    return datas


def get_pytrends_data(string):
    pytrends = TrendReq(hl='en-US', tz=360)
    kw_list = [string]
    pytrends.build_payload(kw_list, cat=7, timeframe='today 12-m', geo='', gprop='')
    df = pytrends.interest_over_time().reset_index()

    return df


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
