import io
import os
import time

import requests
from bs4 import BeautifulSoup
import tweepy
import schedule
from dotenv import load_dotenv

tweeted_texts = []

load_dotenv()

consumer_key = os.environ.get("consumer_key", "")
consumer_secret = os.environ.get("consumer_secret", "")
access_token = os.environ.get("access_token", "")
access_token_secret = os.environ.get("access_token_secret", "")

def check_traffic_info():
    # HTMLの取得(GET)
    req = requests.get("https://trafficinfo.westjr.co.jp/kinki.html")
    req.encoding = req.apparent_encoding

    # HTMLの解析
    bsObj = BeautifulSoup(req.text, "html.parser")

    # 画像の取得
    map = bsObj.find(class_="map")
    if map is not None:
        map = "https://trafficinfo.westjr.co.jp/" + map.find("img")["src"]
    print(map)

    # 運転情報の取得
    items = bsObj.find(id="syosai_1").find_all(class_="jisyo_contents")

    #事象の抽出、ツイート
    for item in items:
        text = ""
        contents = item.find_all("p")
        for content in contents:
            for content_text in content.text.split("\n"):
                text += content_text + "\n,"
        if text in tweeted_texts:
            continue
        tweeted_texts.append(text)
        text += "https://trafficinfo.westjr.co.jp/kinki.html"
        try:
            tweet(text, img=map)
        except tweepy.errors.TooManyRequests:
            print("リクエストが多すぎるため20分停止します")
            time.sleep(20*60)

def tweet(text, img=None):
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    media_id = None
    if img is not None:
        auth = tweepy.OAuth1UserHandler(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        api = tweepy.API(auth)
        media_id = api.media_upload(filename="traffic.gif", file=io.BytesIO(requests.get(img).content),
                                    chunked=True).media_id
        time.sleep(1)

    n = 140
    reply_tweet_id = ""
    split_text = text.split(",")
    tweet_temp_text = ""
    for i in split_text:
        if len(tweet_temp_text+i) > n:
            if reply_tweet_id == "":
                response = client.create_tweet(
                    text=tweet_temp_text,
                    media_ids=[media_id]
                )
                time.sleep(1)
            else:
                response = client.create_tweet(
                    text=tweet_temp_text,
                    in_reply_to_tweet_id=reply_tweet_id
                )
                time.sleep(1)
            reply_tweet_id = response.data["id"]
            tweet_temp_text = i
        else:
            tweet_temp_text += i

    if reply_tweet_id == "":
        response = client.create_tweet(
            text=tweet_temp_text,
            media_ids=[media_id]
        )
        time.sleep(1)
    else:
        response = client.create_tweet(
            text=tweet_temp_text,
            in_reply_to_tweet_id=reply_tweet_id
        )
        time.sleep(1)

    print(f"https://twitter.com/user/status/{response.data['id']}")


def reset_tweeted_text():
    tweeted_texts.clear()

schedule.every(1).days.do(reset_tweeted_text)
schedule.every(5).minutes.do(check_traffic_info)
while True:
    schedule.run_pending()
    time.sleep(1)
