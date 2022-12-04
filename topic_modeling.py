from datetime import date
from geopy.geocoders import Nominatim
import keys
import tweepy
from Tweet import Tweet

from pprint import pprint
import gensim
import gensim.corpora as corpora
import re
import spacy
import string

from nltk.corpus import stopwords

# Add some commonly used stop words into 'stop_words.'
stop_words = stopwords.words('english')
stop_words += list(string.punctuation)
stop_words += ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

# Initialize today's date and the geolocator beforehand.
today = date.today().strftime("%Y-%m--%d")
geolocator = Nominatim(user_agent = "AI for Politics")



def preprocessMessage(tweets_list):
    # Remove emails from the tweets, if any.
    tweets_list = [re.sub('\S*@\S*\s?', "", tweet) for tweet in tweets_list]

    # Remove new line characters from the tweets, if any.
    tweets_list = [re.sub('\s+', " ", tweet) for tweet in tweets_list]

    # Remove distracting single quotes from the tweets, if any.
    tweets_list = [re.sub("\'", "", tweet) for tweet in tweets_list]

    # Remove any URL from the tweets, if any.
    tweets_list = [re.sub("http\S+", "", tweet) for tweet in tweets_list]

    # Break the sentence(s) into individual words.
    tweets_list = list(tokenize(tweets_list))

    # Omit stop words.
    tweets_list = remove_stopwords(tweets_list)

    # Build the bigram and trigram models, if needed.
    # The higher the values of these parameters , the harder its for a word to be combined to bigram.

    bigram = gensim.models.Phrases(tweets_list, min_count = 5, threshold = 100)
    # trigram = gensim.models.Phrases(bigram[message], threshold=100)

    bigram_mod = gensim.models.phrases.Phraser(bigram)
    # trigram_mod = gensim.models.phrases.Phraser(trigram)

    # Form bigrams.
    tweet_bigrams = [bigram_mod[word] for word in tweets_list]

    # Perform lemmatization, keeping only nouns, adjectives, adverbs, and verbs.
    tweets_list = lemmatization(tweet_bigrams, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    
    return tweets_list



# Perform topic modeling on the list of tweets.
def buildClustersByTopic(messages_list):
    # Create a dictionary.
    dict = corpora.Dictionary(messages_list)

    # Term document frequency.  
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



def remove_stopwords(texts):
    return [[word for word in gensim.utils.simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]



def tokenize(sentences):
    for sentence in sentences:
        yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))



def lemmatization(texts, allowed_postags):
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out



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
        messages_list.append(message)
        location = place_id

        tweets_list.append(Tweet(message, location))

    messages_list = preprocessMessage(messages_list)
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
consumer_key = keys.consumer_key
consumer_secret = keys.consumer_secret

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

    if " " in city:
        for place in places:
            if place.name == city and place.place_type == "city":
                place_id = place.id
                break

    # IMPORTANT: Change the '1' in the following line to 10K once finished. For now, keeping it as '1' will allow for easy and quick testing.
    tweets_list = scrapeTweetsByLocation(place_id, 5)
    # print(tweets_list)











'''
# The below code is the implementation of the third option, where we will be scraping in 100K most recent tweets in a given day.

# IMPORTANT: Change the '5' in the following line to 10K once finished. For now, keeping it as '5' will allow for easy and quick testing.
tweets_list = scrapeAllTweets(5)
print(tweets_list)
'''