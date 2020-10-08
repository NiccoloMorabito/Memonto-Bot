'''PICKLER for dumping and loading data in files'''

import pickle
import os

USERS_FOLDER_PATH = 'users/'
COUNTER_FILE_PATH = 'counter.pckl'
REMINDERS_FILE_PATH = '/reminders.pckl'
LANGUAGE_FILE_PATH = '/language.pckl'

def generate_memonto_id():
    '''Dump and load of the MEMONTO_ID_COUNT variable. The value of this variable is used to assign an id to each memonto.'''
    with open(COUNTER_FILE_PATH, 'rb') as f:
        counter = pickle.load(f)
        counter += 1
    with open(COUNTER_FILE_PATH, 'wb') as f:
        pickle.dump(counter, f)
        
    return counter

def save_language_choice(user, language):
    '''Saves language as the selected language of user.'''
    path = USERS_FOLDER_PATH + user + LANGUAGE_FILE_PATH
    with open(path, 'wb') as f:
        pickle.dump(language, f)
        
def load_language_choice(user):
    '''Returns language selected by the user.'''
    path = USERS_FOLDER_PATH + user + LANGUAGE_FILE_PATH
    if not os.path.isfile(path):
        return 'en'
    with open(path, 'rb') as f:
        return pickle.load(f)
    
def save_reminder(user, minutes):
    '''Saves a reminder for the user.
    If time == 'h' -> convert number from hours to minutes
    If time == 'd' -> convert number from days to minutes.
    
    It returns False if the limit of reminders is reached.'''
    
    path = USERS_FOLDER_PATH + user + REMINDERS_FILE_PATH
    # if the file for the user does not exist, creates it with empty list
    if not os.path.isfile(path):
        with open(path, 'wb') as f:
            pickle.dump(set(), f)
    
    # load current reminders
    with open(path, 'rb') as f:
        reminders = pickle.load(f)
    
    # add new reminder to list
    reminders.add(minutes)
    # save new list on the file
    with open(path, 'wb') as f:
        pickle.dump(reminders, f)
    
def save_reminders(user, reminders):
    '''It saves the list of reminders of user substituting the old one.'''
    path = USERS_FOLDER_PATH + user + REMINDERS_FILE_PATH
    with open(path, 'wb') as f:
        pickle.dump(reminders, f)

def load_reminders(user):
    '''Returns the set of the user's reminders.'''
    path = USERS_FOLDER_PATH + user + REMINDERS_FILE_PATH
    if not os.path.isfile(path):
        return set()
    with open(path, 'rb') as f:
        return pickle.load(f)
    
def save_default_reminders(user):
    '''Saves some default reminders for the user.'''
    # default reminders are: 1h, 8h and 1d
    DEFAULT_REMINDERS = { 60, 480, 1440 }
    save_reminders(user, DEFAULT_REMINDERS)