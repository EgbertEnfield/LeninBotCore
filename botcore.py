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
    _api_v2: Final[tweepy.Client] = tweepy.Client

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
            _is_debug = settings['args']['debug'] | settings['main']['debug']
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
    _tweets: dict = {}

    class Greeting(Enum):
        Morning = 0,
        Night = 1

    def __init__(self):
        try:
            with open(tweets_file, 'r', encoding='utf-8') as raw_jsom:
                self._tweets = json.load(raw_jsom)
        except FileNotFoundError:
            logger.exception(f'tweets.json did not find in {cwd}')

    def select_proverb(self):
        try:
            proverbs = self._tweets['main']
            selected = []
            if (proverbs['russian']['enable']):
                if (len(proverbs['russian']['proverbs']) != 0):
                    russian = proverbs['russian']['proverbs']
                    r = random.randint(0, len(russian) - 1)
                    selected.append(russian[r])
                else:
                    logger.warning('proverbs list is empty')
            if (proverbs['english']['enable']):
                if (len(proverbs['english']['proverbs']) != 0):
                    english = proverbs['english']['proverbs']
                    e = random.randint(0, len(english) - 1)
                    selected.append(english[e])
                else:
                    logger.warning('proverbs list is empty')
            if (proverbs['japanese']['enable']):
                if (len(proverbs['japanese']['proverbs']) != 0):
                    japanese = proverbs['japanese']['proverbs']
                    j = random.randint(0, len(japanese) - 1)
                    selected.append(japanese[j])
                else:
                    logger.warning('proverbs list is empty')
            s = random.randint(0, len(selected) - 1)
            return selected[s]
        except Exception:
            logger.exception('Ignoring exception in select_proverb')
            return ''

    def create_greeting(self, mode: Greeting):
        greeting = self._tweets['greeting']
        if (mode == self.Greeting.Morning and greeting['morning']['enable']):
            morning = greeting['morning']
            msg = [morning['tweet'], '']

            if (morning['picture']['enable']):
                path = self._select_picture(
                    cwd + morning['picture']['directory'])
                if (path != ''):
                    msg[1] = path

            return msg

        if (mode == self.Greeting.Night and greeting['evening']['enable']):
            evening = greeting['evening']
            msg = [evening['tweet'], '']

            if (evening['picture']['enable']):
                path = self._select_picture(
                    cwd + evening['picture']['directory'])
                if (path != ''):
                    msg[1] = path

            return msg

    def _select_picture(self, path: str):
        pic_list = []
        ext_list = settings['extension']['picture']
        for ext in ext_list:
            pic_list.extend(glob.glob(path + f'/*.{ext}'))
        r = random.randint(0, len(pic_list) - 1)
        return pic_list[r]


class Log:
    def create_logger(self):
        level_file = logging.INFO
        level_stream = logging.INFO

        log_dir = settings['log']['file']['directory']
        is_enable_file = settings['log']['file']['enable']
        is_enable_stream = settings['log']['stream']['enable']

        level_file = self._get_log_level(
            settings['log']['file']['level'])
        level_stream = self._get_log_level(
            settings['log']['stream']['level'])

        if not (os.path.exists(log_dir)):
            os.mkdir(log_dir)

        for log in glob.glob(log_dir + '/*.log'):
            if (log.endswith('.log')):
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

        if (is_enable_file):
            file_handler = handlers.TimedRotatingFileHandler(
                filename=log_file,
                encoding='UTF-8',
                when='MIDNIGHT',
                backupCount=7
            )
            file_handler.setFormatter(format)
            file_handler.setLevel(level_file)

        if (is_enable_stream):
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(format)
            stream_handler.setLevel(level_stream)

        internal_logger = logging.getLogger()
        internal_logger.setLevel(logging.NOTSET)
        if (is_enable_file):
            internal_logger.addHandler(file_handler)
        if (is_enable_stream):
            internal_logger.addHandler(stream_handler)

        internal_logger.debug(
            f'current file_handler log level is {settings["log"]["file"]["level"]}')
        internal_logger.debug(
            f'current stream_handler log level is {settings["log"]["stream"]["level"]}')
        internal_logger.debug(f'current log file path is {log_file}')
        internal_logger.debug('logger setup complete')

        return internal_logger

    def _get_log_level(self, level: str):
        if (level == 'critical'):
            return logging.CRITICAL
        elif (level == 'error'):
            return logging.ERROR
        elif (level == 'info'):
            return logging.INFO
        elif (level == 'debug'):
            return logging.DEBUG
        elif (level == 'notset'):
            return logging.NOTSET
        else:
            return logging.INFO


