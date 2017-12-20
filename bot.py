#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A bot to tweet screenshots of someone else's tweets"""

import json
import os
import random
import sys
import requests
import tweepy
import heroku3

HEROKU_KEY = sys.argv[1]
HEROKU_APP_NAME = sys.argv[2]
TWEET_URL = "https://twitter.com/{username}/status/{tweet_id}"

def get_twitter_api():
  """Get TWitter API from Heroku config"""
  auth = tweepy.OAuthHandler(HEROKU_CONFIG['CONSUMER_KEY'], HEROKU_CONFIG['CONSUMER_SECRET'])
  auth.set_access_token(HEROKU_CONFIG['ACCESS_KEY'], HEROKU_CONFIG['ACCESS_SECRET'])
  return tweepy.API(auth)

def get_last_checked_off():
  """Get the ID of the last tweet we handled"""
  return HEROKU_CONFIG['LAST_PROCESSED_TWEET_ID']

def build_intro(their_username):
  """Generate the status text for my tweet"""
  intro_template = random.choice(POSSIBLE_INTROS)
  return intro_template.format(**{
      'their_username': their_username
  })

def build_my_tweet(their_tweet):
  """Generate status text for my tweet and a screenshot of their original tweet"""
  local_screenshot = get_tweet_screenshot(their_tweet)
  my_intro = build_intro(their_tweet.user.screen_name)
  return my_intro, local_screenshot

def get_tweet_screenshot(their_tweet):
  """Generate a screenshot for their original tweet"""
  local_file = "temp_{tweet_id}.jpg".format(tweet_id=their_tweet.id)
  their_tweet_url = TWEET_URL.format(username=their_tweet.user.screen_name, tweet_id=their_tweet.id)
  screenshot_url = THUMBNAIL_TEMPLATE.format(tweet_url=their_tweet_url)

  request = requests.get(screenshot_url, stream=True)
  if request.status_code == 200:
    with open(local_file, "wb") as image:
      for chunk in request:
        image.write(chunk)
  return local_file

def check_off(their_tweet):
  """Mark their original tweet as handled so I don't post it again"""
  HEROKU_CONFIG['LAST_PROCESSED_TWEET_ID'] = their_tweet.id

def send_my_tweet(my_tweet_text, local_screenshot):
  """Actually tweet with my own text and the screenshot of their original tweet"""
  TWITTER.update_with_media(local_screenshot, status=my_tweet_text)
  print(my_tweet_text, local_screenshot)

def build_thumbnail_template():
  """Build the thumbnail API endpoint, ready to sub in the URL of the original tweet"""
  template = HEROKU_CONFIG['THUMBNAIL_ENDPOINT']
  template_subs = {
      'api_key': HEROKU_CONFIG['THUMBNAIL_API_KEY'],
      'thumbnail_width': HEROKU_CONFIG['THUMBNAIL_WIDTH'],
      'tweet_url': '{tweet_url}'
  }
  return template.format(**template_subs)

def get_possible_intros():
  """Load possible intros from config, or default if the config is missing"""
  possible_intros = HEROKU_CONFIG['POSSIBLE_INTROS']
  if possible_intros:
    return json.loads(possible_intros)
  return ["So, @{their_username} said..."]

def capture_tweets_for_posterity():
  """Capture tweets in case they... go missing later"""
  their_tweets = TWITTER.user_timeline(
      ORIGINAL_TWEETER,
      count=BATCH_SIZE,
      since_id=LATEST_CAPTURED_TWEET)
  their_tweets.reverse() # i.e. put in chronological order
  for their_tweet in their_tweets:
    their_tweet = TWITTER.get_status(their_tweet.id, tweet_mode='extended')
    my_tweet_text, local_screenshot = build_my_tweet(their_tweet)
    try:
      send_my_tweet(my_tweet_text, local_screenshot)
      check_off(their_tweet)
    finally:
      os.remove(local_screenshot)

if __name__ == '__main__':
  HEROKU_CONN = heroku3.from_key(HEROKU_KEY)
  HEROKU_APP = HEROKU_CONN.apps()[HEROKU_APP_NAME]
  HEROKU_CONFIG = HEROKU_APP.config()

  TWITTER = get_twitter_api()
  ORIGINAL_TWEETER = HEROKU_CONFIG['HELD_TO_ACCOUNT']
  LATEST_CAPTURED_TWEET = get_last_checked_off()
  BATCH_SIZE = HEROKU_CONFIG['BATCH_SIZE']

  POSSIBLE_INTROS = get_possible_intros()
  THUMBNAIL_TEMPLATE = build_thumbnail_template()
  capture_tweets_for_posterity()
