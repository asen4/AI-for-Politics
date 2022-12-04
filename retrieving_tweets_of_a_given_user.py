'''
import tweepy
import pandas as pd

# Read all the credentials from the config file.
# I figured it would be easier to save the credentials in a config file because it would be safer, instead of hard-coding them here.
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# Do authenticatation.
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Obtain tweets from a specific user account below.
user = input("Please enter a username.")
limit = 300

tweets = tweepy.Cursor(api.user_timeline, screen_name = user, count = 200, tweet_mode = 'extended').items(limit)

# For visual purposes, create a DataFrame to organize the tweets.
columns = ['Users', 'Tweets']
data = []

for tweet in tweets:
    data.append([tweet.user.screen_name, tweet.full_text])

df = pd.DataFrame(data, columns = columns)

print(df)
'''