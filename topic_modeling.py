import emoji, spacy, gensim, gensim.corpora as corpora, keys, re, tweepy

from datetime import date
from geopy.geocoders import Nominatim
from pprint import pprint
from Tweet import Tweet

# from spacy.lang.en.stop_words import stop_words

nlp = spacy.load("en_core_web_sm")

# Initialize today's date and the geolocator beforehand.
today = date.today().strftime("%Y-%m--%d")
geolocator = Nominatim(user_agent = "AI for Politics")



def preprocessMessage(tweet):

    # Remove emails from the tweet, if any.
    re.sub('\S*@\S*\s?', "", tweet)

    # Remove new line characters from the tweet, if any.
    re.sub('\s+', " ", tweet)

    # Remove distracting single quotes from the tweet, if any.
    re.sub("\'", "", tweet)

    # Remove any URLs from the tweet, if any.
    re.sub("http\S+", "", tweet)

    # Remove any emojis from the tweet, if any.
    tweet = emoji.replace_emoji(tweet, "")

    # Break the sentence(s) into individual tokens/words.
    tweet = tokenize(tweet)

    # Omit stop words and lemmatize the message.
    tweet = remove_stopwords_and_lemmatize(tweet)

    # Is it necessary to create bigram and trigram models now?
   
    return tweet



# Perform topic modeling on the list of tweets.
def buildClustersByTopic(messages_list):
    # Create a dictionary.
    dict = corpora.Dictionary(messages_list)

    # Term document frequency. 'corpus' contains a mapping of word_ids and corresponding word_frequencies.  
    corpus = [dict.doc2bow(text) for text in messages_list]

    # Build the topic model, as shown in the below line.
    # Adjust 'num_topics' accordingly.
    lda_model = gensim.models.ldamodel.LdaModel(corpus = corpus,
                                                id2word = dict,
                                                num_topics = 5, 
                                                random_state = 100,
                                                update_every = 1,
                                                chunksize = 100,
                                                passes = 10,
                                                alpha = 'auto',
                                                per_word_topics = True)

    return lda_model



def remove_stopwords_and_lemmatize(doc):
    sentence = []
    for word in doc:
        if not word.is_stop and not word.is_punct and not word.like_num:
            sentence.append(word.lemma_)

    return sentence

def tokenize(message):
    return nlp(message)



def scrapeTweetsByHashtag(hashtag, numOfTweets):

    tweets = tweepy.Cursor(api.search_tweets, q = hashtag, lang = "en", since_id = today, tweet_mode = "extended").items(numOfTweets)
    tweets_list = []
    
    for tweet in tweets:
        message = tweet.full_text
        location = setLocation(tweet)

        tweets_list.append(Tweet(message, location))

    return tweets_list



# In this method, we will be storing the 'place_id' as the location for the Tweet, since it's been explicitly geotagged.
def scrapeTweetsByLocation(place_id, numOfTweets):
    tweets = tweepy.Cursor(api.search_tweets, q = "place:%s" % place_id, lang = "en", since_id = today, tweet_mode="extended").items(numOfTweets)
    
    messages_list = []
    tweets_list = []
    
    for tweet in tweets:
        message = tweet.full_text
        message = preprocessMessage(message)
        messages_list.append(message)

        location = place_id

        tweets_list.append(Tweet(message, location))

    print(messages_list)
    lda_model = buildClustersByTopic(messages_list)
    pprint(lda_model.print_topics())

    return tweets_list



def scrapeAllTweets(numOfTweets):

    tweets = tweepy.Cursor(api.search_tweets, q = "*", lang = "en", since_id = today, tweet_mode = "extended").items(numOfTweets)
    tweets_list = []
    
    for tweet in tweets:
        message = tweet.full_text
        location = setLocation(tweet)

        tweets_list.append(Tweet(message, location))

    return tweets_list



def setLocation(tweet):
    location = None

    # Try finding the coordinates first, as it gives the most concrete data.
    if tweet.coordinates:
        location = tweet.coordinates.coordinates
        print(location)
        
    # Next up, try tweet.place, which will have at least the full_name and country attributes.
    elif tweet.place:
        location = tweet.place.full_name + ", " + tweet.place.country
        # location = tweet.place.id
        print(location)

    # Lastly, if all else fails, grab the user location. This data is pretty poor, but is at least something. You may not want it, depending on your usage.
    # Note that we need to be extra careful with user input, since it has so much variability.
    elif tweet.user.location:
        location = tweet.user.location
        location = geolocator.geocode(location)

        if location is None:
            print("Invalid location! ", tweet.user.location)
        else:
            print(location)

    else:
        print("None of the above conditons were met! :(")

    return location



# Retrieve all the keys stored in the 'keys.py' file.
api_key = keys.api_key
api_key_secret = keys.api_key_secret
access_token = keys.access_token
access_token_secret = keys.access_token_secret
bearer_token = keys.bearer_token

# Perform authenticatation.
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)










'''
# The below code is the implementation of the first option, where we will be scraping in tweets based on the top five trending hashtags. 

us_woeid = 23424977 

trend_results = api.get_place_trends(us_woeid)

tweets_list = {}

for trend in trend_results[0]["trends"][:1]:
    hashtag = "#" + trend["name"]

    # IMPORTANT: Change the '5' in the following line to 10K once finished. For now, keeping it as '5' will allow for easy and quick testing.
    tweets_list[hashtag] = scrapeTweetsByHashtag(hashtag, 1)

# print(tweets_list)
'''










# The below code is the implementation of the second option, where we will be scraping in 10K tweets for each of big-10 cities everyday. 

big_cities = ["New York City"]

'''
big_cities = ["New York City",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "Philadelphia",
            "San Antonio",
            "San Diego",
            "Dallas",
            "San Jose"]
'''

for city in big_cities:
    places = api.search_geo(query = city, granularity = "city")
    place_id = places[0].id

    for place in places:
        if place.name == city and place.place_type == "city":
            place_id = place.id
            break

    # IMPORTANT: Change the '5' in the following line to 10K once finished. For now, keeping it as '5' will allow for easy and quick testing.
    tweets_list = scrapeTweetsByLocation(place_id, 5)
    # print(tweets_list)











'''
# The below code is the implementation of the third option, where we will be scraping in 100K most recent tweets in a given day.

# IMPORTANT: Change the '5' in the following line to 10K once finished. For now, keeping it as '5' will allow for easy and quick testing.
tweets_list = scrapeAllTweets(5)
print(tweets_list)
'''
