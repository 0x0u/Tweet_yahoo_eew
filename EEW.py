import re
import sys
import tweepy
import requests
from bs4 import BeautifulSoup
from mastodon import Mastodon

class EEW:
    def get_data(self):
        url = 'https://typhoon.yahoo.co.jp/weather/jp/earthquake/20110331161539.html'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        info = [i.text for i in soup.find_all(width="70%")]
        image = soup.find(id='earthquake-01').find('img').get('src')
        self.__check(text=image)
        self.__get_image(image_url=image)
        text = '[地震速報]\n・時刻: {}\n・震源地: {}\n・最大震度: {}\n・マグニチュード: {}\n・深さ: {}\n・緯度/経度: {}\n・情報: {}'.format(info[0],info[1],info[2],info[3],info[4],info[5],info[6])
        geocode = re.findall('\d+[.]+\d', info[5])
        place = soup.find_all(width="90%")[::-1]
        text2 = []
        intensity = int(re.findall('\d+', info[2])[0])
        for i in range(intensity):
            p = '、'.join(re.findall('(.+?)\u3000', str(place[i])))
            if len(p) >= 133:
                p = '{:.133}...'.format(p)
            text2.append('《震度{}》 {}'.format(i+1, p))
        return text, text2, geocode

    def __get_image(self, image_url):
        req = requests.get(image_url)
        with open('eew.png', 'wb') as w:
            w.write(req.content)

    def __check(self, text):
        with open('check.txt','r') as file1:
            t = file1.read()
        if text != t:
            print('更新があります')
            with open('check.txt','w') as file2:
                file2.write(text)
        else:
            print('更新がありません')
            sys.exit()

    def twitter_api(self):
        consumer_key = 'consumer_key'
        consumer_secret = 'consumer_secret'
        access_key = 'access_key'
        access_secret = 'access_secret'
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        return api

    def tweet(self, text, lat=None, lon=None, id_=None):
        api = self.twitter_api()
        if id_ == None:
            tweet = api.update_with_media(filename='eew.png', status=text, lat=lat, long=lon)
            return tweet.id
        elif id_ != None:
            tweet = api.update_status(status=text, in_reply_to_status_id =id_)
            return tweet.id

    def mastodon_api(self):
        mastodon = Mastodon(
        client_id="app_key.txt",
        access_token="user_key.txt",
        api_base_url = "https://pawoo.net")
        return mastodon

    def toot(self, text, id_=None):
        mastodon = self.mastodon_api()
        media_files = mastodon.media_post('eew.png', "image/png")
        if id_ == None:
            toot = mastodon.status_post(status=text, visibility='direct', media_ids=media_files)
            return toot.id
        elif id_ != None:
            toot = mastodon.status_post(status=text, visibility='direct', in_reply_to_id=id_)
            return toot.id
