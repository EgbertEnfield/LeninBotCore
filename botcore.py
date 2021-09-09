import os
import sys
import json
import glob
import tweepy
import random
import datetime
import argparse
from enum import Enum


class TweetMode(Enum):
    Text = 0
    Picture = 1
    TextAndPicture = 2


class Result(Enum):
    Error = '[error]  '
    Caution = '[caution]'
    Info = '[info]   '
    Success = '[success]'


def poston_twitter(mode: TweetMode, message: str, path=''):
    try:
        settings = SETTINGS
        with open(KEY_FILE) as raw_json:
            keys = json.load(raw_json)
        auth = tweepy.OAuthHandler(keys['twitter']['apiKey'], keys['twitter']['apiSecret'])
        auth.set_access_token(keys['twitter']['token'], keys['twitter']['tokenSecret'])
        api = tweepy.API(auth)
        if (settings['is_debug'] == False):
            if (mode == TweetMode.Picture):
                api.update_with_media(status='', filename=path)
            elif (message != ''):
                if(mode == TweetMode.Text):
                    api.update_status(f'{message}')
                elif (mode == TweetMode.TextAndPicture):
                    api.update_with_media(status=message, filename=path)
            else:
                raise ValueError('Tweet message is empty.')
        else:
            if (mode == TweetMode.Picture and os.path.exists(path) == True):
                print(path)
            elif (message != ''):
                if(mode == TweetMode.Text):
                    print(message)
                elif (mode == TweetMode.TextAndPicture and os.path.exists(path) == True):
                    print(message)
                    print(path)
            else:
                raise ValueError('Tweet message is empty.')
    except FileNotFoundError as ex:
        log_local(Result.Error, f'keys.json does not found in {CWD} or picture does not found.', ex)
    except Exception as ex:
        log_local(Result.Error, '', ex)
    else:
        log_local(Result.Success, 'Tweeted successfully.')


def select_proverb():
    try:
        settings = SETTINGS
        if (settings['is_morning'] == True):
            return ''
        elif (settings['is_night'] == True):
            return ''
        else:
            with open(TWEETS_FILE, 'r', encoding='utf-8') as raw_json:
                proverbs = json.load(raw_json)
                selected = []
                if (proverbs['russian']['isEnable'] == True):
                    if (len(proverbs['russian']['proverbs']) != 0):
                        russian = proverbs['russian']['proverbs']
                        r = random.randint(0, len(russian)-1)
                        selected.append(russian[r])
                    else:
                        raise ValueError('proverbs list is empty')
                if (proverbs['english']['isEnable'] == True):
                    if (len(proverbs['english']['proverbs']) != 0):
                        english = proverbs['english']['proverbs']
                        e = random.randint(0, len(english)-1)
                        selected.append(english[e])
                    else:
                        raise ValueError('proverbs list is empty')
                if (proverbs['japanese']['isEnable'] == True):
                    if (len(proverbs['japanese']['proverbs']) != 0):
                        japanese = proverbs['japanese']['proverbs']
                        j = random.randint(0, len(japanese)-1)
                        selected.append(japanese[j])
                    else:
                        raise ValueError('proverbs list is empty')
                s = random.randint(0, len(selected)-1)
                return selected[s]
    except Exception as ex:
        log_local(Result.Error, '', ex)
        raise(ex)


def get_settings():
    settings = {}
    try:
        with open(SETTINGS_FILE, 'r') as raw_json:
            settings = json.load(raw_json)
    except Exception as ex:
        log_local(Result.Error, f'settings.json does not found in {CWD}.', ex)
    finally:
        settings.setdefault('log', {})
        settings['log'].setdefault('maxLogSize', 51200)  # 500KB
        settings['log'].setdefault('logDirectory', f'{CWD}/log')
        settings['log'].setdefault('logDatetimeFormat', '%y-%m-%d-%H-%M-%S')
        settings.setdefault('main', {})
        settings['main'].setdefault('ignoreError', True)
        return settings


