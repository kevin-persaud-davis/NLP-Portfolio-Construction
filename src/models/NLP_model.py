import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
import pandas as pd
import re
from textblob import TextBlob
import pprint
from settings import DATABASE_PASSWORD

class Database():

    def __init__(self, password):
        self.password = password
        self.host = "localhost"
        self.database = "twitterdb"
        self.user = "root"
        self.charset = "utf8mb4"

    def connect(self, query):

        conn = mysql.connector.connect(
            host=self.host, database=self.database, user=self.user, password=self.password, charset=self.charset)

        if conn.is_connected():

            cursor = conn.cursor()
            query = query
            cursor.execute(query)

            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=[
                            'id', 'symbol', 'tweet', 'user_location', 'user_followercount', 'retweet_count', 'date_time'])

        cursor.close()
        conn.close()

        return df


class Sentiment():

    def __init__(self, query):
        self.date_today = date.today().strftime("%b-%d-%Y")
        self.query = Database(DATABASE_PASSWORD).connect(query)

    def filter(self, tweet):

        tweet_lower = tweet.lower()
        non_RT = re.sub(r'\Art', '', tweet_lower)
        non_url = re.sub(r'https?://[A-Za-z0-9./]+', '', non_RT)
        non_mention = re.sub(r'@[A-Za-z0-9]+', '', non_url)
        non_dollar = re.sub(r'\$[A-Za-z0-9]*', '', non_mention)
        non_dot = re.sub(r'[^a-zA-Z]', ' ', non_dollar)

        return ' '.join(non_dot.split())

    def tweet_sentiment(self, tweet):

        cleaned_tweet = TextBlob(self.filter(tweet))

        if (cleaned_tweet.sentiment.polarity > 0):
            return "positive"
        elif (cleaned_tweet.sentiment.polarity == 0):
            return "neutral"
        else:
            return "negative"

    def tweet_results(self, data_df):

        tweets = []
        tweets_df = data_df

        for tweet in tweets_df.tweet:

            filtered_tweet = " "
            filtered_tweet += self.tweet_sentiment(tweet)

            if filtered_tweet not in tweets:
                tweets.append(filtered_tweet)
            else:
                tweets.append(filtered_tweet)

        return tweets

    def sentiment_column(self, df):

        sentiment_column = self.tweet_results(df)
        return sentiment_column

    def dummy_sentimentdf(self, df):

        df["sentiment"] = self.sentiment_column(df)
        df_dummies = pd.get_dummies(df["sentiment"])
        encoded_df = pd.concat([df, df_dummies], axis=1)

        return encoded_df

    def position_direction(self, df):

        grouped = df["sentiment"].groupby(df["symbol"])
        grouped_df = grouped.size().to_frame()

        neg_count = df[" negative"].groupby(df["symbol"])
        small_df = neg_count.sum().to_frame()

        pos_count = df[" positive"].groupby(df["symbol"])
        big_df = pos_count.sum().to_frame()

        first_merge = small_df.merge(big_df, left_on='symbol', right_on='symbol')
        second_merge = first_merge.merge(grouped_df, left_on='symbol', right_on='symbol')

        second_merge["positive_percent"] = 100 * (second_merge.loc[:, " positive"] / second_merge.loc[:, "sentiment"])
        second_merge["negative_percent"] = 100 * (second_merge.loc[:, " negative"] / second_merge.loc[:, "sentiment"])

        second_merge["direction"] = second_merge.iloc[:, 3] - second_merge.iloc[:, 4]
        second_merge["L/S"] = self.long_short(second_merge)

        return second_merge

    def long_short(self, df):

        dir_df = df
        position_size = {}

        for i in range(len(dir_df)):
            if dir_df.loc[:, "direction"][i] > 0:
                position_size[i] = 1
            else:
                position_size[i] = 0
        return position_size.values()


def main():

    data = Sentiment(
    """SELECT id, symbol, tweet, user_location, user_followercount, retweet_count, date_time 
        FROM stocks;""")

    dummy_df = data.dummy_sentimentdf(data.query)
    position_df = data.position_direction(dummy_df)

    print(f"{data.date_today} Portfolio: \n{position_df}")


if __name__ == "__main__":
    main()
