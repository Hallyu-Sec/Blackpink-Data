#!/usr/bin/env python3
import os
import tweepy
from PIL import Image, ImageFont, ImageDraw 

# Get Twitter API keys
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
access_token = os.environ.get('TWITTER_ACCESS_KEY')
access_token_secret = os.environ.get('TWITTER_ACCESS_SECRET')

test = False

def set_test_mode():
    global test 
    test = True

def twitter_repost(twitter):
    print("Starting Twitter repost task...")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    print("Fetching tweets for {}".format(twitter["url"]))

    if twitter["last_tweet_id"] is not None:
        tweets = api.user_timeline(screen_name = twitter["url"], 
                                since_id = twitter["last_tweet_id"],
                                include_rts = False,
                                # extended mode to get full text
                                tweet_mode = "extended"
                                )
    else:
        tweets = api.user_timeline(screen_name = twitter["url"], 
                                # Take only the last tweet
                                count = 1,
                                include_rts = False,
                                # extended mode to get full text
                                tweet_mode = "extended"
                                )

    for tweet in tweets:
        print("Retwitting this tweet from @{}".format(twitter["url"]))
        print("Tweet ID: {}".format(tweet.id))
        print("Datetime: {}".format(tweet.created_at))
        print(tweet.full_text[:20])
        if test is False:
            api.retweet(tweet.id)

    if len(tweets) > 0:
        twitter["last_tweet_id"] = tweets[0].id
        
    print()
    return twitter

def twitter_post(message):
    """ Post a message on Twitter (uses the Tweepy module)
    
    Args:
        message (str): a string containing the message to be posted
    """
    message = message[:270]
    print(message+"\n")

    if test is False:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        try:
            api.update_status(message)
        except tweepy.TweepError as error:
            print("WARNING: Tweet NOT posted because " + str(error.reason))

def twitter_post_image(message, filename, text, text_size=200, crop=False):
    """ Post a photo with message on Twitter (uses the Tweepy module)
    
    Args:
        message (str): a string containing the message to be posted
        url (str): filename of the image to be posted
    """

    if text is not None:
        edit_image(filename, text, text_size=text_size, crop=crop)
    
    message = message[:270]
    print(message)
    print("Media: " + filename + "\n")

    # Check if the file is a video and exit from function
    # This is needed since Tweepy doesn't support videos
    # See this for more info: https://github.com/marco97pa/Blackpink-Data/issues/12
    # You can remove this check when the issue is fixed
    if filename[-3:] == "mp4":
        print("WARNING: Video not posted since Tweepy doesn't support it\nSee https://github.com/marco97pa/Blackpink-Data/issues/12 for more info")
        return

    if test is False:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        uploaded = api.media_upload(filename)
        api.update_status(message, media_ids=[uploaded.media_id])
        os.remove(filename)

def edit_image(filename, text, text_size=200, crop=False):
    """ Edit an image by adding a text (uses the Pillow module)
    
    Args:
        filename (str): filename of the image to be modified
        text (str): text to be added
    """
    #Open image
    my_image = Image.open(filename)
    # Crop
    if crop:
        # Size of the image in pixels (size of orginal image) 
        width, height = my_image.size 
        
        # Setting the points for cropped image 
        left = 0
        right = width
        top = height / 8
        bottom = height - (height / 8)
        
        # Cropped image of above dimension 
        my_image = my_image.crop((left, top, right, bottom)) 
    
    # Open font
    title_font = ImageFont.truetype('Montserrat-Bold.ttf', text_size)
    # Edit image
    image_editable = ImageDraw.Draw(my_image)
    # Add text
    image_editable.text((50,15), text, (237, 230, 211), font=title_font)
    # Save image
    my_image.save(filename)