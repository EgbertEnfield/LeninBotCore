from logging import handlers
import os
import re
import sys
import json
import glob
import tweepy
import random
import datetime
import argparse
import unicodedata
import logging
from enum import Enum
from typing import Final
from decimal import Decimal, ROUND_HALF_UP
from logging.handlers import TimedRotatingFileHandler

# constants
VERSION = '1.2.1020.5'


class Twitter:
    _api: Final[tweepy.API] = tweepy.API

    class TweetMode(Enum):
        Text = 0
        Picture = 1
        TextAndPicture = 2

    def __init__(self):
        try:
            with open(key_file) as raw_json:
                keys = json.load(raw_json)
            auth = tweepy.OAuthHandler(
                keys['twitter']['apiKey'],
                keys['twitter']['apiSecret'])
            auth.set_access_token(
                keys['twitter']['token'],
                keys['twitter']['tokenSecret'])
            self._api = tweepy.API(auth)
            logger.debug('Bot setup complete')
        except FileNotFoundError:
            logger.exception(f'keys.json did not find in {cwd}')
        except KeyError:
            logger.exception('Several keys are wrong or missing')
        except Exception:
            logger.exception('Ignoring exception in __init__')

    def poston_twitter(self, mode: TweetMode, message: str, path: str = ''):
        try:
            _is_fatal = False
            _is_debug = settings['args']['isDebugMode'] | settings['main']['isDebugMode']
            if (_is_debug is False):
                if (mode == self.TweetMode.Picture):
                    self._api.update_with_media(status='', filename=path)
                elif (message != ''):
                    if (mode == self.TweetMode.Text):
                        self._api.update_status(message)
                    elif (mode == self.TweetMode.TextAndPicture):
                        self._api.update_with_media(
                            status=message, filename=path)
                    else:
                        _is_fatal = True
                        logger.warning('Tweet mode is not specified')
                else:
                    _is_fatal = True
                    logger.warning('Tweet message is empty')
            else:
                _is_fatal = True
                logger.error(
                    'Cannot use poston_twitter with debug-mode true')
        except FileNotFoundError:
            logger.exception(f'Picture file did not find in {cwd}')
        except Exception:
            logger.exception('Ignoring exception in poston_twitter')
        else:
            if (_is_fatal is False):
                logger.info('Tweeted successfully.')
            else:
                logger.info('Finished with error')

    def tweet_debug(self, mode: TweetMode, message: str, path: str = ''):
        try:
            _is_fatal = False
            if (self._is_tweetable(message)):
                if (mode == self.TweetMode.Picture and os.path.exists(path)):
                    print(path)
                elif (message != ''):
                    if (mode == self.TweetMode.Text):
                        print(message)
                    elif (mode == self.TweetMode.TextAndPicture and os.path.exists(path)):
                        print(message)
                        print(path)
                else:
                    _is_fatal = True
                    logger.warning('Tweet message is empty')
            else:
                _is_fatal = True
                logger.warning('Tweet message is up to 140 chars')
        except FileNotFoundError:
            logger.exception(f'Picture file did not find in {cwd}')
        else:
            if (_is_fatal is False):
                logger.info('Succeeded to debug tweet')
            else:
                logger.info('Debug finished with error')

    def _is_tweetable(self, message: str):
        text_count = 0
        url_pattern = 'https?://[\\w/:%#\\$&\\?\\(\\)~\\.=\\+\\-]+'
        links = re.findall(url_pattern, message)

        if (message == ''):
            logger.warning('Tweet message is empty')
            return False

        for c in message:
            j = unicodedata.east_asian_width(c)
            if (j == 'F' or j == 'W' or j == 'H' or j == 'N'):
                text_count += 1
            elif (j == 'Na' or j == 'A' or c == '\n'):
                text_count += 0.5

        if (len(links) > 0):
            text_count += 11.5
            for link in links:
                for lc in link:
                    text_count -= 0.5

        text_count = Decimal(
            str(text_count)).quantize(
            Decimal('0'),
            rounding=ROUND_HALF_UP)

        if (text_count <= 140):
            logger.debug(f'Message length within 140 ({text_count})')
            return True
        else:
            logger.error(f'Message length over 140 ({text_count})')
            return False


class BotCore:
    @staticmethod
    def select_proverb():
        try:
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
        except FileNotFoundError:
            logger.exception(f'proverbs.json did not find in {cwd}')
            return ''
        except Exception:
            logger.exception('Ignoring exception in select_proverb')
            return ''


