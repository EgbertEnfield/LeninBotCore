import os
import glob
import json
import logging
import datetime
from typing import Final


def extract_log(path: str, range_: tuple[int, int]):
    return


def pick_log_file():
    settings = get_settings()
    log_size_limit = settings['log']['maxLogSize']
    logs = glob.glob(settings['log']['logDirectory'] + '/*.log')
    if (len(logs) > 0):
        for log in logs:
            if (os.path.getsize(log) <= log_size_limit):
                return log

    return ''


def get_settings():
    settings = {}
    try:
        with open(settings_file, 'r') as raw_json:
            settings = json.load(raw_json)
    except Exception as ex:
        raise ex
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


cwd: Final[str] = os.path.dirname(__file__)
log_file: Final[str] = pick_log_file()
settings_file: Final[str] = f'{cwd}/settings.json'
