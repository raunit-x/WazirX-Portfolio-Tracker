import requests
import os
from trading_report_analysis import TradingReport, trading_report
from wazirx_api import wazirx_api_details
import time
import threading
from decimal import *
from multiprocessing.pool import ThreadPool as Pool


def get_payloads(ticker: str, payloads: dict):
    def get_data(tkr, currency='inr'):
        url = os.path.join(BASE_API_ENDPOINT, VERSION, 'tickers', tkr + currency)
        response = requests.get(url, params={'market': tkr + currency})
        return response.json()

    data = get_data(ticker.lower())
    if data.get('code') == 2000 or not float(data['ticker']['vol']):
        data = get_data(ticker.lower(), 'usdt')
        data['ticker']['buy'] = Decimal(float(data['ticker']['buy']) * float(payloads['usdt']['ticker']['buy']))
    payloads[ticker] = data


def current_value(payloads: dict):
    total_value = Decimal('0')
    values = []
    print(payloads.keys())
    for ticker, num_coins in trading_report.holdings.items():
        buying_price = Decimal(payloads[ticker]['ticker']['buy'])
        token_value = Decimal(buying_price) * Decimal(num_coins)
        total_value += token_value
        values.append((ticker, token_value))
    values.sort(key=lambda val: -val[1])
    for val in values:
        print(f"{val[0]}: {val[1]}")
    print(f'Current Portfolio Value: {total_value}')


def main():
    getcontext().prec = 10
    pool_size = 16
    payloads = {}
    start = time.time()
    pool = Pool(pool_size)
    get_payloads('usdt', payloads)
    for ticker in trading_report.holdings:
        pool.apply_async(get_payloads, (ticker, payloads))
    pool.close()
    pool.join()
    end = time.time()
    print(f"Time taken for API Calls: {end - start}s")
    current_value(payloads)


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    main()

