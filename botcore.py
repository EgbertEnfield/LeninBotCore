import os
import csv
import sys
import json
import glob
import tweepy
import random
import requests
import datetime
from enum import Enum

key_file = 'keys.json'
proverbs_file = 'proverbs.csv'


class TweetMode(Enum):
    Text = 0
    Picture = 1
    TextAndPicture = 2


def poston_twitter(mode, message, path=''):
    try:
        with open(key_file) as raw_json:
            keys = json.load(raw_json)
        auth = tweepy.OAuthHandler(keys['twitter']['apiKey'], keys['twitter']['apiSecret'])
        auth.set_access_token(keys['twitter']['token'], keys['twitter']['tokenSecret'])
        api = tweepy.API(auth)
        if (mode == TweetMode.Picture):
            api.update_with_media(status='', filename=path)
        elif (message != ''):
            if(mode == TweetMode.Text):
                api.update_status(f'@tos\nTest: {message}')
            elif (mode == TweetMode.TextAndPicture):
                api.update_with_media(status=message, filename=path)
        else:
            raise ValueError('Tweet message is empty.')
    except ValueError as ex:
        log_local(False, ex)
    except FileNotFoundError as ex:
        log_local(False, f'keys.json does not found in {os.getcwd()} or picture does not found.', ex)
    except Exception as ex:
        log_local(False, ex)
    else:
        log_local(True, 'Tweeted successfly.')


def pick_proverbs():
    try:
        with open(proverbs_file, 'r', encoding='utf-8') as f:
            csv_lists = csv.reader(f)
            russian = [row[0] for row in csv_lists]
            # english = [row[1] for row in csv_lists]
            # japanese = [row[2] for row in csv_lists]
            x = random.randint(0, len(russian))

            # English and Japanese version is currently unsupported.
            # Because I have yet to find any proverbs translated in English or Japanese.
            return russian[x]
    except FileNotFoundError as ex:
        log_local(False, f'proverbs.csv does not found in {os.getcwd()}', ex)
        return ['', '', '']


def pick_log_file():
    limited_log_size = 640 * 1024
    logs = glob.glob('./log/*.log')
    if (len(logs) > 0):
        for log in logs:
            if (os.path.getsize(log) <= limited_log_size):
                return log
        return ''
    else:
        return ''


def create_log_message(is_succeeded, message='', except_obj=None):
    if(is_succeeded == True):
        if (message == ''):
            raise ValueError('Log message is empty.')
        else:
            return f'{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}  [Succeeded] {message}'
    else:
        if(except_obj == None):
            raise ValueError('Exception object is none.')
        else:
            if (message == ''):
                return f'{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}  [Failed]    {type(except_obj)}{except_obj}'
            else:
                return f'{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}  [Failed]    {type(except_obj)}{message}'


def log_local(is_succeeded, message='', excep_obj=None):
    log_file = pick_log_file()
    if (log_file == ""):
        if (os.path.exists('./log') == False):
            os.mkdir('./log')
        log_file = f'./log/{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.log'
        with open(log_file, 'w') as f:
            InitMessage = f'{create_log_message(True, "Created new log file.")}\n{create_log_message(is_succeeded, message, excep_obj)}'
            print(InitMessage, file=f)
    else:
        with open(log_file, mode='a') as f:
            log_message = create_log_message(is_succeeded, message, excep_obj)
            print(log_message, file=f)


# This will not maybe use.
'''
def log_Lnotify(is_succeeded, message='', excep_obj=None):
    try:
        with open(key_file) as raw_json:
            keys = json.load(raw_json)
        token = keys['line']['token']
        api_url = 'https://notify-api.line.me/api/notify'
        log_message = create_log_message(is_succeeded, message, excep_obj)
        requests.post(api_url, headers={'Authorization': f'Bearer {token}'}, data={'message': f'\n{log_message}'})
        log_local(True, "Requested LINE Notify")
    except Exception as ex:
        log_local(False, 'Failed to send LINE Notify', ex)
'''


if __name__ == '__main__':
    switch = sys.argv[0]
    if (switch == ''):
        tweet = pick_proverbs()
        poston_twitter(TweetMode.Text, tweet)
    else:
        if (switch == 'hello'):
            tweet = 'Доброе утро!'
        elif (switch == 'goodnight'):
            tweet = 'Спокойной ночи'