def load_settings():
    try:
        with open(settings_file, 'r') as reader:
            j_dic = json.load(reader)
    except FileNotFoundError:
        logger.error(f'settings.json did not find in {cwd}. set default')
    finally:
        j_dic.setdefault('main', {})
        j_dic['main'].setdefault('verbose', True)
        j_dic['main'].setdefault('debug', False)

        j_dic.setdefault('log', {})
        j_dic['log'].setdefault('file', {})
        j_dic['log']['file'].setdefault('enable', True)
        j_dic['log']['file'].setdefault('level', 'info')
        j_dic['log']['file'].setdefault('directory', f'{cwd}/log')

        j_dic['log'].setdefault('stream', {})
        j_dic['log']['stream'].setdefault('enable', True)
        j_dic['log']['stream'].setdefault('level', 'info')

        return j_dic


def parse_args():
    arg_values = {
        'args': {
            'debug': False,
            'verbose': False,
            'mode': 'bot'
        }
    }

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

    parser.add_argument(
        '--version',
        action='store_true')
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Test behave this program')
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true')
    parser.add_argument(
        '-m',
        '--mode',
        default='bot',
        choices=['bot', 'morning', 'evening'],
        help='bot: default, morning: Tweet good morning, evening: Tweet good night')
    parser.add_argument(
        '-?',
        '--help',
        action='help',
        help='Show this help message.')

    arg = parser.parse_args(args)

    if (arg.version):
        print(f'botcore.py version: {VERSION}')
        sys.exit()
    else:
        arg_values['args']['debug'] = arg.debug
        arg_values['args']['verbose'] = arg.verbose
        arg_values['args']['mode'] = arg.mode
        return arg_values


# readonly variables
cwd: Final[str] = os.path.dirname(__file__)
key_file: Final[str] = f'{cwd}/keys.json'
tweets_file: Final[str] = f'{cwd}/tweets.json'
settings_file: Final[str] = f'{cwd}/settings.json'
settings: Final[dict] = parse_args() | load_settings()

# these are must put in this position
log: Final[Log] = Log()
logger: Final[logging.Logger] = log.create_logger()

core: Final[BotCore] = BotCore()
twitter: Final[Twitter] = Twitter()

if __name__ == '__main__':
    tweet = {}
    mode = settings['args']['mode']
    if (mode == 'morning'):
        li = core.create_greeting(core.Greeting.Morning)
        tweet = {
            'tweet': li[0],
            'path': li[1]
        }
    elif (mode == 'evening'):
        li = core.create_greeting(core.Greeting.Night)
        tweet = {
            'tweet': li[0],
            'path': li[1]
        }
    elif (mode == 'bot'):
        tweet = {
            'tweet': core.select_proverb(),
            'path': ''
        }

    _is_debug = settings['args']['debug'] | settings['main']['debug']
    if (_is_debug is False):
        if (tweet['path'] != ''):
            twitter.poston_twitter(
                Twitter.TweetMode.TextAndPicture,
                tweet['tweet'],
                tweet['path'])
        else:
            twitter.poston_twitter(
                Twitter.TweetMode.Text,
                tweet['tweet'])
    else:
        if (tweet['path'] != ''):
            twitter.tweet_debug(
                Twitter.TweetMode.TextAndPicture,
                tweet['tweet'],
                tweet['path'])
        else:
            twitter.tweet_debug(
                Twitter.TweetMode.Text,
                tweet['tweet'])
