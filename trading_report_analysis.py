import pandas as pd


def read_excel(path):
    df = pd.read_excel(path, sheet_name=None)
    return df


def main():
    trading_report_path = '/Users/raunitdalal/Downloads/WazirX_TradeReport_2021-07-31_2021-10-22.xlsx'
