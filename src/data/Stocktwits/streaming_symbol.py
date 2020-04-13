import requests
import json
import csv
from datetime import date, datetime
import pandas as pd


class Symbol():
    def __init__(self):
        self.date_today = date.today().strftime("%b-%d-%Y")
        self.file_name = f"STsymbols_{self.date_today}.csv"
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


class Stream(Symbol):
    def __init__(self, first_parameter, second_parameter):
        self.first_parameter = first_parameter
        self.second_parameter = second_parameter
        self.symbols = Symbol().formatted_symbols()

    def retrieve_url(self, url):

        stocktwits_api = requests.get(url=url)
        if stocktwits_api.ok:
            return stocktwits_api
        else:
            raise ValueError("{} could not be retrieved.".format(url))

    def metadata(self):

        data = self.run_streams()["messages"]
        all_data = []
        for i in data:
            all_data.append(i["id"])
            all_data.append(i["user"]["username"])
            all_data.append(i["body"])
            all_data.append(i["created_at"])
            all_data.append(i["user"]["followers"])
        return all_data

    def run_streams(self):
        """
        Symbol
        -------
        Returns the most recent 30 messages for the specified symbol. Includes symbol object in response.
        
        User
        -----
        Returns the most recent 30 messages for the specified user. Includes user object in response

        Trending
        ---------
        Returns the most recent 30 messages with trending symbols in the last 5 minutes
        
        Suggested 
        ----------
        Returns the most recent 30 messages from our suggested users, a curated list of quality Stocktwits contributors.

        """
        first_parameter = self.first_parameter
        second_parameter = self.second_parameter
        symbols = self.symbols

        URL = f"https://api.stocktwits.com/api/2/{first_parameter}/{second_parameter}/{symbols}.json"

        data_retrieve = self.retrieve_url(URL)

        return data_retrieve.json()


def main():

    stream = Stream("streams", "symbol")

    print(stream.run_streams())


if __name__ == "__main__":
    main()
