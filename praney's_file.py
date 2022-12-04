from keys import *
import tweepy
import requests
import pandas as pd

client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_key_secret=consumer_key_secret, access_token=access_token, 
                        access_token_secret=access_token_secret, return_type = requests.Response, wait_on_rate_limit=True)

id= client.get_user(username='narendramodi')
user_id = id.json()["data"]["id"]
# tweets= client.get_users_tweets(id = user_id)

# Save data as data frame
# tweets_dict = tweets.json() 
# tweets_data = tweets_dict['data'] 
# df = pd.json_normalize(tweets_data) 
# print(df)

id_list = []
text_list = []
l = 100
first = True

while l == 100:
    # tweets has to be defined first before we can fetch pagination token for next pages, therefore we define bool first to fetch the first page
    if first:
        tweets = client.get_users_tweets(user_id, max_results=100)
        first = False
    else:
        #print(tweets.json())
        tweets = client.get_users_tweets(user_id, max_results=100, pagination_token=tweets.json()["meta"]["next_token"])
        
    # handling cases if the amount of tweets is exact multiplication of 100
    if tweets.json()["data"] is None:
        break
    else:
        for tweet in tweets.json()["data"]:
            id_list.append(tweet["id"])
            text_list.append(tweet["text"])

    l = len(tweets.json()["data"])
    
# Creating a pandas DataFrame with columns id (tweet ID) and text (tweet content)
df = pd.DataFrame({
    'id':id_list,
    'text':text_list
})

print(df)