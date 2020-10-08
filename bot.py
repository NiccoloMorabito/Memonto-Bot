import os
import json
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ParseMode

import messages
import clickables
from clickables import get_menu_keyboard, get_cancel_creation_keyboard, get_cancel_addition_keyboard, get_settings_keyboard, get_time_choice_keyboard, get_changelogs_button, get_language_choice_keyboard, get_help_keyboard, get_cancel_button, get_everything_button
from clickables import get_type_time
from languages import IT, EN
from utils import get_lang, parse_timestamp, timestamp_is_passed, get_minutes_of, minutes_to_reminder_text, get_changes_of
from utils import TIMESTAMP_FORMAT
from pickler import generate_memonto_id, load_language_choice, save_language_choice, save_reminder, save_reminders, load_reminders, save_default_reminders
from tokenbot import TOKEN

# CURRENT VERSION
VERSION = "1.1.1"
LASTUPDATE = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")

REPOSITORY_URL = "https://github.com/NiccoloMorabito/Memonto-Bot"

#paths
USERS_PATH = "users"
MEMONTOS_PATH = "memontos"
JSON = ".json"

# Categories
CATEGORIES = {
    EN : ["Food", "Clothes", "Travel", "eCommerce", "Games", "Beauty", "Experiences", "Other"],
    IT : ["Cibo", "Vestiti", "Viaggi", "eCommerce", "Giochi", "Cura personale", "Esperienze", "Altro"]
}

#memonto fields
ID_FIELD = "id"
CATEG_FIELD = "category"
BRAND_FIELD = "brand"
DESCR_FIELD = "description"
CODE_FIELD  = "code"
TIMESTAMP_FIELD = "timestamp"

FIELD_TEXT = {
    ID_FIELD : {
        EN : "id",
        IT : "id"
    },
    CATEG_FIELD : {
        EN : "Category",
        IT : "Categoria"
    },
    BRAND_FIELD : {
        EN : "Brand",
        IT : "Brand"
    },
    DESCR_FIELD : {
        EN : "Description",
        IT : "Descrizione"
    },
    CODE_FIELD  : {
        EN : "Discount code",
        IT : "Codice sconto"
    },
    TIMESTAMP_FIELD : {
        EN : "Expiring on",
        IT : "Scadenza"
    }
}

#other constants
START_COMMAND = 'start'
all_users = set(os.listdir(USERS_PATH))
user2progr_memonto = dict()
user2time_reminder = dict()
LIMIT_MEMONTOS = 30
LIMIT_REMINDERS = 10
LIMIT_CHARACTERS_LITTLE = 20
LIMIT_CHARACTERS_MEDIUM = 50
LIMIT_CHARACTERS_BIG = 150

# passages of memonto creation
FIRST, SECOND, THIRD, FOURTH, FIFTH = range(5)
# passage of reminder creation
NUMBER = 5



