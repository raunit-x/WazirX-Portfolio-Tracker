import pandas as pd
import os


class TradingReportAnalysis:
    def __init__(self, trading_report_path: str):
        try:
            self.trading_report: dict = self.read_excel(trading_report_path)
            self.excel_sheets = list(self.trading_report.keys())
        except FileNotFoundError as e:
            print(f"{e}: {trading_report_path}")
            return
        getcontext().prec = 30
        self.total_deposits = 0
        self.total_withdrawals = 0
        self.holdings = {}
        self.order_history = {}
        self.investment_per_token = {}
        self.internal_fee = 0
        self.external_fee = 0
        self.current_balance = 0
        self.usdt_to_inr = 77.8
        self.read_account_balance(self.trading_report['Account Balance'])
        for sheet_name in self.excel_sheets:
            attr_name = f'read_{"_".join(sheet_name.lower().split())}'
            if attr_name not in self.__dir__() or attr_name == 'Account Balance':
                continue
            self.__getattribute__(attr_name)(self.trading_report[sheet_name])

    @staticmethod
    def read_excel(path):
        return pd.read_excel(path, sheet_name=None)

    def read_deposits_and_withdrawals(self, df: pd.DataFrame):
        deposits = df[df['Transaction'] == 'Deposit']['Volume'].sum()
        withdrawals = df[df['Transaction'] == 'Withdrawal']['Volume'].sum()
        self.total_deposits = deposits
        self.total_withdrawals = withdrawals

    def read_account_balance(self, df: pd.DataFrame):
        self.holdings = {tok: bal for tok, bal in zip(df['Token'], df['Balance'])}

    def read_exchange_trades(self, df: pd.DataFrame):
        for i in range(len(df)):
            tok = df.iloc[i]['Market']
            price = df.iloc[i]['Price']
            trade = int(df.iloc[i]['Trade'] == 'Sell') * -2 + 1
            vol = df.iloc[i]['Volume']
            fee = df.iloc[i]['Fee']
            if 'USDT' in tok:
                tok = tok.split('USDT')[0]
                fee *= self.usdt_to_inr
                price *= self.usdt_to_inr
            elif 'INR' in tok:
                tok = tok.split('INR')[0]
            self.internal_fee += fee
            if tok not in self.order_history:
                self.order_history[tok] = []
            self.order_history[tok].append((price, vol, trade))

        for tok, orders in self.order_history.items():
            if tok in self.holdings:
                self.investment_per_token[tok] = sum(val[0] * val[1] * val[-1] for val in orders)

    def read_account_ledger(self, df: pd.DataFrame):
        self.current_balance = df['Balance'][0]


def main():
    trading_report_path = os.path.join(os.getcwd(), 'Trading Reports', 'trading_report.xlsx')
    trading_report = TradingReportAnalysis(trading_report_path)


if __name__ == '__main__':
    main()
