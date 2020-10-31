'''UTILS'''

import datetime
import re
import messages
from languages import IT, EN
from pickler import load_reminders, save_reminders
from constants import CHANGELOG_PATH, DATETIME_FORMAT, DATE_FORMAT, MINUTE, HOUR, DAY
from telegram_bot_calendar import DetailedTelegramCalendar

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
    '''Returns datetime if timestamp is a date or a date and a time, None otherwise.'''    
    try:
        d = datetime.datetime.strptime(timestamp, DATETIME_FORMAT)
        return d
    except:
        try:
            d = datetime.datetime.strptime(timestamp, DATE_FORMAT)
        except:
            return None

def is_time(string):
    '''Checks if string is a time in format HH:MM'''
    try:
        hours, minutes = string.split(":")
        hours = int(hours)
        minutes = int(minutes)
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return True
        return False
    except:
        return False
    
def timestamp_has_passed(parsed_timestamp):
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

def remove_reminder(user, reminder):
    '''It removes the reminder from the reminders of user.'''
    try:
        time = reminder[-1]
        number = int(reminder[:-1])
        minutes = get_minutes_of(number, time)
        reminders = load_reminders(user)
        reminders.remove(minutes)
        save_reminders(user, reminders)
        return True
    except:
        return False


# custom version of python-telegram-bot-calendar with Italian translation and new method
class CustomTelegramCalendar(DetailedTelegramCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.days_of_week[IT] = list('LMMGVSD')
        self.months[IT] = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', \
                           'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
            
    def create(self):
        '''Custom method to build the calendar with current year and month set.'''
        current_month = datetime.datetime.now().month
        current_year  = datetime.datetime.now().year
        # string formatted according to python-telegram-bot-calendar:
        #   cbcal is useless
        #   0 is the calendar_id
        #   s is the 'select' action
        #   m is the 'month' step
        return self.process(f"cbcal_0_s_m_{current_year}_{current_month}_1")