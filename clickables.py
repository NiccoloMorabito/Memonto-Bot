'''KEYBOARDS and BUTTONS'''

import emojis
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from languages import IT, EN, ITALIAN, ENGLISH

NEWMEMONTO = {
    EN : emojis.PLUSSIGN + " New memonto",
    IT : emojis.PLUSSIGN + " Crea memonto"
}
LISTMEMONTOS = {
    EN : emojis.OPENFOLDER + " List memontos",
    IT : emojis.OPENFOLDER + " Elenco memonto"
}
DELETEMEMONTO = {
    EN : emojis.TRASH + " Delete memonto",
    IT : emojis.TRASH + " Elimina memonto"
}
SETTINGS = {
    EN : emojis.GEAR + " Settings",
    IT : emojis.GEAR + " Impostazioni"
}
ADDREMINDER = {
    EN : emojis.BELL + " Add reminder",
    IT : emojis.BELL + " Aggiungi promemoria"
}
CANCEL_ADDITION = {
    EN : emojis.BACK + " Cancel addition",
    IT : emojis.BACK + " Annulla aggiunta"
}
REMOVEREMINDER = {
    EN : emojis.NOBELL + " Remove reminder",
    IT : emojis.NOBELL + " Rimuovi promemoria"
}
CHANGELANGUAGE = {
    EN : emojis.GLOBE + " Change language",
    IT : emojis.GLOBE + " Cambia lingua"
}
BACK = {
    EN : emojis.BACK + " Back",
    IT : emojis.BACK + " Indietro"
}
CANCEL_CREATION = {
    EN : emojis.BACK + " Cancel creation",
    IT : emojis.BACK + " Annulla creazione"
}

HELP = {
    EN : emojis.QUESTIONMARK + " Help",
    IT : emojis.QUESTIONMARK + " Aiuto"
}
HELP_ADD1 = {
    EN : "How to manage memontos",
    IT : "Come gestire i memonto"
}

HELP_ADD2 = {
    EN : "How to manage reminders",
    IT : "Come gestire i promemoria"
}

INFO = {
    EN : emojis.INFO + " Info",
    IT : emojis.INFO + " Info"
}
CHANGELOGS = {
    EN : "Changelogs",
    IT : "Novità"
}
CANCEL = {
    EN : emojis.CROSS + " Cancel",
    IT : emojis.CROSS + " Annulla"
}
DELETEALL = {
    EN : emojis.TRASH + " Delete all " + emojis.TRASH,
    IT : emojis.TRASH + " Cancella tutti " + emojis.TRASH
}
REMOVEALL = {
    EN : emojis.NOBELL + " Remove all " + emojis.NOBELL,
    IT : emojis.NOBELL + " Rimuovi tutti " + emojis.NOBELL
}

MINUTES = {
    EN : "minutes",
    IT : "minuti (m)"
}
HOURS = {
    EN : "hours",
    IT : "ore (h)"
}
DAYS = {
    EN : "days",
    IT : "giorni (d)"
}

def get_type_time(letter, lang):
    if letter == 'm':
        return MINUTES[lang]
    elif letter == 'h':
        return HOURS[lang]
    else:
        return DAYS[lang]


def get_menu_keyboard(lang):
    return ReplyKeyboardMarkup([
        [KeyboardButton(NEWMEMONTO[lang]), KeyboardButton(LISTMEMONTOS[lang]), KeyboardButton(DELETEMEMONTO[lang])],
        [KeyboardButton(SETTINGS[lang]), KeyboardButton(HELP[lang]), KeyboardButton(INFO[lang])],
    ])

def get_cancel_creation_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CANCEL_CREATION[lang], callback_data=CANCEL_CREATION[lang])],
    ])

def get_cancel_addition_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CANCEL_ADDITION[lang], callback_data=CANCEL_ADDITION[lang])],
    ])

def get_settings_keyboard(lang):
    return ReplyKeyboardMarkup([
        [KeyboardButton(ADDREMINDER[lang]), KeyboardButton(REMOVEREMINDER[lang])],
        [KeyboardButton(CHANGELANGUAGE[lang]), KeyboardButton(BACK[lang])],
    ])

def get_time_choice_keyboard(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = MINUTES[lang], callback_data='m'),
            InlineKeyboardButton(text = HOURS[lang], callback_data='h'),
            InlineKeyboardButton(text = DAYS[lang], callback_data='d')],
        [InlineKeyboardButton(text = CANCEL_ADDITION[lang], callback_data=CANCEL_ADDITION[lang])]
    ])

def get_changelogs_button(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CHANGELOGS[lang], callback_data=CHANGELOGS[lang])],
    ])

def get_language_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = ENGLISH, callback_data=EN),
         InlineKeyboardButton(text = ITALIAN, callback_data=IT)]
    ])



HELP1_CODE = "help1"
HELP2_CODE = "help2"
def get_help_keyboard(lang, first, second):    
    buttons = list()
    if first:
        buttons.append([InlineKeyboardButton(HELP_ADD1[lang], callback_data=HELP1_CODE)])
    if second:
        buttons.append([InlineKeyboardButton(HELP_ADD2[lang], callback_data=HELP2_CODE)])
    return InlineKeyboardMarkup(buttons)


CANCEL_CODE = "-1"
def get_cancel_button(lang, operation):
    # if operation is DELETE MEMONTO
    if operation == 1:
        callback = "MEMONTO #" + CANCEL_CODE
    # else if operation is REMOVE REMINDER
    elif operation == 2:
        callback = CANCEL_CODE + "d"
    return [InlineKeyboardButton(CANCEL[lang], callback_data=callback)]

EVERYTHING_CODE = "-2"
def get_everything_button(lang, operation):
    # if operation is DELETE MEMONTO
    if operation == 1:
        return [InlineKeyboardButton(DELETEALL[lang], callback_data="MEMONTO #" + EVERYTHING_CODE)]
    # else if operation is REMOVE REMINDER
    elif operation == 2:
       return [InlineKeyboardButton(REMOVEALL[lang], callback_data=EVERYTHING_CODE + "d")]
       