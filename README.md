# rftbot

RFT Bot is a Twitter bot that drives the Twitter account [@realFlotusTrump](http://twitter.com/realFlotusTrump). The bot takes a screenshot of all tweets by @realDonaldTrump and posts a corresponding tweet to @realFlotusTrump with the screenshot, along with a comment randomly selected from a configured pool of candidate comments.

Accessing tweets by @realDonaldTrump, and tweeting from @realFlotusTrump, is done using [Tweepy](http://www.tweepy.org/).

The screenshot is taken using the [thumbnail.ws](https://thumbnail.ws/documentation.html) API.

The tweet posted to @realFlotusTrump is a new, original tweet, i.e. not a retweet or quote tweet, since they may be deleted if the original tweet by @realDonaldTrump is deleted.

The bot runs as a scheduled job on Heroku, and uses the following configuration. All values are required.

|Configuration Key|Sample Value     |Description|
|-----------------|-----------------|-----------|
|`HELD_TO_ACCOUNT`|`realDonaldTrump`|The username whose tweets trigger tweets from this bot|
|`CONSUMER_KEY`|`**********`|The Twitter API consumer key for our Twitter account|
|`CONSUMER_SECRET`|`**********`|The Twitter API consumer secret for our Twitter account|
|`ACCESS_KEY`|`**********`|The Twitter API access key for our Twitter account|
|`ACCESS_SECRET`|`**********`|The Twitter API access secret for our Twitter account|
|`LAST_PROCESSED_TWEET_ID`|`949619270631256064`|Tweet ID. Maintained by the bot to keep track of which tweets have already been seen and handled|
|`POSSIBLE_INTROS`|`["In the words of @{their_username}:", "As @{their_username} said:"]`|JSON list of candidate comments to accompany the screenshot|
|`THUMBNAIL_ENDPOINT`|`https://api.thumbnail.ws/api/{api_key}/thumbnail/get?url={tweet_url}&width={thumbnail_width}`|API endpoint for [thumbnail.ws](https://thumbnail.ws/documentation.html), with fields defined for substitutions|
|`THUMBNAIL_API_KEY`|`**********`|API key for [thumbnail.ws](https://thumbnail.ws/documentation.html)|
|`THUMBNAIL_WIDTH`|`600`|Width in pixels of the screenshot|
|`BATCH_SIZE`|`25`|Count of tweets to retrieve in each call to the Twitter API|

A refactoring is intended to separate the code that implements the triggering behaviour from the code and configuration that is specific to this use case.