def pick_log_file():
    settings = get_settings()
    limited_log_size = settings['log']['maxLogSize']
    logs = glob.glob(settings['log']['logDirectory'] + '/*.log')
    if (len(logs) > 0):
        for log in logs:
            if (os.path.getsize(log) <= limited_log_size):
                return log
        return ''
    else:
        return ''


def create_log_message(result: Result, message, except_obj=None):
    settings = SETTINGS
    dtformat = settings['log']['logDatetimeFormat']
    if (result == Result.Error):
        if(except_obj == None):
            raise ValueError('Exception object is none.')
        else:
            if (message == ''):
                return f'{datetime.datetime.now().strftime(str(dtformat))}  {Result.Error.value} {type(except_obj)}{except_obj}'
            else:
                return f'{datetime.datetime.now().strftime(str(dtformat))}  {Result.Error.value} {type(except_obj)}{message}'
    else:
        if (message == ''):
            raise ValueError('Log message is empty.')
        else:
            return f'{datetime.datetime.now().strftime(str(dtformat))}  {result.value} {message}'


def log_local(result: Result, message, excep_obj=None):
    log_dir = f'{CWD}/log'
    log_file = LOG_FILE
    settings = SETTINGS
    if (log_file == ""):
        if (os.path.exists(log_dir) == False):
            os.mkdir(log_dir)
        log_file = f'{log_dir}/{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.log'
        with open(log_file, 'w') as f:
            InitMessage = f'{create_log_message(Result.Success, "Created new log file.")}\n{create_log_message(result, message, excep_obj)}'
            print(InitMessage, file=f)
            if (settings['args']['is_verbose'] == True):
                print(InitMessage)
    else:
        with open(log_file, mode='parser') as f:
            log_message = create_log_message(result, message, excep_obj)
            print(log_message, file=f)
            if (settings['args']['is_verbose'] == True):
                print(log_message)


def parse_args():
    args = sys.argv
    args.pop(0)
    if (len(args) == 0):
        return {'args': {
            'is_debug': False,
            'is_verbose': False,
            'is_goodmorning': False,
            'is_goodnight': False,
        }}
    parser = argparse.ArgumentParser(
        prog='botcore.py',
        usage='python3.9 botcore.py [-d|--debug] [settings...]',
        epilog='MIT License  Copyright (c) 2021 Семён Мошнко  GitHub: https://github.com/Sovietball1922/LeninBotCore',
        add_help=False
    )
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-m', '--good_morning', action='store_true')
    parser.add_argument('-n', '--good_night', action='store_true')
    parser.add_argument('-?', '--help', action='help')
    arg = parser.parse_args(args)
    if (arg.version == True):
        print(f'botcore.py version: {VERSION}')
        sys.exit()
    if (arg.good_morning == True and arg.good_night == True):
        log_local(Result.Caution, '-m and -n switch cannot use at same time')
        return {'args': {
            'is_debug': arg.debug,
            'is_verbose': arg.verbose,
            'is_goodmorning': False,
            'is_goodnight': False,
        }}
    return {'args': {
        'is_debug': arg.debug,
        'is_verbose': arg.verbose,
        'is_goodmorning': arg.good_morning,
        'is_goodnight': arg.good_night,
    }}


# This will not maybe use.
'''
def log_Lnotify(result, message='', excep_obj=None):
    try:
        with open(KEY_FILE) as raw_json:
            keys = json.load(raw_json)
        token = keys['line']['token']
        api_url = 'https://notify-api.line.me/api/notify'
        log_message = create_log_message(result, message, excep_obj)
        requests.post(api_url, headers={'Authorization': f'Bearer {token}'}, data={'message': f'n{log_message}'})
        log_local(True, "Requested LINE Notify")
    except Exception as ex:
        log_local(False, 'Failed to send LINE Notify', ex)
'''

CWD = os.getcwd()
VERSION = f'1.2.909.101'
KEY_FILE = f'{CWD}/keys.json'
TWEETS_FILE = f'{CWD}/tweets.json'
SETTINGS_FILE = f'{CWD}/settings.json'
SETTINGS = parse_args() | get_settings()
LOG_FILE = pick_log_file()

if __name__ == '__main__':
    tweet = select_proverb()
    poston_twitter(TweetMode.Text, tweet)
