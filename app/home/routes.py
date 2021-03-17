# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from pandas import DataFrame

from app.home import blueprint
from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_login import login_required, current_user
from app import login_manager
from yahoofinancials import YahooFinancials
from jinja2 import TemplateNotFound
from app.home.filters import *
import app.home.util as util
import numpy as np
import urllib
import os
import requests
import pandas as pd
import json
import sys
import yfinance as yf

os.environ['HTTP_PROXY'] = ""
os.environ['HTTPS_PROXY'] = ""

@blueprint.route('/market/index')
@login_required
def market_index():
    indexes = {
        'America': {'S&P 500': '^GSPC', 'Dow Jones': '^DJI', 'Nasdaq': '^IXIC'},
        'Europe': {'DAX': '^GDAXI'},
        'Asia': {'Nikkei':'^N225'},
    }

    idx_values = [indexes[x][y] for x in indexes for y in indexes[x]]
    #infos = yf.Tickers(' '. join(idx_values))
    df: pd.DataFrame = yf.download(' '. join(idx_values), period='10y')
    #print(df)
    datas = {}
    for continent in indexes:
        datas[continent] = {}
        for label in indexes[continent]:
            values = df.xs(indexes[continent][label], level=1, axis=1).reset_index()
            values = values.dropna(how='any', axis=0)

            datas[continent][label] = util.get_series_math(values['Close'])
            values['sma200'] = util.sma(200, values['Close'])
            sma200 = [[x['Date'], x['sma200']] for x in json.loads(values.to_json(orient='records'))]
            history = [[x['Date'], x['Close']] for x in json.loads(values.to_json(orient='records'))]

            datas[continent][label]['history'] = json.dumps(history)
            datas[continent][label]['sma200'] = json.dumps(sma200)

    return render_template('market_index.html', segment=['market', 'index'], data=datas)

@blueprint.route('/api/industry', methods=['POST', 'GET'])
@login_required
def api_industry():
    industry = request.args.get('name')
    print(industry)
    # Finvizz Industry Perf
    df: pd.DataFrame = util.get_industry_info("https://finviz.com/grp_export.ashx?g=industry&v=150&o=name&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26")
    print(df)
    data = json.loads(df.loc[df['name'].isin([industry])].to_json(orient='records'))
    print(data)

    return make_response(jsonify(data[0]), 200)

@blueprint.route('/api/pytrend', methods=['POST', 'GET'])
@login_required
def api_pytrend():
    terms = request.args.get('terms')
    terms = terms.split(' ')
    df = util.get_pytrends_data(terms[0])
    data = util.get_series_math(df[terms[0]])
    data['point'] = [[x['date'], x[terms[0]]] for x in json.loads(df.to_json(orient='records'))]

    return make_response(jsonify(data), 200)

@blueprint.route('/api/financials', methods=['POST', 'GET'])
@login_required
def api_financials():
    symbol = request.args.get('symbol')
    type = request.args.get('type')
    data = {
        'income': 'incomeStatementHistory',
        'balance': 'balanceSheetHistory',
        'cash': 'cashflowStatementHistory',
    }
    try:
        financials = yf.Ticker(symbol).financials
        print(financials)
        data = financials.to_json(orient='index')
        print(data)
        #data = financials.get_financial_stmts('annual', type)[data[type]][symbol]

    except: data = []

    return make_response(data, 200)