def create_logger():
    log_level = logging.INFO
    log_dir: Final[str] = settings['log']['logDirectory']
    max_log_size: Final[int] = settings['log']['maxLogSize']
    is_show_log: Final[bool] = settings['main']['isShowLogOutput'] | settings['args']['isShowLogOutput']

    if (settings['log']['logLevel'] == 'critical'):
        log_level = logging.CRITICAL
    elif (settings['log']['logLevel'] == 'error'):
        log_level = logging.ERROR
    elif (settings['log']['logLevel'] == 'info'):
        log_level = logging.INFO
    elif (settings['log']['logLevel'] == 'debug'):
        log_level = logging.DEBUG
    elif (settings['log']['logLevel'] == 'notset'):
        log_level = logging.NOTSET
    else:
        return

    if not (os.path.exists(log_dir)):
        os.mkdir(log_dir)

    for log in glob.glob(log_dir + '/*.log'):
        if (os.path.getsize(log) <= max_log_size):
            log_file = log
            break
    else:
        # create new empty log file
        log_file = f'{log_dir}/{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.log'
        with open(log_file, 'w') as f:
            f.write('')

    format = logging.Formatter(
        '{asctime} [{levelname}]  {message}',
        style='{',
        datefmt='%y/%m/%d %H:%M:%S'
    )

    file_handler = handlers.TimedRotatingFileHandler(
        filename=log_file,
        encoding='UTF-8',
        when='MIDNIGHT',
        backupCount=7
    )
    file_handler.setFormatter(format)
    file_handler.setLevel(log_level)

    if (is_show_log):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(format)
        stream_handler.setLevel(log_level)

    internal_logger = logging.getLogger()
    internal_logger.setLevel(log_level)
    internal_logger.addHandler(file_handler)
    if (is_show_log):
        internal_logger.addHandler(stream_handler)

    internal_logger.debug(f'current log level is {log_level}')
    internal_logger.debug(f'current log file path is {log_file}')
    internal_logger.debug('logger setup complete')

    return internal_logger


def load_settings():
    try:
        with open(settings_file, 'r') as reader:
            j_settings = json.load(reader)
    except FileNotFoundError:
        logger.error(f'settings.json did not find in {cwd}. set default')
    finally:
        j_settings.setdefault('main', {})
        j_settings['main'].setdefault('ignoreError', True)
        j_settings['main'].setdefault('isDebugMode', False)
        j_settings['main'].setdefault('isShowLogOutput', False)
        j_settings.setdefault('log', {})
        j_settings['log'].setdefault('maxLogSize', 1024 * 5)
        j_settings['log'].setdefault('logDirectory', f'{cwd}/log')
        j_settings['log'].setdefault('isLogStacktrace', True)
        j_settings['log'].setdefault('logLevel', 'info')
        return j_settings


def init_settings():
    json_dic = {
        'main': {
            'ignoreError': True,
            'isDebugMode': False,
            'isShowLogOutput': False
        },
        'log': {
            'maxLogSize': 1024 * 5,
            'logDirectory': f'{cwd}/log',
            'isLogStacktrace': False,
            'logLevel': 'info'
        }
    }
    with open(settings_file, 'w') as writer:
        json_str = json.dumps(json_dic)
        writer.write(json_str)


def parse_args():
    arg_values = {}
    arg_values.setdefault('args', {})
    arg_values['args'].setdefault('isDebugMode', False)
    arg_values['args'].setdefault('isShowLogOutput', False)
    arg_values['args'].setdefault('isGoodmorning', False)
    arg_values['args'].setdefault('isGoodnight', False)
    args = sys.argv
    if (len(args) == 0):
        return {}
    elif (len(args) == 1):
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
settings: Final[dict] = parse_args() | load_settings()

logger: Final[logging.Logger] = create_logger()
twitter: Final[Twitter] = Twitter()

if __name__ == '__main__':
    tweet = ''
    if (settings['args']['isGoodmorning']):
        tweet = 'Доброе утро'
    elif (settings['args']['isGoodnight']):
        tweet = 'Спокойной ночи'
    else:
        tweet = BotCore.select_proverb()

    _is_debug = settings['args']['isDebugMode'] | settings['main']['isDebugMode']
    if (_is_debug is False):
        twitter.poston_twitter(Twitter.TweetMode.Text, tweet)
    else:
        twitter.tweet_debug(Twitter.TweetMode.Text, tweet)
