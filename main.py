import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import pandas as pd
import config


class TwitterClient(object):
    def __init__(self):
        self.tweets = []
        self.current = []
        self.name = []
        consumer_key = 'nxSBJTykJucdB9WA8JU0f8Ch6'
        consumer_secret = 'qT9FW8ne020J5WxF1hvLVzmvfFJtatx9yjAX2W5hqrSzCjcOGR'
        access_token = '867467289213321216-TRdoljbC6K2H14BFJstWeUhKWllXpfe'
        access_token_secret = 'rIZ1PnKJxqDb1htddL5TtCI54NmLwJtkc82RwcjCU9FCQ'

        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)

    def get_names(self, username):
        ids = []
        for page in tweepy.Cursor(self.api.friends_ids, screen_name=username).pages():
            ids.extend(page)

        for i in range(0, len(ids)):
            user = self.api.get_user(ids[i])
            screen_name = user.screen_name
            self.name.append(screen_name)
            i += 1
        self.current = self.name
        # print(self.current)

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z1-9]+)|([^0-9A-Za-z \t])|(w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=5):

        try:
            fetched_tweets = self.api.search(q=query, count=count)

            for tweet in fetched_tweets:
                parsed_tweet = {'text': tweet.text, 'sentiment': self.get_tweet_sentiment(tweet.text)}

                if tweet.retweet_count > 0:
                    if parsed_tweet not in self.tweets:
                        self.tweets.append(parsed_tweet)
                else:
                    self.tweets.append(parsed_tweet)
            return self.tweets
        except tweepy.TweepError as e:
            print("Darn! Error: " + str(e))

    def create_list(self, name, description, mode):
        self.api.create_list(name, description=description, mode=mode)

    def racist_check(self, tweets):
        first = [match for match in tweets if "nigga" in match]
        second = [match for match in tweets if "black people" in match]
        third = [match for match in tweets if "white people" in match]
        fourth = [match for match in tweets if "all lives natter" in match]
        self.score = len(first) + len(second) + len(third) + len(fourth)
        #print(self.score)


def main():
    api = TwitterClient()

    name = input("Enter the name of the list you want to create: ")
    description = input("Enter a short description of the list: ")
    mode = input("Do you want your list to be public or not? For public type: 'public' else type 'private'. ")
    # owner_un = input("What is your screen name? (Tip: it usually starts with '@'. Do not include '@' when entering name) ")
    #api.create_list(name, description, mode)

    username = input("Enter the user name: ")
    api.get_names(username)
    friends = api.current

    list_members = []

    for i in range(0, len(friends)):
        #print(friends[i])
        tweets = api.get_tweets(query=f"'{friends[i]}'", count=200)
        api.racist_check(tweets)
        if api.score == 0:
            ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
            ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']

            pos = (100 * len(ptweets) / len(tweets))
            neg = (100 * len(ntweets) / len(tweets))
            if pos > neg:
                list_members.append(friends[i])

    print(list_members)




if __name__ == '__main__':
    main()


# PritishaBaldeo
# HariKirtanRasa
#print(friends[i])
#print("Negative tweets percentage: {0:8.2f} %".format(100*len(ntweets)/len(tweets)))
#print("Positive tweets percentage: {0:8.2f} %".format(100*len(ptweets)/len(tweets)))
#tweepy.API.add_list_members(screen_name=f"'{list_members}'", slug=f"'{name}'", owner_screen_name=f"'{owner_un}'")
#df = pd.DataFrame(list_members)
#df.to_csv('TrustPpl.csv', index=False, header=False)
#df = pd.read_csv('TrustPpl.csv', header=None)