@blueprint.route('/stock/<ticker>')
@login_required
def stock(ticker):

    # timeframe = [10*365, 5*365, 365]

    # Yahoo Data
    yahoo = yf.Ticker(ticker)
    print(yahoo.info)
    df = yahoo.history(period='10y').reset_index()
    tick = [[x['Date'], x['Close']] for x in json.loads(df.to_json(orient='records'))]
    #print(yahoo.financials.head)






    #index = util.get_index(yahoo['exchange'])
    #tickers = ticker + ' ' + ' '.join(index)
    #df = yf.download(tickers, period='10y').reset_index()
    #index = util.get_quandl('BCB/UDJIAD1').reset_index()
    #index = util.get_df_history(index, 10*365)

    #print('quandl finished')
    #df = util.merge_df(df, index, 'Date')

    #df = yahoo.history(period='max').reset_index()
    #print(df.head())
    # multitick = {
    #     'date': pd.to_datetime(df['Date']).tolist(),
    #     'close': list(df['Close']),
    #     'volume': list(df['Volume']),
    # }
    #print(json.loads(df.to_json(orient='records')))

    # vol = [[x['Date'], x['Volume']] for x in json.loads(df.to_json(orient='records'))]
    #index = [[x['Date'], x[index[0]]['Value']] for x in json.loads(df.to_json(orient='records'))]


    # PyTrends Data
    #pytrend = util.get_pytrends_data(yahoo.info['shortName'].split(' ')[0])
    #print('pytrend finished')

    # IEX Data
    iex_tick = util.convert_ticker('yahoo', 'iex', ticker)
    iex = util.get_iex_ticker(iex_tick)

    data = {
        'yahoo': yahoo.info,
        #'financial': financial,
        'iex': iex,
        #'pytrend': pytrend,
        'tick': tick,
        'math': util.get_series_math(df['Close'])
        #'volume': vol,
        #'multi': multitick,
        #'index': index,
    }
    return render_template('stock.html', segment=['stock', data['yahoo']['shortName']], data=data)


@blueprint.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        q = request.form.get('search')
        try:
            data = pd.read_html('https://finance.yahoo.com/lookup/all?s=%s&c=9999' % urllib.parse.quote(q), header=0)
            df: pd.DataFrame = data[0]
            df.columns = ['symbol', 'name', 'last', 'industry', 'type', 'exchange']
            rows = len(df)
            df = json.loads(df.to_json(orient='records'))
        except:
            df = []
            rows = 0

        #print(df, file=sys.stderr)
        data = {
            'query': q,
            'count': rows,
            'result': df,
        }
    return render_template('search_result.html', data=data)


# @blueprint.route('/search', methods=['POST', 'GET'])
# @login_required
# def search():
#     if request.method == 'POST':
#         q = request.form.get('search')
#         print(q, file=sys.stderr)
#         req = util.request_finnhub_data('https://finnhub.io/api/v1/search', q=q)
#         print(req, file=sys.stderr)
#
#         data = req['result']
#         data = {
#             'query': q,
#             'result': data,
#         }
#     return render_template('search_result.html', data=data)

# def search_old():
#     if request.method == 'POST':
#         q = request.form.get('search')
#         print(q, file=sys.stderr)
#         req = util.request_finnhub_data('https://finnhub.io/api/v1/search', q=q)
#         print(req, file=sys.stderr)
#
#         data = []
#         for r in req['result']:
#             try:
#                 info = yf.Ticker(r['symbol']).info
#                 info['type'] = r['type']
#                 print(info, file=sys.stderr)
#                 if info['longName']:
#                     data.append(info)
#             except:
#                 continue
#
#         data = {
#             'query': q,
#             'result': data,
#         }
#     return render_template('search_result.html', data=data)

@blueprint.route('/autocomplete', methods=['POST', 'GET'])
@login_required
def autocomplete():
    q = request.args.get('term', '')
    req = util.request_finnhub_data('https://finnhub.io/api/v1/search', q=q)
    # req = util.request_iex_data('https://cloud.iexapis.com/stable/search/%s' % q)
    print(req, file=sys.stderr)
    if req:
        # res = [{'label': '%s - %s' % (v['securityName'], 'bbla'), 'value': util.convert_ticker('iex', 'yahoo', v['symbol'])}
        #            for v in req]
        res = [{'label': '%s - %s' % (v['description'], v['type']), 'value': v['symbol']}
               for v in req['result']]
        print(res, file=sys.stderr)
    return json.dumps(res)


@blueprint.route('/index')
@login_required
def index():
    return render_template('index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template(template, segment=segment)

    except TemplateNotFound:
        return render_template('page-404.html'), 404

    except:
        return render_template('page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
