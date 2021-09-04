import os
import csv
import json
import glob
import random
import requests
import datetime
from lib import tweepy

keyFile = './keys.json'


class Lbot_core:
    def __init__(self):
        self.logger = Logger()
        try:
            with open(keyFile) as jsonString:
                keys = json.load(jsonString)
            auth = tweepy.OAuthHandler(keys['twitter']['apiKey'], keys['twitter']['apiSecret'])
            auth.set_access_token(keys['twitter']['token'], keys['twitter']['tokenSecret'])
            self._api = tweepy.API(auth)
        except Exception as ex:
            Logger.log_local(Logger(), False, "Failed to load Twitter API keys and tokens", ex)
            Logger.send_line_notify(Logger(), False, "Failed to load Twitter API keys and tokens", ex)

    def post_sentence(self, message):
        try:
            if (message == ""):
                raise ValueError
            else:
                # self._api.update_status(message)
                Logger.log_local(Logger(), True, 'Posted tweet')
                Logger.send_line_notify(Logger(), True, 'Posted tweet')
        except ValueError as ex:
            Logger.log_local(Logger(), False, 'Tweet message was empty.', ex)
            Logger.send_line_notify(Logger(), False, 'Tweet message was empty.', ex)
        except tweepy.TweepError as ex:
            Logger.log_local(Logger(), False, 'Failed to post message', ex)
            Logger.send_line_notify(Logger(), False, 'Failed to post message', ex)

    def post_picture(self, path):
        try:
            self._api.update_with_media(status='', filename=path)
            Logger.log_local(Logger(), True, f'Posted Twitter image at {path}')
            Logger.send_line_notify(Logger(), True, f'Posted Twitter image at {path}')
        except FileNotFoundError as ex:
            Logger.log_local(Logger(), False, 'Cannot open image file', ex)
            Logger.send_line_notify(Logger(), False, 'Cannot open image file', ex)
        except tweepy.TweepError as ex:
            Logger.log_local(Logger(), False, 'Failed to post message', ex)
            Logger.send_line_notify(Logger(), False, 'Failed to post message', ex)

    def post_with_picture(self, message, path):
        try:
            self._api.update_with_media(status=message, filename=path)
            Logger.log_local(Logger(), True, f'Posted with image at {path}')
            Logger.send_line_notify(Logger(), True, f'Posted with image at {path}')
        except FileNotFoundError as ex:
            Logger.log_local(Logger(), False, 'Cannot open image file', ex)
            Logger.send_line_notify(Logger(), False, 'Cannot open image file', ex)
        except tweepy.TweepError as ex:
            Logger.log_local(Logger(), False, 'Failed to post message', ex)
            Logger.send_line_notify(Logger(), False, 'Failed to post message', ex)

    def pick_random_sentence(self, path='./proverbs.csv'):
        try:
            with open(path, 'r') as f:
                csv_lists = csv.reader(f)
                russian = [row[0] for row in csv_lists]
                english = [row[1] for row in csv_lists]
                japanese = [row[2] for row in csv_lists]
                x = random.randint(0, len(russian))
                return [russian[x]]
        except FileNotFoundError as ex:
            Logger.log_local(Logger(), False, 'database does not exists.', ex)
            return ["", "", ""]


class Logger:
    _logFile = ""
    _minLogSize = 640 * 1024

    def __init__(self):
        self.pick_log_file()
        return

    @staticmethod
    def create_log_message(is_failed, message, excep_obj=None,):
        if(is_failed == True):
            return f'{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}  [Succeeded] {message}'
        else:
            if(excep_obj == None):
                try:
                    raise ValueError('Exception Object is nothing.')
                except ValueError as ex:
                    print(ex)
            else:
                return f'{datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")}  [Failed]    {type(excep_obj)}{message}'

    def log_local(self, is_failed, message, excep_obj=None):
        if (self._logFile == ""):
            if (os.path.exists('./log') == False):
                os.mkdir('./log')
            self._logFile = f'./log/{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.log'
            with open(self._logFile, 'w') as f:
                InitMessage = f'{Logger.create_log_message(True, "Created new log file.")}\n{Logger.create_log_message(is_failed, message, excep_obj)}'
                print(InitMessage, file=f)
        else:
            with open(self._logFile, mode='a') as f:
                logMessage = self.create_log_message(is_failed, message, excep_obj)
                print(logMessage, file=f)

    def pick_log_file(self):
        logs = glob.glob('./log/*.log')
        if (len(logs) > 0):
            for p in logs:
                if (os.path.getsize(p) <= self._minLogSize):
                    self._logFile = p
                    return

    def send_line_notify(self, is_failed, message, excep_obj=None):
        try:
            with open(keyFile) as jsonString:
                keys = json.load(jsonString)
            token = keys['line']['token']
            log_message = Logger.create_log_message(is_failed, message, excep_obj)
            line_notify_api_url = 'https://notify-api.line.me/api/notify'
            headers = {'Authorization': f'Bearer {token}'}
            data = {'message': f'\n{log_message}'}
            requests.post(line_notify_api_url, headers=headers, data=data)
            self.log_local(True, "Requested LINE Notify")
        except Exception as ex:
            self.log_local(False, 'Failed to send LINE Notify', ex)


if __name__ == "__main__":
    logger = Logger()
    main = Lbot_core()
    proverbs = main.pick_random_sentence()
    main.post_sentence(proverbs[0])
