import quandl
import os
import requests
import json
import sys


os.environ['HTTP_PROXY'] = "http://172.16.99.9:3129"
os.environ['HTTPS_PROXY'] = "http://172.16.99.9:3129"

quandl.ApiConfig.api_key = "2RieC3BYU62Z4Z-koxRX"
IEX_API_KEY = "pk_67178ec015c04eae909c3308f69ebf09"


def request_iex_data(url):
    req = requests.get('%s?token=%s')
    json_data = json.loads(req.content)
    print(json_data, file=sys.stderr)