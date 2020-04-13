import requests
import csv
import json
import os
import pandas as pd
from datetime import datetime, date
import time
import subprocess
from settings import IEX_TOKEN

class Symbol():
    def __init__(self):
        self.date_today = date.today().strftime("%b-%d-%Y")
        self.file_name = f"../stocktwitsAPI/STsymbols_{self.date_today}.csv"
        self.tickers = self.read_file(self.file_name)

    def read_file(self, file_name):
        symbols_file = pd.read_csv(file_name)
        df = symbols_file.copy()

        return {k: v for k, v in enumerate(df.loc[:, "symbol"])}

    def formatted_symbols(self):
        ticker_string = ''
        for i in self.tickers.values():
            ticker_string += ''.join(f"{i},")
        return ticker_string


class Prices(Symbol):
    def __init__(self, token):
        self.token = token
        self.symbols = Symbol().formatted_symbols()
        self.time = datetime.now().strftime("%d-%m-%Y")
        self.data = requests.get(f"https://cloud.iexapis.com/stable/tops/last?symbols={self.symbols}&token={self.token}").json()

    def IEX_file(self, obj_data):
        """Turn data into csv file"""
        column_headers = ["symbol", "price", "size","time"]  
        file_name = f'IEXtickerprices_{self.time}.csv'

        with open(file_name, 'a', newline='') as csv_file:
            symbols = csv.DictWriter(csv_file, fieldnames=column_headers)

            for data in obj_data:
                symbols.writerow(data)
        return symbols


def main():
    TOKEN = IEX_TOKEN
    price = Prices(TOKEN)
    price.IEX_file(price.data)

    print("done")


if __name__ == "__main__":
    main()