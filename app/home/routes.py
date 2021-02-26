# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from pandas import DataFrame

from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import app.home.util as util
import numpy as np
import urllib
import requests
import pandas as pd
import json
import sys
import yfinance as yf


@blueprint.route('/stock/<ticker>')
@login_required
def stock(ticker):
    # timeframe = [10*365, 5*365, 365]

    # Yahoo Data
    yahoo = yf.Ticker(ticker)
    df = yf.download(ticker, period='10y').reset_index()
    print(df.head())
    #df = yahoo.history(period='max').reset_index()
    #print(df.head())
    # multitick = {
    #     'date': pd.to_datetime(df['Date']).tolist(),
    #     'close': list(df['Close']),
    #     'volume': list(df['Volume']),
    # }
    tick = [[x['Date'], x['Close']] for x in json.loads(df.to_json(orient='records'))]

    # tick = [(tf, util.get_df_history(df, tf)) for tf in timeframe]

    # PyTrends Data
    pytrend = util.get_pytrends_data(yahoo.info['shortName'].split(' ')[0])
    print('pytrend finished')

    # IEX Data
    iex_tick = util.convert_ticker('yahoo', 'iex', ticker)
    iex = util.get_iex_ticker(iex_tick)
    print('iex finished')

    data = {
        'yahoo': yahoo.info,
        'iex': iex,
        'pytrend': pytrend,
        'tick': tick,
        # 'multi': multitick,
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