def job_each_minute(context: CallbackContext):
    '''Function that each minute checks existing memontos in order to see if
    they are expiring / if they are expired and notifies consequently
    the corresponding user.'''
    global all_users
    expired_files = set()
    
    for user in all_users:
        reminders = load_reminders(user)
        lang = load_language_choice(user)
        chat_id = int(user)
        memontos_path = get_memontos_path_of(user)
        for file in os.listdir(memontos_path):
            file_path = os.path.join(memontos_path, file)
            with open(file_path, 'r') as f:
                memonto = json.load(f)
            memonto_text = get_memonto_text(memonto, lang)
            try:
                timestamp = datetime.datetime.strptime(
                    memonto[TIMESTAMP_FIELD],
                    TIMESTAMP_FORMAT
                )
            except:
                continue
            now = datetime.datetime.now()
            
            diff = timestamp - now
            missing_minutes = int(diff.total_seconds()//60)
            
            # if memonto has expired, delete it
            if missing_minutes <= 0:
                expired_files.add(file_path)
                context.bot.send_message(
                    chat_id,
                    messages.MEMONTO_EXPIRED[lang].format(memonto_text, parse_mode=ParseMode.MARKDOWN)
                )
                
            # if difference between now and memonto timestamp is in the reminders set,
            # then send a notification for expiring memonto
            if missing_minutes in reminders:
                context.bot.send_message(
                    chat_id,
                    messages.EXPIRING_MEMONTO[lang].format(
                        minutes_to_reminder_text(missing_minutes),
                        memonto_text
                    ),
                    parse_mode=ParseMode.MARKDOWN
                )
    
    for path in expired_files:
        os.remove(path)



'''
START
'''

def start_command(update, context):
    '''The function that is invoked with the "start" command.'''
    user = str(update.message.chat_id)
    
    # actions for new users
    if user not in all_users:
        all_users.add(user)
        os.mkdir(os.path.join(USERS_PATH, user))
        os.mkdir(get_memontos_path_of(user))
        save_language_choice(user, get_lang(update))
        save_default_reminders(user)

    lang = load_language_choice(user)
    
    # check if another memonto for the same user is in progress
    if user in user2progr_memonto.keys():
        id_memonto = user2progr_memonto[user]
        file_path = get_memonto_path_of(user, id_memonto)
        with open(file_path, 'r') as f:
            memonto = json.load(f)
        # if there is no timestamp, that memonto is still in progress -> remove old memonto
        if memonto[TIMESTAMP_FIELD] == "":
            os.remove(file_path)
            update.message.reply_text(messages.OLD_MEMONTO_DELETED[lang])
        user2progr_memonto.pop(user, None)

    # welcome message only if the user typed /start
    if update.message.text == '/' + START_COMMAND:
        update.message.reply_text(
            messages.WELCOME[lang],
            reply_markup = get_menu_keyboard(lang)
        )
    else:
        update.message.reply_text(
            messages.MENU[lang],
            reply_markup = get_menu_keyboard(lang)
        )


   
'''
MEMONTO CREATION
In order to create a memonto you need to specify:
    - category
    - brand name
    - description
    - discount code
    - expiring date
'''
    
def newmemonto_command(update, context):
    '''The function that is invoked with the "new-memonto" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    # create empty memonto
    id_memonto = create_memonto(user)
    # if limit reached -> stop creation
    if id_memonto==-1:
        update.message.reply_text(
            messages.LIMIT_REACHED[lang],
            reply_markup = get_menu_keyboard(lang)
        )
        return ConversationHandler.END
    
    user2progr_memonto[user] = id_memonto
    update.message.reply_text(
        messages.CREATION_STARTED[lang].format(id_memonto),
        reply_markup=ReplyKeyboardRemove()
    )
    
    # inline keyboard for category choice (all categories + 'cancel' option)
    # organized into two columns
    buttons = list()
    catgs = CATEGORIES[lang]
    for cat1, cat2 in zip(catgs[0::2], catgs[1::2]):
        buttons.append([
            InlineKeyboardButton( cat1, callback_data = cat1 ),
            InlineKeyboardButton( cat2, callback_data = cat2 )
        ])
    if len(catgs) % 2 == 1:
        buttons.append([InlineKeyboardButton( catgs[-1], callback_data = catgs[-1] )])
    buttons.append(get_cancel_creation_keyboard(lang).inline_keyboard[0])
        
    update.message.reply_text(
        messages.CHOOSE_CATEGORY[lang],
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    
    return FIRST

def categ_query(update, context):
    '''It saves inserted category of memonto and asks for brand.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # save selected category in both languages
    categ = query.data
    i = CATEGORIES[lang].index(categ)
    tosave = { EN : CATEGORIES[EN][i], IT : CATEGORIES[IT][i]}
    save_field_in_memonto(user, CATEG_FIELD, tosave)
    
    # asking for brand name
    query.edit_message_text(messages.CATEGORY_SELECTED[lang].format(categ))
    query.answer()
    query.message.reply_text(
        messages.INSERT_BRAND[lang],
        reply_markup = get_cancel_creation_keyboard(lang)
    )
    
    return SECOND

def brand_memonto(update, context):
    '''It saves inserted brand of memonto and asks for description.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    
    # checking limit of characters
    if len(text) > LIMIT_CHARACTERS_LITTLE:
        update.message.reply_text(
            messages.TOO_MANY_CHARACTERS[lang].format(LIMIT_CHARACTERS_LITTLE), 
            reply_markup = get_cancel_creation_keyboard(lang)
        )
        return SECOND
    
    save_field_in_memonto(user, BRAND_FIELD, text)

    # asking for description
    update.message.reply_text(
        messages.INSERT_DESCRIPTION[lang],
        reply_markup = get_cancel_creation_keyboard(lang)
    )

    return THIRD

def description_memonto(update, context):
    '''It saves inserted description of memonto and asks for discount code.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    
    # checking limit of characters
    if len(text) > LIMIT_CHARACTERS_BIG:
        update.message.reply_text(
            messages.TOO_MANY_CHARACTERS[lang].format(LIMIT_CHARACTERS_BIG),
            reply_markup = get_cancel_creation_keyboard(lang)
        )
        return THIRD
    
    save_field_in_memonto(user, DESCR_FIELD, text)
    
    update.message.reply_text(
        messages.INSERT_CODE[lang],
        reply_markup = get_cancel_creation_keyboard(lang)
    )

    return FOURTH

def code_memonto(update, context):
    '''It saves inserted discount code of memonto and asks for expiring date.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    
    # limit of characters
    if len(text) > LIMIT_CHARACTERS_MEDIUM:
        update.message.reply_text(
            messages.TOO_MANY_CHARACTERS[lang].format(LIMIT_CHARACTERS_LITTLE),
            reply_markup = get_cancel_creation_keyboard(lang)
        )
        return FOURTH
    
    save_field_in_memonto(user, CODE_FIELD, text)
        
    update.message.reply_text(
        messages.INSERT_TIMESTAMP[lang],
        reply_markup = get_cancel_creation_keyboard(lang)
    )

    return FIFTH

def expiring_date_memonto(update, context):
    '''It saves inserted expiring date (if it is valid)
    of memonto and it ends memonto creation process.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text

    parsed_timestamp = parse_timestamp(text)
    # check if timestamp is in the correct format
    if parsed_timestamp != None:
        # check if timestamp is passed
        if timestamp_is_passed(parsed_timestamp):
            update.message.reply_text(
                messages.TIMESTAMP_PASSED[lang],
                reply_markup = get_cancel_creation_keyboard(lang)
            )
            return FIFTH
        
        memonto = save_field_in_memonto(
            user, TIMESTAMP_FIELD,
            parsed_timestamp.strftime(TIMESTAMP_FORMAT)
        )
            
        # memonto for user is no more in progress
        user2progr_memonto.pop(user, None)
        update.message.reply_text(messages.MEMONTO_CREATED[lang])
        update.message.reply_text(
            get_memonto_text(memonto, lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup = get_menu_keyboard(lang)
        )
        return ConversationHandler.END
    
    else:
        update.message.reply_text(
            messages.TIMESTAMP_NOT_VALID[lang],
            reply_markup = get_cancel_creation_keyboard(lang)
        )
        return FIFTH

def newmemonto_cancel(update, context):
    '''It cancels memonto creation process deleting
    the memonto that was being created.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    id_memonto = user2progr_memonto[user]
    file_path = get_memonto_path_of(user, id_memonto)

    os.remove(file_path)
    query.edit_message_text(messages.MEMONTO_CREATION_CANCELED[lang])
    query.answer()
    query.message.reply_text(
        messages.OLD_MEMONTO_DELETED[lang],
        reply_markup = get_menu_keyboard(lang)
    )
    user2progr_memonto.pop(user, None)
    
    return ConversationHandler.END



'''
LIST MEMONTO
Command to list all the memontos saved by the user which
are still available (not deleted and not expired).
'''
    
def listmemontos_command(update, context):
    '''The function that is invoked with the "list-memonto" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    memontos = get_memontos_list(user, lang)
    if not memontos:
        update.message.reply_text(messages.NOMEMONTOS[lang])
    # sending a message for each available memonto of user
    else:
        for memonto_text in memontos:
            update.message.reply_text(memonto_text, parse_mode=ParseMode.MARKDOWN)



'''
DELETE MEMONTO
In order to delete a memonto you need to click on the corresponding
button or you can click on "Delete all" button.
'''

def deletememonto_command(update, context):
    '''The function that is invoked with the "delete-memonto" command.
    If there are available memontos, it send a keyboard to choose 
    what to delete.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)

    memontos = get_memontos_list(user, lang)
    if not memontos:
        update.message.reply_text(messages.NOMEMONTOS[lang])
        return
    
    buttons = list()
    # cancel button to cancel the operation
    buttons.append(get_cancel_button(lang, 1))
    # a button for each deletable memonto
    for memonto in memontos:
        buttons.append([InlineKeyboardButton(
            memonto.split("\n")[0],
            callback_data = memonto.split("\n")[0] 
        )])
    # delete-all button to delete all the memontos
    buttons.append(get_everything_button(lang, 1))
    
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    # sending created keyboard
    update.message.reply_text(
        messages.DELETE_MEMONTO[lang],
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    
def deletememonto_query(update, context):
    '''It reads what button has been selected for the deletion of a memonto.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    memonto_id = query.data.split("#")[1]
    
    # if cancel button pressed, cancel operation
    if memonto_id == clickables.CANCEL_CODE:
        text = messages.OPERATION_CANCELED[lang]
        
    # elif delete-all button pressed, delete all memontos
    elif memonto_id == clickables.EVERYTHING_CODE:
        mids = get_memontos_ids_list(user)
        # if at least one deletion does not finish correctly, change message text
        b = True
        for mid in mids:
            if not delete_memonto(user, mid):
                b = False
        if b:
            text = messages.ALL_MEMONTOS_DELETED[lang]
        else:
            text = messages.SOMETHING_WENT_WRONG[lang]
        
    # delete just the single memonto selected
    elif delete_memonto(user, memonto_id):
        text = messages.MEMONTO_DELETED[lang].format(memonto_id)
    else:
        text = messages.SOMETHING_WENT_WRONG[lang]
        
    query.edit_message_text(text)
    query.answer()
    query.message.reply_text(
        messages.MENU[lang],
        reply_markup = get_menu_keyboard(lang)
    )
    


'''
SETTINGS
'''

def settings_command(update, context):
    '''The function that is invoken with the "settings" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    update.message.reply_text(
        update.message.text,
        reply_markup = get_settings_keyboard(lang)
    )



'''
REMINDER ADDITION
The reminder addition starts with the corresponding button.
In order to add a reminder you need to specify:
    - time (minutes, hours or days)
    - number
The reminder is than saved as an integer which represents the
number of minutes.
'''

def addreminder_command(update, context):
    '''The function that is invoked with the "add-reminder" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    # checking limit of reminders
    if len(load_reminders(user)) == LIMIT_REMINDERS:
        update.message.reply_text(messages.REMINDER_LIMIT[lang])
        return ConversationHandler.END 
        
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    # asking for time (minutes, hours or days)
    update.message.reply_text(
        messages.REMINDER_TIME_CHOICE[lang],
        reply_markup = get_time_choice_keyboard(lang)
    )
    
    return NUMBER

def addreminder_query(update, context):
    '''It reads what button has been selected for the time of reminders
    and saves it in a dictionary.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    user2time_reminder[user] = query.data
    
    # asking for number
    query.edit_message_text(
        messages.INSERT_REMINDER_NUMBER[lang].format(get_type_time(query.data, lang)),
        reply_markup = get_cancel_addition_keyboard(lang)
    )
    query.answer()
    
def addreminder_number(update, context):
    '''It saves the reminder.'''
    user = str(update.message.chat_id)
    text = update.message.text
    lang = load_language_choice(user)

    # user is creating a reminder
    if user in user2time_reminder.keys():
        #
        if not text.isdigit():
            update.message.reply_text(
                messages.REMINDER_NUMBER_NOT_VALID[lang],
                reply_markup = get_cancel_addition_keyboard(lang)
            )
            return NUMBER
        else:
            # save reminder
            minutes = get_minutes_of(int(text), user2time_reminder[user])
            save_reminder(user, minutes)
            update.message.reply_text(
                messages.REMINDER_CREATED[lang].format(minutes_to_reminder_text(minutes)),
                reply_markup = get_settings_keyboard(lang)
            )          
            user2time_reminder.pop(user, None)
            
            return ConversationHandler.END    

def addreminder_cancel(update, context):
    '''It cancels reminder addition process.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    query.edit_message_text(messages.REMINDER_ADDITION_CANCELED[lang])
    query.answer()
    query.message.reply_text(
        messages.OLD_REMINDER_DELETED[lang],
        reply_markup = get_settings_keyboard(lang)
    )
    
    return ConversationHandler.END



'''
REMOVE REMINDER
In order to remove a reminder you need to click on the corresponding
button or you can click on "Remove all" button.
'''

def removereminder_command(update, context):
    '''The function that is invoked with the "remove-reminder" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    reminders = load_reminders(user)
    if not reminders:
        update.message.reply_text(messages.NOREMINDERS[lang])
        return
    
    buttons = list()
    # cancel button to cancel the operation
    buttons.append(get_cancel_button(lang, 2))
    # a button for each removable reminder
    for reminder in reminders:
        reminder_text = minutes_to_reminder_text(reminder)
        buttons.append([InlineKeyboardButton(
            reminder_text,
            callback_data = reminder_text
        )])
    # remove-all button to remove all reminders
    buttons.append(get_everything_button(lang, 2))
    
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    # sending created keyboard
    update.message.reply_text(
        messages.REMOVE_REMINDER[lang],
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    
def removeaddreminder_query(update, context):
    '''It reads what button has been selected for the remotion of a reminder.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    reminder = query.data
    
    # if cancel button pressed, cancel operation
    if reminder[:-1] == clickables.CANCEL_CODE:
        text = messages.OPERATION_CANCELED[lang]
    
    # elif remove-all button pressed, remove all reminders
    elif reminder[:-1] == clickables.EVERYTHING_CODE:
        save_reminders(user, set())
        text = messages.ALL_REMINDERS_REMOVED[lang]
    
    # remove just the single reminder selected
    elif remove_reminder(user, reminder):
        text = messages.REMINDER_REMOVED[lang].format(reminder)
    else:
        text = messages.SOMETHING_WENT_WRONG[lang]
        
    query.edit_message_text(text)
    query.answer()
    query.message.reply_text(
        messages.MENU[lang], 
        reply_markup = get_settings_keyboard(lang)
    )



'''
CHANGE LANGUAGE
'''
    
def changelanguage_command(update, context):
    '''The function that is invoked with the "change-language" command.'''
    update.message.reply_text(
        messages.LANGUAGE_CHOICE,
        reply_markup = get_language_choice_keyboard()
    )

def changelanguage_query(update, context):
    '''It reads what language has been selected.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = query.data
    save_language_choice(user, lang)
    
    query.edit_message_text(messages.LANGUAGE_SELECTED[lang])
    query.answer()
    query.message.reply_text(
        messages.WELCOME[lang],
        reply_markup = get_menu_keyboard(lang)
    )



'''
HELP
The help command sends a message with all the important information about
the bot. In order to organize everything, the message shows some inline
buttons, each of one adds some text to the initial message.
'''

def help_command(update, context):
    '''The function that is invoked with the "help" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    # replying with the complete keyboards (two buttons)
    update.message.reply_text(
        messages.HELP[lang],
        reply_markup = get_help_keyboard(lang, True, True)
    )
    
def help_query(update, context):
    '''It reads what button has been selected for adding text to help message.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # first, the answer contains the old message
    answer = query.message.text
    
    # plus How to manage memonto, if that was clicked
    if query.data == clickables.HELP1_CODE:
        answer += "\n\n" + messages.HELP1[lang]
        # if the inline keyboard contained two buttons, answer with the remaining one
        if len(query.message.reply_markup.inline_keyboard) == 2:
            keyboard = get_help_keyboard(lang, False, True)
        # otherwise, both buttons have been pressed
        else:
            keyboard = get_help_keyboard(lang, False, False)
    # or plus How to manage reminders, if that was clicked
    elif query.data == clickables.HELP2_CODE:
        answer += "\n\n" + messages.HELP2[lang]
        # if the inline keyboard contained two buttons, answer with the remaining one
        if len(query.message.reply_markup.inline_keyboard) == 2:
            keyboard = get_help_keyboard(lang, True, False)
        # otherwise, both buttons have been pressed
        else:
            keyboard = get_help_keyboard(lang, False, False)

    query.edit_message_text(answer, reply_markup = keyboard)



'''
INFO
The info command sends a message with version, last update and changelogs
(readable through the corresponding inline button).
'''

def info_command(update, context):
    '''The function that is invoked with the "info" command.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    update.message.reply_text(
        messages.INFO[lang].format(VERSION, LASTUPDATE, REPOSITORY_URL),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup = get_changelogs_button(lang)
    )
    
def info_query(update, context):
    '''The function that is invoked with the "changelogs" command.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # send changelogs of this version
    changes = get_changes_of(VERSION, lang)
    query.edit_message_text(changes)
    query.answer()


















def create_memonto(user):
    '''It creates and dumps an empty memonto with an incremental id in the user folder.'''
    memontos_folder = get_memontos_path_of(user)
    # check if limit of memonto reached
    n = len(os.listdir(memontos_folder)) + 1
    if n > LIMIT_MEMONTOS:
        return -1
    
    MEMONTO_ID_COUNT = generate_memonto_id()
    empty_memonto = {
        ID_FIELD: MEMONTO_ID_COUNT,
        CATEG_FIELD: {EN : "", IT : ""},
        BRAND_FIELD: "",
        DESCR_FIELD: "",
        CODE_FIELD : "",
        TIMESTAMP_FIELD: ""
    }
    
    # save empty memonto as json into the user folder
    file_path = get_memonto_path_of(user, str(MEMONTO_ID_COUNT))
    with open(file_path, 'w') as f:
        json.dump(empty_memonto, f)
    
    return MEMONTO_ID_COUNT

def save_field_in_memonto(user, field, content):
    id_memonto = user2progr_memonto[user]
    file_path = get_memonto_path_of(user, id_memonto)
    
    with open(file_path, 'r') as f:
        memonto = json.load(f)
    memonto[field] = content
    with open(file_path, 'w') as f:
        json.dump(memonto, f)
    
    return memonto

def delete_memonto(user, id_memonto):
    '''It deletes the memonto with memonto_id as id from the memontos of user.'''
    file_path = get_memonto_path_of(user, id_memonto)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False

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

def get_memontos_list(user, lang):
    '''It returns a list of all the memontos' texts created by the user.'''
    memontos = list()
    
    memontos_path = get_memontos_path_of(user)
    for file in os.listdir(memontos_path):
        file_path = os.path.join(memontos_path, file)
        with open(file_path, 'r') as f:
            memonto = json.load(f)
        memontos.append(get_memonto_text(memonto, lang))
    
    return memontos

def get_memontos_ids_list(user):
    '''Returns a list of ids, where each id corresponds to a memonto of user.'''
    paths = list()
    
    for file in os.listdir(get_memontos_path_of(user)):
        paths.append(file.split(JSON)[0])
        
    return paths
        
def get_memonto_text(memonto, lang):
    '''It returns a string correctly formatted with all the fields of memonto.'''
    return "MEMONTO #{}\n\n".format(memonto[ID_FIELD]) +\
            FIELD_TEXT[CATEG_FIELD][lang]       + ": " +\
                memonto[CATEG_FIELD][lang] + "\n" +\
            FIELD_TEXT[BRAND_FIELD][lang]       + ": " +\
                memonto[BRAND_FIELD]       + "\n" +\
            FIELD_TEXT[DESCR_FIELD][lang]       + ": " +\
                memonto[DESCR_FIELD]       + "\n" +\
            FIELD_TEXT[CODE_FIELD][lang]        + ": ```\n" +\
                memonto[CODE_FIELD]        + "```\n" +\
            FIELD_TEXT[TIMESTAMP_FIELD][lang]   + ": " +\
                memonto[TIMESTAMP_FIELD]
    
def get_memontos_path_of(user):
    '''Returns the path in which there are all the memontos (json files) of user.'''
    return os.path.join(USERS_PATH, user, MEMONTOS_PATH)

def get_memonto_path_of(user, id_memonto):
    '''Returns the path of the memonto file for the user passed with the id passed.'''
    return os.path.join(get_memontos_path_of(user), str(id_memonto) + JSON)



# BOT
updater = Updater(TOKEN, use_context=True)
# start job_each_minute for checking memontos
job_queue = updater.job_queue
job_minute = job_queue.run_repeating(job_each_minute, interval=60, first=0)

# HANDLERs
dp = updater.dispatcher
dp.add_handler(CommandHandler(START_COMMAND, start_command))

for lang in [EN, IT]:
    # adding conversation handler with the states BRAND, DESCRIPTION, CODE and EXPIRATION DATE
    categ_pattern = "^(" + ")$|^(".join(CATEGORIES[lang]) + ")$"
    NOTBACK = ~Filters.regex(clickables.BACK[lang])
    memonto_creation_handler = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.NEWMEMONTO[lang]),
            newmemonto_command
        )],
    
        states={
            FIRST:  [CallbackQueryHandler(categ_query, pattern=categ_pattern)],
            SECOND: [MessageHandler(Filters.text & NOTBACK, brand_memonto)],
            THIRD:  [MessageHandler(Filters.text & NOTBACK, description_memonto)],
            FOURTH: [MessageHandler(Filters.text & NOTBACK, code_memonto)],
            FIFTH:  [MessageHandler(Filters.text & NOTBACK, expiring_date_memonto)]
        },
    
        fallbacks=[CallbackQueryHandler(
            newmemonto_cancel,
            pattern="^" + clickables.CANCEL_CREATION[lang] + "$"
        )]
    )
    dp.add_handler(memonto_creation_handler)
    
    # list memonto handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.LISTMEMONTOS[lang]),
        listmemontos_command
    ))
    
    # delete memonto handlers
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.DELETEMEMONTO[lang]),
        deletememonto_command
    ))
    dp.add_handler(CallbackQueryHandler(
        deletememonto_query,
        pattern="^MEMONTO #(.*)"
    ))
    
    # setting handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.SETTINGS[lang]),
        settings_command
    ))
    
    # adding conversation handler for the reminder creation
    reminder_addition_handler = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.ADDREMINDER[lang]),
            addreminder_command
        )],
    
        states={
            NUMBER: [MessageHandler(Filters.text, addreminder_number)]
        },
        
        fallbacks=[CallbackQueryHandler(
            addreminder_cancel,
            pattern="^" + clickables.CANCEL_ADDITION[lang] + "$"
        )]
    )
    dp.add_handler(reminder_addition_handler)
    dp.add_handler(CallbackQueryHandler(addreminder_query, pattern="^(d|h|m)$"))
    
    # remove reminder handlers
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.REMOVEREMINDER[lang]),
        removereminder_command
    ))
    dp.add_handler(CallbackQueryHandler(
        removeaddreminder_query,
        pattern="(.*)(d|h|m)$"
    ))
    
    # change language handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.CHANGELANGUAGE[lang]),
        changelanguage_command
    ))
    dp.add_handler(CallbackQueryHandler(changelanguage_query, pattern="^(en|it)$"))
    
    # back handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.BACK[lang]),
        start_command
    ))
    
    # help handlers
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.HELP[lang]),
        help_command
    ))
    dp.add_handler(CallbackQueryHandler(help_query, pattern="^help(1|2)$"))
    
    # info handlers
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.INFO[lang]),
        info_command
    ))
    dp.add_handler(CallbackQueryHandler(
        info_query,
        pattern="^" + clickables.CHANGELOGS[lang] + "$"
    ))


# starting the Bot
updater.start_polling()
updater.idle()