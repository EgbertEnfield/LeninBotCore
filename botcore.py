import os
import sys
import json
import glob
import tweepy
import random
import datetime
import argparse
import traceback
import logging
from enum import Enum
from typing import Final
from logging import NOTSET, FileHandler
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

# constants
VERSION = '1.2.915.14'


class TweetMode(Enum):
    Text = 0
    Picture = 1
    TextAndPicture = 2


class Result(Enum):
    Error = '[error]  '
    Caution = '[caution]'
    Info = '[info]   '
    Success = '[success]'

class Twitter:
    @staticmethod
    def poston_twitter(mode: TweetMode, message: str, path: str=''):
        try:
            with open(key_file) as raw_json:
                keys = json.load(raw_json)
            auth = tweepy.OAuthHandler(
                keys['twitter']['apiKey'],
                keys['twitter']['apiSecret'])
            auth.set_access_token(
                keys['twitter']['token'],
                keys['twitter']['tokenSecret'])
            api = tweepy.API(auth)
            if (settings['args']['isDebugMode'] | settings['main']['isDebugMode']):
                if (mode == TweetMode.Picture and os.path.exists(path)):
                    print(path)
                elif (message != ''):
                    if (mode == TweetMode.Text):
                        print(message)
                    elif (mode == TweetMode.TextAndPicture and os.path.exists(path)):
                        print(message)
                        print(path)
                else:
                    logger.warning('Tweet message is empty.')
            else:
                if (mode == TweetMode.Picture):
                    api.update_with_media(status='', filename=path)
                elif (message != ''):
                    if (mode == TweetMode.Text):
                        api.update_status(message)
                    elif (mode == TweetMode.TextAndPicture):
                        api.update_with_media(status=message, filename=path)
                    else:
                        logger.warning('Tweet mode is not specified')
                else:
                    logger.warning('Tweet message is empty.')
        except FileNotFoundError as ex:
            logger.exception(f'keys.json does not found in {cwd} or picture does not found.')
        except Exception as ex:
            logger.exception('Ignoring exception in poston_twitter')
        else:
            logger.info('Tweeted successfully.')


def select_proverb():
    try:
        if (settings['args']['isGoodmorning']):
            return 'Доброе утро'
        elif (settings['args']['isGoodnight']):
            return ''
        else:
            with open(tweets_file, 'r', encoding='utf-8') as raw_json:
                proverbs = json.load(raw_json)
                selected = []
                if (proverbs['russian']['isEnable']):
                    if (len(proverbs['russian']['proverbs']) != 0):
                        russian = proverbs['russian']['proverbs']
                        r = random.randint(0, len(russian) - 1)
                        selected.append(russian[r])
                    else:
                        logger.warning('proverbs list is empty')
                if (proverbs['english']['isEnable']):
                    if (len(proverbs['english']['proverbs']) != 0):
                        english = proverbs['english']['proverbs']
                        e = random.randint(0, len(english) - 1)
                        selected.append(english[e])
                    else:
                        logger.warning('proverbs list is empty')
                if (proverbs['japanese']['isEnable']):
                    if (len(proverbs['japanese']['proverbs']) != 0):
                        japanese = proverbs['japanese']['proverbs']
                        j = random.randint(0, len(japanese) - 1)
                        selected.append(japanese[j])
                    else:
                        logger.warning('proverbs list is empty')
                s = random.randint(0, len(selected) - 1)
                return selected[s]
    except Exception as ex:
        logger.exception('Ignoring exception in select_proverb')
        return ''


def create_logger():
    log_dir: Final[str] = settings['log']['logDirectory']
    max_log_size: Final[int] = settings['log']['maxLogSize']
    is_show_log: Final[bool] = settings['main']['isShowLogOutput'] | settings['args']['isShowLogOutput']

    if not (os.path.exists(log_dir)):
        os.mkdir(log_dir)

    for log in glob.glob(log_dir + '/*.log'):
        if (os.path.getsize(log) <= max_log_size):
            log_file = log
            break
    else:
        log_file = f'{log_dir}/{datetime.datetime.now():"%y%m%d%H%M%S"}.log'
        with open(log_file, 'w') as f:
            f.write('')

    root = logging.getLogger()

    format = logging.Formatter(
        # '{asctime} {f"[{levelname}]": <10} {message}',
        '{asctime} {levelname}: {message}',
        style='{',
        datefmt='%y/%m/%d %H:%M:%S'
    )

    if (is_show_log):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(format)
        stream_handler.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(
        filename=log_file,
        encoding='utf8',
        mode='w',
        maxBytes=max_log_size,
        backupCount=1000
    )
    file_handler.setFormatter(format)
    file_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=NOTSET,
        handlers=[stream_handler, file_handler]
    )

    return logging.getLogger(__name__)

class JsonConverter:
    @staticmethod
    def get_settings():
        settings = {}
        try:
            with open(settings_file, 'r') as raw_json:
                settings = json.load(raw_json)
        except Exception as ex:
            logger.exception(f'settings.json does not found in {cwd}.')
        finally:
            settings.setdefault('log', {})
            settings['log'].setdefault('maxLogSize', 1024 * 5)
            settings['log'].setdefault('logDirectory', f'{cwd}/log')
            settings['log'].setdefault('isLogStacktrace', False)
            settings.setdefault('main', {})
            settings['main'].setdefault('ignoreError', True)
            settings['main'].setdefault('isDebugMode', False)
            settings['main'].setdefault('isShowLogOutput', False)
            return settings


def parse_args():
    args = sys.argv
    arg_values = {}
    arg_values.setdefault('args', {})
    arg_values['args'].setdefault('isDebugMode', False)
    arg_values['args'].setdefault('isShowLogOutput', False)
    arg_values['args'].setdefault('isGoodmorning', False)
    arg_values['args'].setdefault('isGoodnight', False)
    if (len(args) == 1):
        return arg_values
    args.pop(0)
    parser = argparse.ArgumentParser(
        prog='botcore.py',
        usage='python3.9 botcore.py [-d|--debug] [settings...]',
        epilog='MIT License  Copyright (c) 2021 Семён Мошнко  GitHub: https://github.com/Sovietball1922/LeninBotCore',
        add_help=False)
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-m', '--good_morning', action='store_true')
    parser.add_argument('-n', '--good_night', action='store_true')
    parser.add_argument('-?', '--help', action='help')
    arg = parser.parse_args(args)
    if (arg.version):
        print(f'botcore.py version: {VERSION}')
        sys.exit()
    elif (arg.good_morning and arg.good_night):
        arg_values['args']['isDebugMode'] = arg.debug
        arg_values['args']['isShowLogOutput'] = arg.verbose
        return arg_values
    else:
        arg_values['args']['isDebugMode'] = arg.debug
        arg_values['args']['isShowLogOutput'] = arg.verbose
        arg_values['args']['isGoodmorning'] = arg.good_morning
        arg_values['args']['isGoodnight'] = arg.good_night
        return arg_values


# readonly variables
cwd: Final[str] = os.path.dirname(__file__)
key_file: Final[str] = f'{cwd}/keys.json'
tweets_file: Final[str] = f'{cwd}/tweets.json'
settings_file: Final[str] = f'{cwd}/settings.json'
settings: Final[dict] = parse_args() | JsonConverter.get_settings()

logger: Final[logging.Logger]= create_logger()
twitter: Final[Twitter] = Twitter()
converter: Final[JsonConverter] = JsonConverter()

if __name__ == '__main__':
    tweet = select_proverb()
    Twitter.poston_twitter(TweetMode.Text, tweet)
