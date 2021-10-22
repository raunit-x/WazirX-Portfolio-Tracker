import requests
import os
from datetime import datetime
from wazirx_api import wazirx_api_details


def get_payloads():
    payloads = {}
    for ticker in MY_TICKERS:
        url = os.path.join(BASE_API_ENDPOINT, VERSION, 'tickers', ticker)
        response = requests.get(url, params={'market': ticker})
        data = response.json()
        payloads[ticker] = data
    return payloads


def current_value(payloads: dict):
    total_value = 0
    for ticker, payload in payloads.items():
        print(ticker, payload)
        num_coins = MAPPED_HOLDINGS[ticker]
        buying_price = float(payload['ticker']['buy'])
        total_value += buying_price * num_coins
    print(f'Current Portfolio Value: {total_value}')


def main():
    payloads = get_payloads()
    current_value(payloads)
    get_payloads()


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    MY_COIN_TICKERS = ['BTC', 'ADA', 'ETH', 'XLM', 'LINK', 'XRP', 'MATIC', 'REN', 'ZIL', 'VET', 'BTT', 'SC', 'XEM',
                       'POLY']
    MY_HOLDINGS = [0.00809, 94.3, 0.0348, 166.5, 6.31, 74.4, 55.4, 87.7, 779, 670, 12429, 1991, 87, 1]
    MY_TICKERS = [coin_ticker.lower() + 'inr' for coin_ticker in MY_COIN_TICKERS]
    MAPPED_HOLDINGS = {tkr: hold for tkr, hold in zip(MY_TICKERS, MY_HOLDINGS)}
    print(MY_TICKERS)
    main()

