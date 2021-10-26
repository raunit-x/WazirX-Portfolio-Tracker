import requests
import os
from trading_report_analysis import TradingReport
from wazirx_api import wazirx_api_details
import time
from decimal import *
from multiprocessing.pool import ThreadPool as Pool
import pandas as pd
from terminal_formatting import *
import argparse
from utils import *


def get_payloads(ticker: str, payloads: dict):
    def get_data(tkr, currency=INR):
        url = os.path.join(BASE_API_ENDPOINT, VERSION, 'tickers', tkr + currency.lower())
        response = requests.get(url, params={'market': tkr + currency})
        return response.json()

    currency = INR.upper()
    data = get_data(ticker.lower())
    if data.get('code') == 2000 or not float(data[TICKER][VOLUME]):
        currency = USDT.upper()
        data = get_data(ticker.lower(), USDT)

    data[TICKER][ORIGINAL] = Decimal(float(data[TICKER][BUY]))
    data[TICKER][BUY] = data[TICKER][ORIGINAL] * payloads[currency.lower()][BUY]

    payloads[ticker] = {BUY: data[TICKER][BUY], ORIGINAL: data[TICKER][ORIGINAL], 'currency': currency}


def get_token_info(payloads: dict, trading_report: TradingReport) -> dict:
    token_info = {
        ticker: {
            TOTAL_VALUE: Decimal(payloads[ticker][BUY]) * Decimal(num_coins),
            BUY: Decimal(payloads[ticker][BUY]),
            CURRENCY: payloads[ticker][CURRENCY],
            ORIGINAL: payloads[ticker][ORIGINAL]
        } for ticker, num_coins in trading_report.holdings.items()}
    return token_info


def populate_trading_currency_per_token(payloads: dict, trading_report: TradingReport):
    trading_report.trading_currency_per_token = {
        ticker: payloads[ticker][CURRENCY] for ticker in trading_report.holdings
    }


def generate_holdings_report(token_info: dict, trading_report: TradingReport, col) -> pd.DataFrame:
    report_df = pd.DataFrame(columns=['TOKEN', 'CURRENT PRICE', 'HOLDINGS', 'INVESTMENT',
                                      'CURRENT VALUE', 'GAINS (%)'])
    for col_name in report_df.columns:
        if col and (col in "_".join(col_name.lower().split()) or col in col_name.lower()):
            col = col_name
            break
    else:
        col = 'CURRENT VALUE'
    for i, tok in enumerate(trading_report.holdings):
        gains = 100 * ((token_info[tok][TOTAL_VALUE] / trading_report.investment_per_token[tok]) - 1)
        report_df.loc[i] = [tok, token_info[tok][ORIGINAL], Decimal(trading_report.holdings[tok]), trading_report.investment_per_token[tok],
                            token_info[tok][TOTAL_VALUE], gains]
    report_df.sort_values(by=col, ascending=False, inplace=True, ignore_index=True)
    return report_df


def get_metrics(trading_report: TradingReport, report_df: pd.DataFrame) -> dict:
    metrics = {
        'total_investment': Decimal(trading_report.total_deposits) - Decimal(float(trading_report.total_withdrawals)),
        'total_current_value': Decimal(report_df['CURRENT VALUE'].sum()) + trading_report.current_balance,
    }
    metrics['gains'] = (metrics['total_current_value'] / metrics['total_investment'] - 1) * 100
    metrics['gains_total'] = metrics['total_current_value'] - metrics['total_investment']
    return metrics


def print_metrics(metrics: dict):
    total_investment = metrics['total_investment']
    total_current_value = metrics['total_current_value']
    gains, gains_total = metrics['gains'], metrics['gains_total']

    print(f"\n{ef.bold}{fg.li_yellow}INITIAL INVESTMENT: {rs.bold_dim}{RUPEE}{total_investment:.2f}\n", end='\r')
    color = fg.li_green if total_current_value > total_investment else fg.li_red
    print(f"{ef.bold}{color}CURRENT PORTFOLIO : {rs.bold_dim}{RUPEE}{total_current_value:.2f}\n", end='\r')
    print(
        f"{ef.bold}{color}GAINS : {rs.bold_dim}{RUPEE}{gains_total:.2f} ({UP_ARROW if gains > 0 else DOWN_ARROW} {gains:.2f} %)\n\n\n",
        end='\r')


def print_report(report_df: pd.DataFrame, trading_report: TradingReport, column_length=18):
    print_metrics(get_metrics(trading_report, report_df))
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

            if prefix == CURRENCY:
                prefix = TOKEN_SYMBOLS[trading_report.trading_currency_per_token[report_df.iloc[i][0]]]

            symbol = TOKEN_SYMBOLS.get(val, '')
            if not j and symbol:
                symbol = f" ({symbol})"

            val = f"{prefix}{' ' * int(j == n - 1)}{val}{symbol}{' %' * int(j == n - 1)}"

            row_string += f"{text_fmt}{color}{val:{column_length}}"
        print(f"{row_string}\n\n", end='\r')


def valid_payloads(payloads: dict, trading_report: TradingReport):
    for token in trading_report.holdings:
        print(token, payloads.get(token))
    return all(token in payloads for token in trading_report.holdings)


def print_to_terminal(token_info: dict, trading_report: TradingReport, args, column_length=18):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{' ':{2 * column_length}}{ef.inverse}{ef.bold}{fg.li_cyan}{BColors.UNDERLINE}{ef.italic}"
          f"WAZIRX{rs.italic}{fg.li_yellow} PORTFOLIO TRACKER{rs.bold_dim}{BColors.ENDC}{rs.inverse}\n")
    print(f"{fg.cyan}UDST ({TOKEN_SYMBOLS['USDT']}) to INR: "
          f"{ef.bold}{RUPEE}{float(trading_report.usdt_to_inr):.2f}{rs.dim_bold}")
    report_df = generate_holdings_report(token_info, trading_report, col=args.sort_by_column)
    print_report(report_df, trading_report, column_length)
    for i in range(10, -1, -1):
        time.sleep(1)
        i = f'{i:0}'
        print(f" {ef.bold}{fg.da_green}REFRESHING DATA IN: {rs.bold_dim}{fg.cyan}{i.zfill(2)} SECONDS{rs.dim_bold}",
              end='\r')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tp', '--trading_report_path', type=str, help='Trading report path')
    parser.add_argument('-col', '--sort_by_column', type=str, help="Column to sort with [gains, current_value, "
                                                                   "investment, current_price]")
    args = parser.parse_args()
    column_length = 18
    while True:
        trading_report_path = args.trading_report_path or os.environ.get('TRADING_REPORT_PATH', None)
        payloads = {INR: {BUY: Decimal('1')}}
        get_payloads(USDT, payloads)
        trading_report = TradingReport(trading_report_path, Decimal(payloads[USDT][BUY]))
        getcontext().prec = 10
        pool_size = 16  # I have an 8 core CPU
        pool = Pool(pool_size)
        for ticker in trading_report.holdings:
            pool.apply_async(get_payloads, (ticker, payloads))
        pool.close()
        pool.join()
        if valid_payloads(payloads, trading_report):
            save_to_pickle(payloads)
        payloads = load_from_pickle()
        token_info = get_token_info(payloads, trading_report)
        populate_trading_currency_per_token(payloads, trading_report)
        print_to_terminal(token_info, trading_report, args, column_length)


if __name__ == '__main__':
    BASE_API_ENDPOINT = wazirx_api_details.BASE_API_ENDPOINT
    VERSION = wazirx_api_details.VERSION
    main()

