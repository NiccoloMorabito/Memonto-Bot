'''UTILS'''

import datetime
import re
import messages
from languages import IT, EN

CHANGELOG_PATH = 'CHANGELOG.md'

TIMESTAMP_FORMAT = '%d/%m/%Y %H:%M'

MINUTE  = 'm'
HOUR    = 'h'
DAY     = 'd'

def get_changes_of(version, lang):
    '''Returns a message for changelogs of the version passed, if exist.'''
    with open(CHANGELOG_PATH, 'r') as f:
        content = f.read()
    
    # if the version passed has changelogs
    # return a text of changes
    if "## [{}] - ".format(version) in content:
        changes = re.split("## \[(.*)\] - (.*)-(.*)-(.*)", content)[5].strip().replace("### ", "")
        return messages.CHANGELOGS_HEADER[lang].format(version) + changes
    # otherwise, error message
    else:
        return messages.NO_CHANGELOGS_MESSAGE[lang].format(version)
    
def get_lang(update, is_query=False):
    '''Function that returns language of user from update (default: en).'''
    if is_query:
        lang = update.inline_query.from_user.language_code
    else:
        lang = update.message.from_user.language_code
    if lang==IT:
        return lang
    return EN

def parse_timestamp(timestamp):
    '''Returns datetime of timestamp is in the following format: DD/MM/YYYY HH:MM, None otherwise.'''
    try:
        d = datetime.datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        return d
    except:
        return None
    
def timestamp_is_passed(parsed_timestamp):
    '''Returns true if parsed_timestamp is passed, false otherwise.'''
    now = datetime.datetime.now()
    diff = parsed_timestamp - now
    if diff.total_seconds() <= 0:
        return True
    else:
        return False

def get_minutes_of(number, time):
    '''
    It returns the number of corresponding minutes.
        number = 30, time = 'm' -> 30
        number = 2, time = 'h' -> 60
        ...
    '''
    if time == DAY:
        return number * 60 * 24
    elif time == HOUR:
        return number * 60
    else:
        return number

def minutes_to_reminder_text(minutes):
    '''
    It returns the missing time as a string:
    30 -> 30m
    50 -> 1h 20m
    ...
    '''
    if minutes <60:
        return str(minutes) + MINUTE
    hours = minutes // 60
    minutes = minutes % 60
    if hours <24:
        s = str(hours) + HOUR
        if minutes != 0:
            s += " " + str(minutes) + MINUTE
        return s
    days = hours // 24
    hours = hours % 24
    s = str(days) + DAY
    if hours != 0:
        s += " " + str(hours) + HOUR
    if minutes != 0:
        s += " " + str(minutes) + MINUTE
    return s