import pandas as pd
from decimal import *


class TradingReport:
    def __init__(self, trading_report_path: str, usdt_to_inr=Decimal('77.8')):
        try:
            self.trading_report: dict = self.read_excel(trading_report_path)
            self.excel_sheets = list(self.trading_report.keys())
        except FileNotFoundError as e:
            print(f"{e}: {trading_report_path}")
            return
        getcontext().prec = 10
        self.total_deposits = Decimal('0')
        self.total_withdrawals = Decimal('0')
        self.holdings = {}
        self.order_history = {}
        self.investment_per_token = {}
        self.external_fee = Decimal('0')
        self.current_balance = Decimal('0')
        self.usdt_to_inr = usdt_to_inr
        self.read_account_balance(self.trading_report['Account Balance'])
        self.trading_currency_per_token = {}
        for sheet_name in self.excel_sheets:
            attr_name = f'read_{"_".join(sheet_name.lower().split())}'
            if attr_name not in self.__dir__() or attr_name == 'Account Balance':
                continue
            self.__getattribute__(attr_name)(self.trading_report[sheet_name])

    @staticmethod
    def read_excel(path):
        return pd.read_excel(path, sheet_name=None)

    def read_deposits_and_withdrawals(self, df: pd.DataFrame):
        deposits = df[df['Transaction'] == 'Deposit']['Volume'].apply(lambda val: Decimal(val)).sum()
        withdrawals = df[df['Transaction'] == 'Withdrawal']['Volume'].apply(lambda val: Decimal(val)).sum()
        self.total_deposits = deposits
        self.total_withdrawals = withdrawals

    def read_account_balance(self, df: pd.DataFrame):
        self.holdings = {tok: bal for tok, bal in zip(df['Token'], df['Balance'])}

    def add_usdt_to_account_balance(self):
        if not self.holdings.get('USDT'):
            return
        self.current_balance += Decimal(self.holdings['USDT']) * self.usdt_to_inr
        self.holdings.pop('USDT')

    def read_exchange_trades(self, df: pd.DataFrame):
        for i in range(len(df)):
            tok = df.iloc[i]['Market']
            price = Decimal(df.iloc[i]['Price'])
            trade = Decimal(int(df.iloc[i]['Trade'] == 'Sell') * -2 + 1)
            vol = Decimal(df.iloc[i]['Volume'])
            if 'USDT' in tok:
                tok = tok.split('USDT')[0]
                price *= self.usdt_to_inr
            elif 'INR' in tok:
                tok = tok.split('INR')[0]
            if tok not in self.order_history:
                self.order_history[tok] = []
            self.order_history[tok].append((price, vol, trade))

        for tok, orders in self.order_history.items():
            if tok in self.holdings:
                self.investment_per_token[tok] = sum(val[0] * val[1] * val[-1] for val in orders)

    def read_account_ledger(self, df: pd.DataFrame):
        self.current_balance = Decimal(df['Balance'][0])
        self.add_usdt_to_account_balance()
