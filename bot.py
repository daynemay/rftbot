#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import calendar
import datetime
import heroku3
import json
import pytz
import sys
import tweepy

HEROKU_KEY = sys.argv[1]
HEROKU_APP_NAME = sys.argv[2]
DATE_FORMAT = 'At {hour}:{minute:02} on {short_month} {day}, {year}'

def get_twitter_api(heroku_config):
  auth = tweepy.OAuthHandler(heroku_config['CONSUMER_KEY'], heroku_config['CONSUMER_SECRET'])
  auth.set_access_token(heroku_config['ACCESS_KEY'], heroku_config['ACCESS_SECRET'])
  return tweepy.API(auth)

def get_timezone(heroku_config):
  return pytz.timezone(heroku_config['USE_TIMEZONE'])

def human_date(datetime):
  """Takes a datetime; returns a short, human-readable string, e.g. At "11:36 on Dec 18, 2017" """
  long_month_name = calendar.month_name[datetime.month]
  short_month_name = long_month_name[0:3]
  date_format_dict = {
    'year': datetime.year,
    'month': long_month_name,
    'short_month': short_month_name,
    'day': datetime.day,
    'hour': datetime.hour,
    'minute': datetime.minute,
  }
  return DATE_FORMAT.format(**date_format_dict)

def get_last_checked_off(heroku_config):
  return heroku_config['LAST_PROCESSED_TWEET_ID']
  
def build_intro(who_said_it, when_they_said_it, timezone):
  their_datetime = timezone.normalize(when_they_said_it.replace(tzinfo=pytz.utc))
  return "{date}, @{who_said_it} said: ".format(**{
    'date': human_date(their_datetime),
    'who_said_it': who_said_it
  })

def build_my_tweet(their_tweet, timezone):
  who_said_it = their_tweet.user.screen_name
  my_intro = build_intro(who_said_it, their_tweet.created_at, timezone)
  return my_intro + their_tweet.full_text

def check_off(their_tweet):
  # Update Heroku config var to record that this tweet has been processed
  heroku_config['LAST_PROCESSED_TWEET_ID'] = their_tweet.id 

def send_my_tweet(my_tweet_text):
  # TODO: send via Tweepy API
  print(my_tweet_text)  

def repeat_tweets_in_case_of_later_deletion(twitter_api, original_tweeter, since_tweet_id, timezone):
  their_tweets = twitter_api.user_timeline(original_tweeter, count=25, since_id=since_tweet_id)
  their_tweets.reverse() # i.e. put in chronological order
  for their_tweet in their_tweets:
    their_tweet = twitter_api.get_status(their_tweet.id, tweet_mode='extended')
    my_tweet_text = build_my_tweet(their_tweet, timezone)
    check_off(their_tweet)
    send_my_tweet(my_tweet_text)

if __name__ == '__main__':
  heroku_conn = heroku3.from_key(HEROKU_KEY)
  heroku_app = heroku_conn.apps()[HEROKU_APP_NAME]
  heroku_config = heroku_app.config()
  
  twitter = get_twitter_api(heroku_config)
  original_tweeter = heroku_config['HELD_TO_ACCOUNT']
  last_repeated_tweet_id = get_last_checked_off(heroku_config)
  timezone = get_timezone(heroku_config)
  repeat_tweets_in_case_of_later_deletion(twitter, original_tweeter, last_repeated_tweet_id, timezone)
