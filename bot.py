import os
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ParseMode

from tokenbot import TOKEN
import constants
import messages
import clickables
from clickables import get_menu_keyboard, get_cancel_creation_keyboard, get_cancel_addition_keyboard, get_settings_keyboard, get_time_choice_keyboard, get_changelogs_button, get_language_choice_keyboard, get_help_keyboard, get_cancel_button, get_everything_button, get_type_time
from languages import IT, EN
from utils import get_lang, parse_timestamp, timestamp_has_passed, get_minutes_of, minutes_to_reminder_text, get_changes_of, is_time, remove_reminder, CustomTelegramCalendar
from pickler import load_language_choice, save_language_choice, save_reminder, save_reminders, load_reminders, save_default_reminders
import Memonto

# CURRENT VERSION
VERSION = "1.2"
LASTUPDATE = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")

# constants for ConversationHandler states
FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH = range(6)

all_users = set(os.listdir(constants.USERS_PATH))
user2progr_memonto = dict()
user2prog_memonto_msg = dict()
user2time_reminder = dict()

def job_each_minute(context: CallbackContext):
    '''Function that each minute checks existing memontos in order to see if
    they are expiring / if they are expired and notifies consequently
    the corresponding user.'''
    global all_users
    
    for user in all_users:
        expired_memontos = set()
        reminder_to_memontos = dict()
        reminders = load_reminders(user)
        for reminder in reminders:
            reminder_to_memontos[reminder] = set()
        lang = load_language_choice(user)
        chat_id = int(user)
        memontos = Memonto.get_memontos_list(user)
        for memonto in memontos:
            try:
                timestamp = datetime.datetime.strptime(
                    memonto.timestamp,
                    constants.DATETIME_FORMAT
                )
            except:
                continue
            now = datetime.datetime.now()
            diff = timestamp - now
            missing_minutes = int(diff.total_seconds()//60)+1
            
            # if memonto has expired, notification of expiration needs 
            # to be sent and the memonto to be deleted
            if missing_minutes <= 0:
                expired_memontos.add(memonto)
                
            # if difference between now and memonto timestamp is in the reminders set,
            # then notification for expiring memonto needs to be sent
            if missing_minutes in reminders:
                reminder_to_memontos[missing_minutes].add(memonto)
        
        # send a message for each group of memontos expiring in a certain time
        for missing_minutes, memontos in reminder_to_memontos.items():
            if memontos:
                text = messages.EXPIRING_MEMONTO[lang].format(
                    minutes_to_reminder_text(missing_minutes),
                    Memonto.get_string_of_memontos(lang, memontos)
                )
                context.bot.send_message(
                    chat_id,
                    text,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        # send a notification for all memontos that are going to be deleted
        # (if there is at least one)
        if expired_memontos:
            context.bot.send_message(
                chat_id,
                messages.MEMONTO_EXPIRED[lang].format(
                    Memonto.get_string_of_memontos(lang, expired_memontos)
                ),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # actually delete expired memontos
        for memonto in expired_memontos:
            memonto.delete()



'''
START
'''

def start_command(update, context):
    '''The function that is invoked with the "start" command.'''
    user = str(update.message.chat_id)
    
    # actions for new users
    if user not in all_users:
        all_users.add(user)
        os.mkdir(os.path.join(constants.USERS_PATH, user))
        os.mkdir(Memonto.get_memontos_path_of(user))
        save_language_choice(user, get_lang(update))
        save_default_reminders(user)

    lang = load_language_choice(user)
    
    # check if another memonto for the same user is in progress
    if user in user2progr_memonto.keys():
        update.message.reply_text(messages.OLD_MEMONTO_DELETED[lang])
        user2progr_memonto.pop(user, None)

    # welcome message + menu
    update.message.reply_text(
        messages.WELCOME[lang],
        reply_markup = get_menu_keyboard(lang)
    )
    
'''
HOME
'''

def home_command(update, context):
    '''The function that is invoked to show the home menu.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    # check if another memonto for the same user is in progress
    if user in user2progr_memonto.keys():
        update.message.reply_text(messages.OLD_MEMONTO_DELETED[lang])
        user2progr_memonto.pop(user, None)

    # menu message
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
    memonto = Memonto.create_memonto(user)
    # if limit reached -> stop creation
    if memonto==None:
        update.message.reply_text(
            messages.LIMIT_REACHED[lang],
            reply_markup = get_menu_keyboard(lang)
        )
        return ConversationHandler.END
    
    update.message.reply_text(
        messages.CREATION_STARTED[lang],
        reply_markup=ReplyKeyboardRemove()
    )
    user2progr_memonto[user] = memonto
    
    # inline keyboard for category choice (all categories + 'cancel' option)
    # organized into two columns
    buttons = list()
    catgs = constants.CATEGORIES[lang]
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
    i = constants.CATEGORIES[lang].index(categ)
    tosave = { EN : constants.CATEGORIES[EN][i], IT : constants.CATEGORIES[IT][i]}
    user2progr_memonto[user].category = tosave
    
    # delete query message
    # msg = query.edit_message_text(messages.CATEGORY_SELECTED[lang].format(categ))
    context.bot.delete_message(
        chat_id=user,
        message_id=query.message.message_id
    )
    query.answer()
    # message with memonto in progress and request for brand
    user2prog_memonto_msg[user] = query.message.reply_text(
        user2progr_memonto[user].to_string(lang) +\
            "\n\n" + messages.INSERT_BRAND[lang],
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_cancel_creation_keyboard(lang)
    )
    
    return SECOND

def brand_memonto(update, context):
    '''It saves inserted brand of memonto and asks for description.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    # delete message of user
    context.bot.delete_message(
        chat_id=user,
        message_id=update.message.message_id
    )
    
    # checking limit of characters
    limit_brand = constants.LIMIT_CHARACTERS_LITTLE
    if len(text) > limit_brand:
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2prog_memonto_msg[user].text_markdown +\
                "\n" + messages.TOO_MANY_CHARACTERS[lang].format(limit_brand),
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = get_cancel_creation_keyboard(lang)
        )
        return SECOND
    
    user2progr_memonto[user].brand = text

    # message with memonto in progress and request for description
    # editing the previous prog_memonto_msg
    user2prog_memonto_msg[user] = context.bot.edit_message_text(
    	chat_id = user,
    	message_id = user2prog_memonto_msg[user].message_id,
    	text = user2progr_memonto[user].to_string(lang) +\
            "\n\n" + messages.INSERT_DESCRIPTION[lang],
        parse_mode=ParseMode.MARKDOWN,
    	reply_markup = get_cancel_creation_keyboard(lang)
    )

    return THIRD

def description_memonto(update, context):
    '''It saves inserted description of memonto and asks for discount code.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    # delete message of user
    context.bot.delete_message(
        chat_id=user,
        message_id=update.message.message_id
    )
    
    # checking limit of characters
    limit_description = constants.LIMIT_CHARACTERS_MEDIUM
    if len(text) > limit_description:
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2prog_memonto_msg[user].text_markdown +\
                "\n" + messages.TOO_MANY_CHARACTERS[lang].format(limit_description),
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = get_cancel_creation_keyboard(lang)
        )
        return THIRD
    
    user2progr_memonto[user].description = text
    
    # message with memonto in progress and request for description
    # editing the previous prog_memonto_msg
    user2prog_memonto_msg[user] = context.bot.edit_message_text(
    	chat_id = user,
    	message_id = user2prog_memonto_msg[user].message_id,
    	text = user2progr_memonto[user].to_string(lang) +\
            "\n\n" + messages.INSERT_CODE[lang],
        parse_mode=ParseMode.MARKDOWN,
    	reply_markup = get_cancel_creation_keyboard(lang)
    )

    return FOURTH

def code_memonto(update, context):
    '''It saves inserted discount code of memonto and asks for expiring date.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    # delete message of user
    context.bot.delete_message(
        chat_id=user,
        message_id=update.message.message_id
    )
    
    # limit of characters
    limit_code = constants.LIMIT_CHARACTERS_MEDIUM
    if len(text) > limit_code:
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2prog_memonto_msg[user].text_markdown +\
                "\n" + messages.TOO_MANY_CHARACTERS[lang].format(limit_code),
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = get_cancel_creation_keyboard(lang)
        )
        return FOURTH
    
    user2progr_memonto[user].code = text
    
    # generation of calendar for expiring date
    result, calendar, step = CustomTelegramCalendar(locale=lang).create()
    # message with memonto in progress and request for description
    # editing the previous prog_memonto_msg
    user2prog_memonto_msg[user] = context.bot.edit_message_text(
    	chat_id = user,
    	message_id = user2prog_memonto_msg[user].message_id,
    	text = user2progr_memonto[user].to_string(lang) +\
            "\n\n" + messages.SELECT_DATE[lang],
        parse_mode=ParseMode.MARKDOWN,
    	reply_markup = calendar
    )
    
    return FIFTH

def expiring_date_query_memonto(update, context):
    '''It reads what day has been selected from the inline calendar and answer accordingly.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    result, key, step = CustomTelegramCalendar(locale=lang).process(query.data)
    # if the selection is not the final date but it's for some intermediate step
    if not result and key:
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2progr_memonto[user].to_string(lang) +\
                "\n\n" + messages.SELECT_DATE[lang],
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = key
        )
        return FIFTH
    # elif date has been selected
    elif result:
        date = result.strftime(constants.DATE_FORMAT)
        parsed_timestamp = parse_timestamp(date + " 23:59")
        
        # selected day has passed
        if timestamp_has_passed(parsed_timestamp):
            query.answer()
            result, calendar, step = CustomTelegramCalendar(locale=lang).create()
            user2prog_memonto_msg[user] = context.bot.edit_message_text(
            	chat_id = user,
            	message_id = user2prog_memonto_msg[user].message_id,
            	text = user2prog_memonto_msg[user].text_markdown +\
                    "\n" + messages.DATE_PASSED[lang],
                parse_mode=ParseMode.MARKDOWN,
            	reply_markup = calendar
            )
            return FIFTH
        
        #if date is ok, save it and ask for time
        user2progr_memonto[user].timestamp = date
        
        query.edit_message_text(messages.DATE_SELECTED[lang].format(date))
        query.answer()
        # message with memonto in progress and request for description
        # editing the previous prog_memonto_msg
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2progr_memonto[user].to_string(lang) +\
                "\n\n" + messages.INSERT_TIME[lang],
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = get_cancel_creation_keyboard(lang)
        )
        return SIXTH
    
def expiring_time_memonto(update, context):
    '''It saves inserted expiring timestamp (if time is valid)
    of memonto and it ends memonto creation process.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    text = update.message.text
    # delete message of user
    context.bot.delete_message(
        chat_id=user,
        message_id=update.message.message_id
    )

    if not is_time(text):
        user2prog_memonto_msg[user] = context.bot.edit_message_text(
        	chat_id = user,
        	message_id = user2prog_memonto_msg[user].message_id,
        	text = user2prog_memonto_msg[user].text_markdown +\
                "\n" + messages.TIME_NOT_VALID[lang],
            parse_mode=ParseMode.MARKDOWN,
        	reply_markup = get_cancel_creation_keyboard(lang)
        )
        return SIXTH
    
    date = user2progr_memonto[user].timestamp
    parsed_timestamp = parse_timestamp(date + " " + text)
    # check if timestamp is in the correct format
    if parsed_timestamp != None:
        # check if timestamp is passed
        if timestamp_has_passed(parsed_timestamp):
            user2progr_memonto[user].timestamp = ""
            result, calendar, step = CustomTelegramCalendar(locale=lang).create()
            user2prog_memonto_msg[user] = context.bot.edit_message_text(
            	chat_id = user,
            	message_id = user2prog_memonto_msg[user].message_id,
            	text = user2prog_memonto_msg[user].text_markdown +\
                    "\n" + messages.TIMESTAMP_PASSED[lang],
                parse_mode=ParseMode.MARKDOWN,
            	reply_markup = calendar
            )
            return FIFTH
    
        user2progr_memonto[user].timestamp = \
            parsed_timestamp.strftime(constants.DATETIME_FORMAT)
            
        # delete message with memonto in progress
        context.bot.delete_message(
            chat_id=user,
            message_id=user2prog_memonto_msg[user].message_id
        )
        user2prog_memonto_msg.pop(user, None)
        
        # memonto for user is no more in progress
        update.message.reply_text(messages.MEMONTO_CREATED[lang])
        update.message.reply_text(
            user2progr_memonto[user].to_string(lang),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup = get_menu_keyboard(lang)
        )
        # save complete memonto
        user2progr_memonto[user].save()
        user2progr_memonto.pop(user, None)
        return ConversationHandler.END

def newmemonto_cancel(update, context):
    '''It cancels memonto creation process deleting
    the memonto that was being created.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    query.edit_message_text(messages.MEMONTO_CREATION_CANCELED[lang])
    query.answer()
    query.message.reply_text(
        messages.OLD_MEMONTO_DELETED[lang],
        reply_markup = get_menu_keyboard(lang)
    )
    # delete memonto in progress 
    user2progr_memonto.pop(user, None)
    
    return ConversationHandler.END



'''
LIST MEMONTO
Command to list all the memontos saved by the user which
are still available (not deleted and not expired).
'''
    
def listmemontos_command(update, context):
    '''The function that is invoked with the "list-memonto" command
    and makes the user choose what category of memontos to list.'''
    user = str(update.message.chat_id)
    lang = load_language_choice(user)
    
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    
    memontos = Memonto.get_memontos_list(user)
    if not memontos:
        update.message.reply_text(
            messages.NOMEMONTOS[lang],
            reply_markup = get_menu_keyboard(lang)
        )
        return ConversationHandler.END
    
    else:
        catgs = list({memonto.category[lang] for memonto in memontos if memonto.category[lang]!=""})
        # if memontos are all of just one category, list them all and stop
        if len(catgs) == 1:
            memontos = Memonto.get_memontos_list(user)
            listing_text = messages.LISTING_ALL[lang].format(len(memontos))
            update.message.reply_text(listing_text)
            
            update.message.reply_text(
                Memonto.get_string_of_memontos(lang, memontos),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup = get_menu_keyboard(lang)
            )
            return ConversationHandler.END
        
        # otherwise, answer with keyboard of categories to list
        buttons = list()
        buttons.append(get_cancel_button(lang, 3))
        for cat1, cat2 in zip(catgs[0::2], catgs[1::2]):
            buttons.append([
                InlineKeyboardButton( cat1, callback_data = cat1 ),
                InlineKeyboardButton( cat2, callback_data = cat2 )
            ])
        if len(catgs) % 2 == 1:
            buttons.append([InlineKeyboardButton( catgs[-1], callback_data = catgs[-1] )])
        buttons.append(get_everything_button(lang, 3))
        
        update.message.reply_text(
            messages.CHOOSE_CATEGORY_FOR_LISTING[lang],
            reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        )
    
    return FIRST

def listmemontos_query(update, context):
    '''It reads what button has been selected for the category of memontos to
    list and answer accordingly.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # operation canceled
    if query.data == clickables.CANCEL[lang]:
        query.edit_message_text(query.data)
        query.message.reply_text(
            messages.OPERATION_CANCELED[lang],
            parse_mode=ParseMode.MARKDOWN,
            reply_markup = get_menu_keyboard(lang)
        )
    # listing memontos (everyone if LISTALL selected, just those of selected catg otherwise)
    else:
        memontos = Memonto.get_memontos_list(user)
        if query.data != clickables.LISTALL[lang]:
            memontos = [m for m in memontos if m.category[lang] == query.data]
            listing_text = messages.LISTING_CATEGORY[lang].format(
                len(memontos),
                query.data
            )
        else:
            listing_text = messages.LISTING_ALL[lang].format(len(memontos))
        query.edit_message_text(listing_text)
        
        query.message.reply_text(
            Memonto.get_string_of_memontos(lang, memontos),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup = get_menu_keyboard(lang)
        )
        
    query.answer()
    return ConversationHandler.END


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

    memontos = Memonto.get_memontos_list(user)
    if not memontos:
        update.message.reply_text(messages.NOMEMONTOS[lang])
        return ConversationHandler.END
    
    buttons = list()
    # a button for each deletable memonto
    for memonto in memontos:
        buttons.append([InlineKeyboardButton(
            memonto.to_little_string(lang),
            callback_data = memonto.id
        )])
    # cancel button to cancel the operation
    buttons.append(get_cancel_button(lang, 1))
    # delete-all button to delete all the memontos
    buttons.append(get_everything_button(lang, 1))
    
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    # sending created keyboard
    update.message.reply_text(
        messages.DELETE_MEMONTO[lang],
        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    return FIRST
    
def deletememonto_query(update, context):
    '''It reads what button has been selected for the deletion of a memonto.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    memonto_id = query.data
    
    # if cancel button pressed, cancel operation
    if memonto_id == clickables.CANCEL_CODE:
        text = messages.OPERATION_CANCELED[lang]
        
    # elif delete-all button pressed, delete all memontos
    elif memonto_id == clickables.EVERYTHING_CODE:
        mids = Memonto.get_memontos_ids_list(user)
        # if at least one deletion does not finish correctly, change message text
        b = True
        for mid in mids:
            if not Memonto.delete_memonto(user, mid):
                b = False
        if b:
            text = messages.ALL_MEMONTOS_DELETED[lang]
        else:
            text = messages.SOMETHING_WENT_WRONG[lang]
        
    # delete just the single memonto selected
    elif Memonto.delete_memonto(user, memonto_id):
        text = messages.MEMONTO_DELETED[lang]
    else:
        text = messages.SOMETHING_WENT_WRONG[lang]
        
    query.edit_message_text(text)
    query.answer()
    query.message.reply_text(
        messages.MENU[lang],
        reply_markup = get_menu_keyboard(lang)
    )
    return ConversationHandler.END
    


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
    if len(load_reminders(user)) == constants.LIMIT_REMINDERS:
        update.message.reply_text(messages.REMINDER_LIMIT[lang])
        return ConversationHandler.END 
        
    # removing standard keyboard
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    # asking for time (minutes, hours or days)
    update.message.reply_text(
        messages.REMINDER_TIME_CHOICE[lang],
        reply_markup = get_time_choice_keyboard(lang)
    )
    
    return FIRST

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
    return SECOND
    
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
            return SECOND
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
        return ConversationHandler.END
    
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
    return FIRST
    
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
    return ConversationHandler.END



'''
CHANGE LANGUAGE
'''
    
def changelanguage_command(update, context):
    '''The function that is invoked with the "change-language" command.'''
    update.message.reply_text(
        messages.LANGUAGE_CHOICE,
        reply_markup = get_language_choice_keyboard()
    )
    return FIRST

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
    return ConversationHandler.END



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
    return FIRST
    
def help_query(update, context):
    '''It reads what button has been selected for adding text to help message.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # number of inline buttons that were contained in the inline keyboard
    num_buttons_before = len(query.message.reply_markup.inline_keyboard)
    # if it was 1, now all buttons have been pressed and keyboard is going to be empty
    if num_buttons_before == 1:
        keyboard = get_help_keyboard(lang, False, False)
        all_pressed = True
        ret = ConversationHandler.END
    else:
        all_pressed = False
        ret = FIRST
    
    # first, the answer contains the old message
    answer = query.message.text
    
    # plus How to manage memonto, if that was clicked
    if query.data == clickables.HELP1_CODE:
        answer += "\n\n" + messages.HELP1[lang]
        # if the inline keyboard contained two buttons, answer with the remaining one
        if not all_pressed:
            keyboard = get_help_keyboard(lang, False, True)
    # or plus How to manage reminders, if that was clicked
    elif query.data == clickables.HELP2_CODE:
        answer += "\n\n" + messages.HELP2[lang]
        # if the inline keyboard contained two buttons, answer with the remaining one
        if not all_pressed:
            keyboard = get_help_keyboard(lang, True, False)
        
    query.edit_message_text(answer, reply_markup = keyboard)
    return ret



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
        messages.INFO[lang].format(VERSION, LASTUPDATE, constants.REPOSITORY_URL),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup = get_changelogs_button(lang)
    )
    return FIRST
    
def info_query(update, context):
    '''The function that is invoked with the "changelogs" command.'''
    query = update.callback_query
    user = str(query.message.chat_id)
    lang = load_language_choice(user)
    
    # send changelogs of this version
    changes = get_changes_of(VERSION, lang)
    query.edit_message_text(changes)
    query.answer()
    return ConversationHandler.END





'''
BOT
'''
updater = Updater(TOKEN, use_context=True)
# start job_each_minute for checking memontos
job_queue = updater.job_queue
job_minute = job_queue.run_repeating(job_each_minute, interval=60, first=0)

# HANDLERs
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start_command))

