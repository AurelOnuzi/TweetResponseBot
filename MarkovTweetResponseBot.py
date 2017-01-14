import tweepy #twitter based api
import csv #for CSV files to store tweets
import markovify #markov chain generator
import codecs
import re #regex

#Twitter API credentials
CONSUMER_KEY = "MY_CONSUMER_KEY"
CONSUMER_SECRET = "MY_CONSUMER_SECRET"
ACCESS_TOKEN = "MY_ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "MY_ACCESS_SECRET"

#for authorization to twitters api 
class TwitterAuthAcc(object):
    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret,
                 wait_on_rate_limit=False,
                 wait_on_rate_limit_notify=False):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.secure = True
        self.auth.set_access_token(access_token, access_token_secret)
        self.__api = tweepy.API(self.auth,
                                wait_on_rate_limit=wait_on_rate_limit,
                                wait_on_rate_limit_notify=wait_on_rate_limit_notify)

    @property
    def api(self):
        return self.__api


class MyStreamListener(tweepy.StreamListener):
    a = TwitterAuthAcc(CONSUMER_KEY, CONSUMER_SECRET,
                       ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                       wait_on_rate_limit=True,
                       wait_on_rate_limit_notify=True)
    def on_status(self, status):
        if status ==  420:
            print("Request refused due to limit or access, try again later")
            return False
        else:
            # m = "@%s "%(status.user.screen_name)
            # msg = m + _get_all_tweets_(status.user.screen_name)
            # a.api.update_status(msg)
            if "me" in status.text:
                for mentions in status.entities['user_mentions']:
					#change my_twitter_name to be your bots name
                    if "my_twitter_name" == mentions['screen_name'].lower():
                        if (len(status.entities['user_mentions']) > 2):
                            # too many mentions or didn't even mean to mention the bot
                            m = "@%s too many requests or mentions, limit it to one and try again" % (
                            status.user.screen_name)
                            a.api.update_status(m)
                        elif (len(status.entities['user_mentions']) == 1):
                            m = "@%s" % (status.user.screen_name)
                            ms = m + " %s :" % (status.user.screen_name)
                            msg = ms + " " + strip_links(str(_get_all_tweets_(screen_name=status.user.screen_name)))
                            a.api.update_status(msg)
                        elif (len(status.entities['user_mentions']) == 2):
                            for mentions in status.entities['user_mentions']:
                                if "my_twitter_name" == mentions['screen_name'].lower():
                                    continue
                                else:
                                    m = "@%s" % (status.user.screen_name)
                                    ms = m + " %s :" % (mentions['screen_name'])
                                    msg = ms + " " + strip_links(
                                        str(_get_all_tweets_(screen_name=mentions['screen_name'])))
                                    a.api.update_status(msg)

            else:
                for mentions in status.entities['user_mentions']:
                    if "my_twitter_name" == mentions['screen_name'].lower():
                        if len(status.entities['user_mentions']) > 2:
                            m = "@%s too many requests or mentions, limit it to one and try again" % (
                            status.user.screen_name)
                            a.api.update_status(m)
                        elif (len(status.entities['user_mentions']) == 2):
                            for mentions in status.entities['user_mentions']:
                                if "my_twitter_name" == mentions['screen_name'].lower():
                                    continue
                                else:
                                    m = "@%s" % (status.user.screen_name)
                                    ms = m + " %s :" % (mentions['screen_name'])
                                    msg = ms + " " + strip_links(
                                        str(_get_all_tweets_(screen_name=mentions['screen_name'])))
                                    a.api.update_status(msg)
                                    # else didn't mean to mention bot so ignore the tweet

#to remove almost all links in tweets (if you do not want to remove links, remove the strip links from the above code)
def strip_links(text):
    link_regex    = re.compile('((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', re.DOTALL)
    links         = re.findall(link_regex, text)
    for link in links:
        text = text.replace(link[0], '')
    return text

#gets all tweets from a CSV file, and generates a Markov-chain tweet response 
def _get_all_tweets_(screen_name):
    a = TwitterAuthAcc(CONSUMER_KEY, CONSUMER_SECRET,
                         ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                         wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)
    api = a.api

    fopen = (open('%s_tweets.csv' % screen_name,'w',encoding='utf-8'))
    csvWriter = csv.writer(fopen)
	
	#removing retweets
    for tweet in tweepy.Cursor(api.user_timeline, screen_name= screen_name,exclude_replies=True,include_rts=False).items():
        try:
            if not tweet.retweeted and 'RT @' not in tweet.text:
                csvWriter.writerow([tweet.text])
            else:
                continue

        except StopIteration:
            break
    fopen.close()

    with codecs.open('%s_tweets.csv' % screen_name,"r","utf-8") as f:
        text = f.read()

    text_model = markovify.Text(text,state_size=2)
    fopen.close()
	
	#test the following numbers out and see what works for you, sometimes a response may exceed the 140 limit 
    # 140 is the limit in a tweet, minus screen name length, 25 for the twitter handle and other things at the start of a msg
	
	#return text_model.make_short_sentence(tries=100,char_limit=140-(len(screen_name)+1))
    return text_model.make_short_sentence(tries=100,char_limit=((140-25)-(len(screen_name))))
    
if __name__ == "__main__":
    a = TwitterAuthAcc(CONSUMER_KEY, CONSUMER_SECRET,
                         ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                         wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)

    TwitStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=a.auth,listener=TwitStreamListener)
	#you can track other keywords if desired, just change the line below
    myStream.filter(track=['my_twitter_name'],async=True)