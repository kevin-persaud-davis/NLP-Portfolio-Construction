import requests
import json
import csv
from datetime import date


class Stocktwits():

    def __init__(self):
        self.timestamp = date.today()

    def get_url(self, url=None):
        endpoint_api = requests.get(url=url)
        if endpoint_api.ok:
            return endpoint_api
        else:
            raise ValueError(f"{url} could not be retrieved.")

    def csv_file(self, data_endpoints):
        dict_data = data_endpoints.json()["symbols"]
        date = self.timestamp.strftime("%b-%d-%Y")
        file_name = f"STsymbols_{date}.csv"

        with open(file_name, 'w') as csv_file:
            symbols = csv.DictWriter(csv_file, fieldnames=dict_data[0])
            symbols.writeheader()
            for data in dict_data:
                symbols.writerow(data)
        return symbols


def main():
    first_parameter = "trending"
    second_parameter = "symbols"
    third_parameter = "equities"

    data = Stocktwits()
    get_data = data.get_url(
        url=f"https://api.stocktwits.com/api/2/{first_parameter}/{second_parameter}/{third_parameter}.json")

    return data.csv_file(get_data)


if __name__ == "__main__":
    main()