for lang in [EN, IT]:
    # ConversationHandler for memonto creation
    categ_pattern = "^(" + ")$|^(".join(constants.CATEGORIES[lang]) + ")$"
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
            FIFTH:  [CallbackQueryHandler(expiring_date_query_memonto)],
            SIXTH:  [MessageHandler(Filters.text & NOTBACK, expiring_time_memonto)]
        },
    
        fallbacks=[CallbackQueryHandler(
            newmemonto_cancel,
            pattern="^" + clickables.CANCEL_CREATION[lang] + "$"
        )]
    )
    dp.add_handler(memonto_creation_handler)
    
    # ConversationHandler for list memontos
    categ_pattern = "^(" + ")|(".join(constants.CATEGORIES[lang]) + ")|(" +\
        clickables.CANCEL[lang] + ")|(" +\
        clickables.LISTALL[lang] + ")$"
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.LISTMEMONTOS[lang]),
            listmemontos_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(
                listmemontos_query,
                pattern=categ_pattern
            )]
        },
    
        fallbacks= list()
    ))
    
    # ConversationHandler for delete memonto
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.DELETEMEMONTO[lang]),
            deletememonto_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(
                deletememonto_query,
                pattern="^-?([0-9]*)"
            )]
        },
    
        fallbacks= list()
    ))
    
    # setting handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.SETTINGS[lang]),
        settings_command
    ))
    
    # ConversationHandler for reminder addition
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.ADDREMINDER[lang]),
            addreminder_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(addreminder_query, pattern="^(d|h|m)$")],
            SECOND: [MessageHandler(Filters.text, addreminder_number)]
        },
        
        fallbacks=[CallbackQueryHandler(
            addreminder_cancel,
            pattern="^" + clickables.CANCEL_ADDITION[lang] + "$"
        )]
    ))
    
    # ConversationHandler for remove reminder
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.REMOVEREMINDER[lang]),
            removereminder_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(
                removeaddreminder_query,
                pattern="(.*)(d|h|m)$"
            )]
        },
    
        fallbacks= list()
    ))
    
    # ConversationHandler for change language
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.CHANGELANGUAGE[lang]),
            changelanguage_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(changelanguage_query, pattern="^(en|it)$")]
        },
    
        fallbacks= list()
    ))

    # back handler
    dp.add_handler(MessageHandler(
        Filters.regex(clickables.BACK[lang]),
        home_command
    ))
    
    # ConversationHandler for help
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.HELP[lang]),
            help_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(help_query, pattern="^help(1|2)$")]
        },
    
        fallbacks= list()
    ))
    
    # ConversationHandler for info
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(clickables.INFO[lang]),
            info_command
        )],
    
        states={
            FIRST: [CallbackQueryHandler(info_query)]
        },
    
        fallbacks= list()
    ))


# starting the Bot
updater.start_polling()
updater.idle()