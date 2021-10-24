import requests
import os
from trading_report_analysis import TradingReport
from wazirx_api import wazirx_api_details
import time
from decimal import *
from multiprocessing.pool import ThreadPool as Pool
import pandas as pd
from terminal_formatting import *


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


def get_value_per_token(payloads: dict, trading_report: TradingReport) -> dict:
    value_per_token = {
        ticker: {
            TOTAL_VALUE: Decimal(payloads[ticker][TICKER][BUY]) * Decimal(num_coins),
            BUY: Decimal(payloads[ticker][TICKER][BUY])
        } for ticker, num_coins in trading_report.holdings.items()}
    return value_per_token


def generate_holdings_report(token_info: dict, trading_report: TradingReport) -> pd.DataFrame:
    report_df = pd.DataFrame(columns=['TOKEN', 'CURRENT PRICE', 'HOLDINGS', 'INVESTMENT',
                                      'CURRENT VALUE', 'GAINS (%)'])
    for i, tok in enumerate(trading_report.holdings):
        gains = 100 * ((token_info[tok][TOTAL_VALUE] / trading_report.investment_per_token[tok]) - 1)
        report_df.loc[i] = [tok, token_info[tok][BUY], Decimal(trading_report.holdings[tok]), trading_report.investment_per_token[tok],
                            token_info[tok][TOTAL_VALUE], gains]
    report_df.sort_values(by='CURRENT VALUE', ascending=False, inplace=True, ignore_index=True)
    return report_df


def get_metrics(trading_report: TradingReport, report_df: pd.DataFrame) -> dict:
    metrics = {
        'total_investment': Decimal(trading_report.total_deposits),
        'total_current_value': Decimal(report_df['CURRENT VALUE'].sum()),
    }
    metrics['gains'] = (metrics['total_current_value'] / metrics['total_investment'] - 1) * 100
    metrics['gains_total'] = metrics['total_current_value'] - metrics['total_investment']
    return metrics


def print_report(report_df: pd.DataFrame, trading_report: TradingReport):
    column_length = 18
    metrics = get_metrics(trading_report, report_df)
    total_investment = metrics['total_investment']
    total_current_value = metrics['total_current_value']
    gains, gains_total = metrics['gains'], metrics['gains_total']

    print(f"\n{ef.bold}{fg.yellow}INITIAL INVESTMENT: {RUPEE}{total_investment:.2f}\n", end='\r')
    color = fg.da_green if total_current_value > total_investment else fg.da_red
    print(f"{ef.bold}{color}CURRENT PORTFOLIO : {RUPEE}{total_current_value:.2f}\n", end='\r')
    print(f"{ef.bold}{color}GAINS : {RUPEE}{gains_total:.2f} ({UP_ARROW if gains > 0 else DOWN_ARROW} {gains:.2f} %)\n\n\n",
          end='\r')

    column_string = ''.join([f"{ef.bold}{fg.da_magenta}{col:{column_length}}{BColors.ENDC}" for col in report_df.columns])
    print(f"{column_string}\n\n", end='\x1b[1K\r')
    n = len(report_df.columns)
    for i in range(len(report_df)):
        row_string = ''
        for j in range(len(report_df.columns)):
            color = color_encoding[j]
            text_fmt = text_formatting[j]
            val = report_df.iloc[i][j]
            prefix = prefixes[j]

            if isinstance(color, tuple):
                color = color[int(report_df.iloc[i][-1] > 0)]

            if isinstance(val, Decimal):
                val = f"{float(val):.{2 + 2 * int(j == 2)}f}"

            if isinstance(prefix, tuple):
                prefix = prefix[int(report_df.iloc[i][j] < 0)]

            val = f"{prefix}{' ' * int(j == n - 1)}{val}{' %' * int(j == n - 1)}"

            row_string += f"{text_fmt}{color}{val:{column_length}}"
        print(f"{row_string}\n\n", end='\r')


def main():
    while True:
        trading_report_path = '/Users/raunitdalal/PycharmProjects/myCryptoApp/Trading Reports/trading_report.xlsx'
        payloads = {}
        get_payloads(USDT, payloads)
        trading_report = TradingReport(trading_report_path, Decimal(payloads[USDT][TICKER][BUY]))
        getcontext().prec = 10
        pool_size = 16
        pool = Pool(pool_size)
        for ticker in trading_report.holdings:
            pool.apply_async(get_payloads, (ticker, payloads))
        pool.close()
        pool.join()
        token_info = get_value_per_token(payloads, trading_report)
        os.system('cls' if os.name == 'nt' else 'clear')
        report_df = generate_holdings_report(token_info, trading_report)
        print_report(report_df, trading_report)
        for i in range(10, -1, -1):
            time.sleep(1)
            i = f'{i:0}'
            print(f" {fg.da_green}REFRESHING THE DATA IN: {i.zfill(2)} SECONDS", end='\r')


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    main()

