import os
import sys
import json
import glob
import tweepy
import random
import datetime
import argparse
import traceback
from enum import Enum
from typing import Final

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


def poston_twitter(mode: TweetMode, message: str, path=''):
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
                if(mode == TweetMode.Text):
                    print(message)
                elif (mode == TweetMode.TextAndPicture and os.path.exists(path)):
                    print(message)
                    print(path)
            else:
                logger.log_local(Result.Caution, 'Tweet message is empty.')
        else:
            if (mode == TweetMode.Picture):
                api.update_with_media(status='', filename=path)
            elif (message != ''):
                if (mode == TweetMode.Text):
                    api.update_status(message)
                elif (mode == TweetMode.TextAndPicture):
                    api.update_with_media(status=message, filename=path)
            else:
                logger.log_local(Result.Caution, 'Tweet message is empty.')
    except FileNotFoundError as ex:
        logger.log_local(
            Result.Error,
            f'keys.json does not found in {cwd} or picture does not found.',
            ex)
    except Exception as ex:
        logger.log_local(Result.Error, excep_obj=ex)
    else:
        logger.log_local(Result.Success, 'Tweeted successfully.')


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
                        logger.log_local(
                            Result.Caution, 'proverbs list is empty')
                if (proverbs['english']['isEnable']):
                    if (len(proverbs['english']['proverbs']) != 0):
                        english = proverbs['english']['proverbs']
                        e = random.randint(0, len(english) - 1)
                        selected.append(english[e])
                    else:
                        logger.log_local(
                            Result.Caution, 'proverbs list is empty')
                if (proverbs['japanese']['isEnable']):
                    if (len(proverbs['japanese']['proverbs']) != 0):
                        japanese = proverbs['japanese']['proverbs']
                        j = random.randint(0, len(japanese) - 1)
                        selected.append(japanese[j])
                    else:
                        logger.log_local(
                            Result.Caution, 'proverbs list is empty')
                s = random.randint(0, len(selected) - 1)
                return selected[s]
    except Exception as ex:
        logger.log_local(Result.Error, excep_obj=ex)
        return ''


class Logger:
    _log_file = ''
    _log_dir = ''
    _max_log_size = 0
    _is_show_log = False
    _is_ignore_error = False
    _is_log_stacktrace = False

    def __init__(self):
        self._log_file: Final[str] = self._pick_log_file()
        self._log_dir: Final[str] = settings['log']['logDirectory']
        self._max_log_size: Final[int] = settings['log']['maxLogSize']
        self._is_show_log: Final[bool] = settings['main']['isShowLogOutput'] | settings['args']['isShowLogOutput']
        self._is_ignore_error: Final[bool] = settings['main']['ignoreError']
        self._is_log_stacktrace: Final[bool] = settings['main']['isLogStacktrace']
        return

    def _pick_log_file(self):
        logs = glob.glob(self._log_dir + '/*.log')
        if (len(logs) > 0):
            for log in logs:
                if (os.path.getsize(log) <= self._max_log_size):
                    return log

        return f'{self._log_dir}/{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.log'

    def log_local(
            self,
            result: Result,
            message: str = '',
            excep_obj: Exception = None):
        log_message = self._create_log_message(result, message, excep_obj)
        if not os.path.exists(self._log_file):
            if not os.path.exists(self._log_dir):
                os.mkdir(self._log_dir)
            with open(self._log_file, 'w') as f:
                print('', file=f, end='')

        with open(self._log_file, mode='a') as f:
            print(log_message, file=f, end='')
            if (self._is_show_log):
                print(log_message, end='')  # console output

        if (result == Result.Error and self._is_ignore_error is False):
            raise (Exception(excep_obj))

    def _create_log_message(
            self,
            result: Result,
            message: str = '',
            excep_obj: Exception = None):
        dtformat = '%y/%m/%d %H:%M:%S'
        if (result == Result.Error):
            if(excep_obj is None):
                raise ValueError('Exception object is none.')
            else:
                stacktrace = ''
                if (self._is_log_stacktrace):
                    stacktrace = traceback.format_exc()
                if (message == ''):
                    return f'{datetime.datetime.now().strftime(str(dtformat))}  {Result.Error.value} {type(excep_obj)}{excep_obj}\n{stacktrace}'
                else:
                    return f'{datetime.datetime.now().strftime(str(dtformat))}  {Result.Error.value} {type(excep_obj)}{message}\n{stacktrace}'
        else:
            if (message == ''):
                raise ValueError('Log message is empty.')
            else:
                return f'{datetime.datetime.now().strftime(str(dtformat))}  {result.value} {message}\n'
# end log brock


def get_settings():
    settings = {}
    try:
        with open(settings_file, 'r') as raw_json:
            settings = json.load(raw_json)
    except Exception as ex:
        logger.log_local(
            Result.Error,
            f'settings.json does not found in {cwd}.',
            ex)
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
    if (arg.good_morning and arg.good_night):
        arg_values['args']['isDebugMode'] = arg.debug
        arg_values['args']['isShowLogOutput'] = arg.verbose
        return arg_values
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
settings: Final[dict] = parse_args() | get_settings()

logger: Final[Logger] = Logger()

if __name__ == '__main__':
    tweet = select_proverb()
    poston_twitter(TweetMode.Text, tweet)
