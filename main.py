import requests
import os
from trading_report_analysis import TradingReport
from wazirx_api import wazirx_api_details
import time
from decimal import *
from multiprocessing.pool import ThreadPool as Pool
import pandas as pd
from token_constants import *
from terminal_formatting import *
from sty import fg, ef


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
    value_per_token = {}
    total_value = Decimal('0')
    for ticker, num_coins in trading_report.holdings.items():
        buying_price = Decimal(payloads[ticker][TICKER][BUY])
        token_value = Decimal(buying_price) * Decimal(num_coins)
        total_value += token_value
        value_per_token[ticker] = {TOTAL_VALUE: token_value, BUY: buying_price}
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


def print_report(report_df: pd.DataFrame, trading_report: TradingReport):
    total_investment = trading_report.total_deposits
    total_current_value = report_df['CURRENT VALUE'].sum()
    gains = (total_current_value / total_investment - 1) * 100
    gains_total = total_current_value - total_investment
    print(f"\n{ef.bold}{fg.yellow}INITIAL INVESTMENT: {RUPEE}{total_investment:.2f}\n", end='\r')
    color = fg.da_green if total_current_value > total_investment else fg.da_red
    print(f"{ef.bold}{color}CURRENT PORTFOLIO : {RUPEE}{total_current_value:.2f}\n", end='\r')
    print(f"{ef.bold}{color}GAINS : {RUPEE}{gains_total:.2f} ({UP_ARROW if gains > 0 else DOWN_ARROW} {gains:.2f} %)\n\n\n",
          end='\r')
    # print()
    color_encoding = [fg.li_cyan, (fg.li_red, fg.da_green), fg.cyan, fg.yellow, (fg.li_red, fg.da_green),
                      (fg.li_red, fg.da_green)]
    text_formatting = [ef.bold, ef.bold, ef.bold, '', ef.bold, ef.bold]
    prefixes = ['', RUPEE, '', RUPEE, RUPEE, (UP_ARROW, DOWN_ARROW)]
    column_string = ''.join([f"{ef.bold}{fg.da_magenta}{col:18}{BColors.ENDC}" for col in report_df.columns])
    print(f"{column_string}\n\n", end='\x1b[1K\r')
    for i in range(len(report_df)):
        row_string = ''
        for j in range(len(report_df.columns)):
            color = color_encoding[j]
            text_fmt = text_formatting[j]
            if isinstance(color, tuple):
                color = color[int(report_df.iloc[i][-1] > 0)]
            val = report_df.iloc[i][j]
            if isinstance(val, Decimal):
                if j == 2:
                    val = f"{float(val):.4f}"
                else:
                    val = f"{float(val):.2f}"
            prefix = prefixes[j]
            if isinstance(prefix, tuple):
                prefix = prefix[int(report_df.iloc[i][j] < 0)]
            # val = f"{prefix}{val}"
            if j == len(report_df.columns) - 1:
                val = f"{prefix} {val} %"
            else:
                val = f"{prefix}{val}"
            row_string += f"{text_fmt}{color}{val:18}"
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
        # print(f"\n Hello ", end='\r')
        token_info = get_value_per_token(payloads, trading_report)
        os.system('cls' if os.name == 'nt' else 'clear')
        # for i in range(10):
        #     time.sleep(0.02)
        #     progress_bar(i, 10)
        report_df = generate_holdings_report(token_info, trading_report)
        print_report(report_df, trading_report)
        for i in range(10, -1, -1):
            time.sleep(1)
            i = f'{i:0}'
            print(f" {fg.da_green}REFRESHING THE DATA IN: {i.zfill(2)} SECONDS", end='\r')
        # time.sleep(10)


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    main()

