import requests
from datetime import date, datetime
import subprocess
import pandas as pd
import os
import base64
import json
import mysql.connector
from mysql.connector import Error
from settings import DATABASE_PASSWORD, CONSUMER_KEY, CONSUMER_SECRET

CONSUMER_KEY = CONSUMER_KEY
CONSUMER_SECRET = CONSUMER_SECRET


class Symbol():
    def __init__(self):
        self.date_today = date.today().strftime("%b-%d-%Y")
        self.file_name = f"../data/STsymbols_{self.date_today}.csv"

    def read_file(self, file_name):
        symbols_file = pd.read_csv(file_name)
        df = symbols_file.copy()

        return {k: v for k, v in enumerate(df.loc[:, "symbol"])}


class Key():

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def encoding(self):
        key_secret = f"{self.consumer_key}:{self.consumer_secret}".encode("ascii")
        b64_encoded_key = base64.b64encode(key_secret)
        b64_encoded_key = b64_encoded_key.decode("ascii")
        base_url = "https://api.twitter.com/"
        auth_url = "{}oauth2/token".format(base_url)
        auth_headers = {
            "Authorization": "Basic {}".format(b64_encoded_key),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        auth_data = {"grant_type": "client_credentials"}
        auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)

        return auth_resp.json()["access_token"]


class TwitterSearch(Key):

    def __init__(self):
        self.base_url = "https://api.twitter.com/"
        self.access_token = Key(CONSUMER_KEY, CONSUMER_SECRET).encoding()

    def search_endpoint(self, ACCESS_TOKEN, query_parameter=None):

        search_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        search_params = {
            'q': f'${query_parameter}',
            'result_type': 'recent',
            'count': 100,
            'lang': 'en',
            'include_entities': False
        }
        search_url = f"{self.base_url}1.1/search/tweets.json"
        search_response = requests.get(search_url, headers=search_headers, params=search_params)

        return search_response.json()["statuses"]

    def rate_limit(self, ACCESS_TOKEN):

        search_headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        url = 'https://api.twitter.com/1.1/application/rate_limit_status.json'

        search_request_resp = requests.get(url, headers=search_headers)
        rate_return = json.loads(search_request_resp.content)['resources']['search']

        return rate_return

    def search_metadata(self, symbol):
        """Create list of all tweets for each symbol and desired parameters"""

        metadata = []

        for i in self.search_endpoint(ACCESS_TOKEN=self.access_token, query_parameter=f"{symbol}"):
            metadata.append(i["id"])
            metadata.append(f"{symbol}")
            metadata.append(i["created_at"])
            metadata.append(i["text"])
            metadata.append(i["user"]["id"])
            metadata.append(i["user"]["location"])
            metadata.append(i["user"]["followers_count"])
            metadata.append(i["user"]["verified"])
            metadata.append(i["retweet_count"])
            metadata.append(i["favorite_count"])

        return metadata

    def nested_list(self, data):
        """Split data on each symbol name based on specified index"""

        data_list = []

        for item in data:
            split_list = [i for i in range(10, (len(item)), 10)]
            res = [item[i: j]
                   for i, j in zip([0] + split_list, split_list + [None])]
            data_list.append(res)

        return data_list


class Database():

    def __init__(self, password):
        self.password = password

    def connect(self, tweet_id, symbol, created_at, tweet, user_id, user_location, user_followercount, user_verified, retweet_count, favorite_count):
        """
        Insert specified twitter metadata into database
        """

        try:
            conn = mysql.connector.connect(host='localhost',
                                           database='twitterdb',
                                           user='root',
                                           password=self.password,
                                           charset='utf8mb4')

            if conn.is_connected():
                cursor = conn.cursor()

                query = """INSERT INTO stocks 
                (tweet_id, symbol, created_at, tweet, user_id, user_location, user_followercount, user_verified, retweet_count, favorite_count) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                cursor.execute(query, (tweet_id, symbol, created_at, tweet, user_id, user_location,
                                       user_followercount, user_verified, retweet_count, favorite_count))
                conn.commit()

        except IndexError as e:
            print(e)

        cursor.close()
        conn.close()

        return


def main():

    twitter_key = TwitterSearch()

    symbols_today = Symbol()
    tickers = symbols_today.read_file(symbols_today.file_name)
    print(tickers)

    ticker_data = [twitter_key.search_metadata(
        tickers[i]) for i in range(len(tickers))]
    split_data = twitter_key.nested_list(ticker_data)

    db = Database(DATABASE_PASSWORD)
    for i in range(len(split_data)):
        for symbol_item in split_data[i]:
            db.connect(symbol_item[0], symbol_item[1], symbol_item[2], symbol_item[3], symbol_item[4],
                       symbol_item[5], symbol_item[6], symbol_item[7], symbol_item[8], symbol_item[9])
            print("Success")

    print(twitter_key.rate_limit(twitter_key.access_token))


if __name__ == "__main__":
    main()
