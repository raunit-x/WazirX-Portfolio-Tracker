import requests
import os
from trading_report_analysis import TradingReport
from wazirx_api import wazirx_api_details
import time
from decimal import *
from multiprocessing.pool import ThreadPool as Pool
import pandas as pd
from token_constants import *


def get_payloads(ticker: str, payloads: dict):
    def get_data(tkr, currency=INR):
        url = os.path.join(BASE_API_ENDPOINT, VERSION, 'tickers', tkr + currency)
        response = requests.get(url, params={'market': tkr + currency})
        return response.json()

    data = get_data(ticker.lower())
    if data.get('code') == 2000 or not float(data[TICKER][VOLUME]):
        data = get_data(ticker.lower(), USDT)
        data[TICKER][BUY] = Decimal(float(data[TICKER][BUY]) * float(payloads[USDT][TICKER][BUY]))
    payloads[ticker] = data


def current_value(payloads: dict, trading_report: TradingReport) -> dict:
    value_per_token = {}
    total_value = Decimal('0')
    values = []
    for ticker, num_coins in trading_report.holdings.items():
        buying_price = Decimal(payloads[ticker][TICKER][BUY])
        token_value = Decimal(buying_price) * Decimal(num_coins)
        total_value += token_value
        value_per_token[ticker] = {TOTAL_VALUE: token_value, BUY: buying_price}
        values.append((ticker, token_value))
    values.sort(key=lambda x: -x[1])
    for val in values:
        print(f"{val[0]}: {val[1]}")
    print(f'Current Portfolio Value: {total_value}')
    return value_per_token


def generate_holdings_report(token_info: dict, trading_report: TradingReport) -> pd.DataFrame:
    report_df = pd.DataFrame(columns=['TOKEN', 'CURRENT_PRICE', 'INITIAL_INVESTMENT', 'CURRENT_VALUE', 'GAINS'])
    for i, tok in enumerate(trading_report.holdings):
        gains = 100 * (1 - (trading_report.investment_per_token[tok] / token_info[tok][TOTAL_VALUE]))
        report_df.loc[i] = [tok, token_info[tok][BUY], trading_report.investment_per_token[tok], token_info[tok][TOTAL_VALUE], gains]
    report_df.sort_values(by='INITIAL_INVESTMENT', ascending=False, inplace=True, ignore_index=True)
    return report_df


def print_report(report_df: pd.DataFrame):
    pass


def main():
    trading_report_path = os.path.join(os.getcwd(), 'Trading Reports', 'trading_report.xlsx')
    payloads = {}
    get_payloads(USDT, payloads)
    trading_report = TradingReport(trading_report_path, Decimal(payloads[USDT][TICKER][BUY]))
    getcontext().prec = 10
    pool_size = 16
    start = time.time()
    pool = Pool(pool_size)
    for ticker in trading_report.holdings:
        pool.apply_async(get_payloads, (ticker, payloads))
    pool.close()
    pool.join()
    end = time.time()
    print(f"Time taken for API Calls: {end - start}s")
    token_info = current_value(payloads, trading_report)
    report_df = generate_holdings_report(token_info, trading_report)
    print(report_df)


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    main()

