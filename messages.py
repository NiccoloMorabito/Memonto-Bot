'''MESSAGES'''

import clickables
from languages import IT, EN
import emojis

LANGUAGE_CHOICE = "Choose your language / Scegli la tua lingua"

LANGUAGE_SELECTED = {
    EN : "English selected.",
    IT : "Lingua italiana selezionata."
}

WELCOME = {
    EN : "Welcome to Memonto!\n\n"
            "Memonto Bot helps you to remember your discount codes and offers. Create a new memonto specifying the expiration date and you will be able to add custom reminders (from Settings) to be notified when the offers are about to end through a Telegram message!\n\n"
            "Select an option from the menu to get started or click the\n"
            "[{}] button if you need more information on how the bot works:"           
                .format(clickables.HELP[EN]),
    IT : "Benvenut* in Memonto!\n\n"
            "Memonto Bot ti aiuta a ricordare i tuoi codici sconto e offerte. Crea un nuovo memonto specificando la data di scadenza e dalle impostazioni potrai aggiungere dei promemoria personalizzati per essere notificato quando le tue offerte stanno per finire con un messaggio Telegram!\n\n"
            "Seleziona un'opzione dal menu per iniziare o clicca il bottone\n"
            "[{}] se hai bisogno di maggiori informazioni sul funzionamento del bot:"  
                .format(clickables.HELP[IT])
}

MENU = {
    EN : "Select an option from the menu:",
    IT : "Seleziona un'opzione dal menu:"
}

LIMIT_REACHED = {
    EN : "You have reached the limit of savables memontos. Use [{}] to free up space and retry."
            .format(clickables.DELETEMEMONTO[EN]),
    IT : "Hai raggiunto il limite di memonto salvabili. Usa [{}] per liberare spazio e riprova."
            .format(clickables.DELETEMEMONTO[IT])
}

CREATION_STARTED = {
    EN : "CREATION OF MEMONTO",
    IT : "CREAZIONE DEL MEMONTO"    
}

CHOOSE_CATEGORY = {
    EN : "Choose a category for your memonto:",
    IT : "Scegli una categoria per il tuo memonto:"    
}

CATEGORY_SELECTED = {
    EN : "Category {} selected.",
    IT : "Categoria {} selezionata."    
}

TOO_MANY_CHARACTERS = {
    EN : emojis.CROSS + " The string you inserted is too long. Write less than {} characters. " + emojis.CROSS,
    IT : emojis.CROSS + " Il testo che hai inserito è troppo lungo. Scrivi meno di {} caratteri. " + emojis.CROSS   
}

INSERT_BRAND = {
    EN : "Insert brand name",
    IT : "Inserisci il nome del brand"
}

INSERT_DESCRIPTION = {
    EN : "Insert a brief description of the offer to easily identify it",
    IT : "Inserisci una breve descrizione dell'offerta per identificarla facilmente"
}

INSERT_CODE = {
    EN : "Insert discount code",
    IT : "Inserisci il codice sconto"
}

SELECT_DATE = {
    EN : "Select the expiring date of the offer from the inline calendar below.",
    IT : "Seleziona la data di scadenza dell'offerta dal calendario inline di seguito."
}

DATE_PASSED = {
    EN : emojis.CROSS + " The date you selected has passed. " + emojis.CROSS,
    IT : emojis.CROSS + " La data che hai scelto è passata. " + emojis.CROSS   
}

DATE_SELECTED = {
    EN : "You selected {}",
    IT : "Hai selezionato la data {}"   
}

INSERT_TIME = {
    EN : "Insert expiring time of the offer in the following format HH:MM\n"
            "If no time is specified, insert 23:59",
    IT : "Inserisci l'ora di scadenza dell'offerta nel seguente formato HH:MM\n"
            "Se nessuna ora è specificata, inserisci 23:59"
}

TIME_NOT_VALID = {
    EN : emojis.CROSS + " Time is not valid. Insert time in the following format HH:MM " + emojis.CROSS,
    IT : emojis.CROSS + " Orario non valido. Inserisci l'orario nel seguente formato HH:MM " + emojis.CROSS
}

TIMESTAMP_PASSED = {
    EN : emojis.CROSS + " The date and time you inserted have passed. Select a valid date and time. " + emojis.CROSS,
    IT : emojis.CROSS + " La data e ora che hai inserito sono passati. Seleziona una data e ora validi. " + emojis.CROSS   
}

MEMONTO_CREATED = {
    EN : "Your memonto has been created! Remember to manage your reminders in [{}] in order to be notified when this memonto is expiring."
            .format(clickables.SETTINGS[EN]),
    IT : "Il tuo memonto è stato creato! Ricorda di gestire i tuoi promemoria in [{}] per essere notificato quando questo memonto sta scadendo."
            .format(clickables.SETTINGS[IT])
}

CHOOSE_CATEGORY_FOR_LISTING = {
    EN : "Choose the category you want to list or list all.",
    IT : "Scegli la categoria che vuoi elencare o elenca tutti."
}

LISTING_ALL = {
    EN : "Listing all {} memontos",
    IT : "Elenco di tutti i {} memonto"
}
LISTING_CATEGORY = {
    EN : "Listing {} memontos of category {}",
    IT : "Elenco di {} memonto della categoria {}"
}

DELETE_MEMONTO = {
    EN : "Select the memonto you want to delete",
    IT : "Seleziona il memonto che vuoi eliminare"
}

MEMONTO_CREATION_CANCELED = {
    EN : "Memonto creation canceled.",
    IT : "Creazione del memonto annullata."
}

OLD_MEMONTO_DELETED = {
    EN : "The memonto you were creating has been deleted. " + MENU[EN],
    IT : "Il memonto che stavi creando è stato cancellato. " + MENU[IT]
}

MEMONTO_DELETED = {
    EN : "The memonto has been deleted.",
    IT : "Il memonto è stato cancellato."
}

ALL_MEMONTOS_DELETED = {
    EN : "All your memontos have been deleted.",
    IT : "Tutti i tuoi memonto sono stati cancellati."
}

EXPIRING_MEMONTO = {
    EN : emojis.BELL + " NOTIFICATION OF REMINDER " + emojis.BELL +\
            "\nThe following memontos are expiring in {}:\n\n{}",
    IT : emojis.BELL + " NOTIFICA DI PROMEMORIA" + emojis.BELL +\
            "\nI seguenti memonto scadranno tra {}:\n\n{}"
}

MEMONTO_EXPIRED = {
    EN : emojis.TRASH + " NOTIFICATION OF EXPIRATION " + emojis.TRASH +\
            "\nThe following memontos have just expired and have been deleted:\n\n{}",
    IT : emojis.TRASH + " NOTIFICA DI SCADENZA " + emojis.TRASH +\
            "\nI seguenti memonto sono appena scaduti e sono stati cancellati:\n\n{}"
}

NOMEMONTOS = {
    EN : "You have no active memontos. Click on [{}] to create a new memonto!" .format(clickables.NEWMEMONTO[EN]),
    IT : "Non hai memonto attivi. Clicca su [{}] per creare un nuovo memonto!" .format(clickables.NEWMEMONTO[IT])
}

REMINDER_TIME_CHOICE = {
    EN : "Select one of the option below to add a new reminder for your memontos:",
    IT : "Seleziona una delle opzioni di seguito per aggiungere un nuovo promemoria ai tuoi memonto:"
}

REMINDER_ADDITION_CANCELED = {
    EN : "Reminder addition canceled.",
    IT : "Aggiunta del promemoria annullata."
}

OLD_REMINDER_DELETED = {
    EN : "The reminder you were adding has not been saved.",
    IT : "Il promemoria che stavi aggiungendo non è stato salvato."
}

INSERT_REMINDER_NUMBER = {
    EN : "Insert the number of {}",
    IT : "Inserisci il numero di {}"
}

REMINDER_NUMBER_NOT_VALID = {
    EN : "You have to insert a positive integer.",
    IT : "Devi inserire un numero intero positivo."
}

REMINDER_CREATED = {
    EN : "New reminder of {} added!",
    IT : "Nuovo promemoria di {} aggiunto!"
}

REMINDER_LIMIT = {
    EN : "You have reached the limit of savable reminders. You cannot add a new reminder",
    IT : "Hai raggiunto il limite di promemoria salvabili. Non puoi aggiungere un nuovo promemoria."
}

REMOVE_REMINDER = {
    EN : "Select the reminder you want to remove:",
    IT : "Seleziona il promemoria che vuoi rimuovere:"
}

REMINDER_REMOVED = {
    EN : "The {} reminder has been removed.",
    IT : "Il promemoria di {} è stato cancellato."
}

ALL_REMINDERS_REMOVED = {
    EN : "All your reminders have been removed.",
    IT : "Tutti i tuoi promemoria sono stati cancellati."
}

NOREMINDERS = {
    EN : "You have no reminders. Click on [{}] to add a reminder."                              .format(clickables.ADDREMINDER[EN]),
    IT : "Non hai impostato alcun promemoria. Clicca su [{}] per aggiungere un promemoria."     .format(clickables.ADDREMINDER[IT])
}

SOMETHING_WENT_WRONG = {
    EN : "Ops... something went wrong. Try another time.",
    IT : "Ops... qualcosa è andato storto. Riprova."
}

OPERATION_CANCELED = {
    EN : "Operation canceled.",
    IT : "Operazione annullata."
}

INFO = {
    EN : "MEMONTO BOT\n\n"
            "Version: {}\n"
            "Last update: {}\n"
            "Developed by @NiccoloMorabito. Source code available [here]({}).",
    IT : "MEMONTO BOT\n\n"
            "Versione: {}\n"
            "Ultimo aggiornamento: {}\n\n"
            "Sviluppato da @NiccoloMorabito. Il codice sorgente è disponibile [qui]({})."
}

HELP = {
    EN :  "Remember: you can change your language every time you want. Just go on [{}] and click on [{}] button.\n\n"
            "HOW THE BOT WORKS\n"
            "A memonto is an offer or a discount that you want to remember. It can be a JustEat code to order your kebab for €3 less or the word you need to get a 5% discount in printing all the photos of kittens on Cheerz: the important thing is that it is an unmissable offer! To avoid forgetting it, in fact, you can set reminders by selecting how long before you want to be notified.\n\n"
            "Note: the added reminders will be valid for all the created memontos and will remain saved regardless of them.\n"
            "Please, feel free to contact @NiccoloMorabito in case of need."
                .format(clickables.SETTINGS[EN], clickables.CHANGELANGUAGE[EN]),
            
    IT : "Ricorda: puoi cambiare la lingua quando vuoi. Semplicemente vai su [{}] e clicca il bottone [{}].\n\n"
            "COME FUNZIONA IL BOT\n"
            "Un memonto è un'offerta o uno sconto che vuoi ricordare. Può essere un codice JustEat per ordinare il tuo kebab a €3 in meno o la parola necessaria a ottenere il 5% di sconto sulla stampa di tutte le foto di gattini su Cheerz: l'importante è che sia un'offerta imperdibile! Per evitare di scordarla infatti, potrai impostare dei promemoria selezionando quanto tempo prima vuoi essere notificato.\n\n"
            "Nota: i promemoria aggiunti saranno validi per tutti i memonto eventualmente creati e rimarranno salvati a prescindere da loro.\n"
            "Contatta @NiccoloMorabito in caso di necessità."
                .format(clickables.SETTINGS[IT], clickables.CHANGELANGUAGE[IT])
}

HELP1 = {
    EN : "HOW TO MANAGE MEMONTOS\n"
            "Click on [{}] button to create a memonto. You have to specify a few fields, one at a time. Read the instructions in realtime, the bot is going to answer you. In order to see your saved memontos, just click on [{}] button. You can delete a memonto by clicking on [{}] button and selecting the one you want to delete."
                .format(clickables.NEWMEMONTO[EN], clickables.LISTMEMONTOS[EN], clickables.DELETEMEMONTO[EN]),
    IT : "COME GESTIRE I MEMONTO\n"
            "Clicca sul bottone [{}] per creare un memonto. Dovrai specificare alcuni campi, uno alla volta. Leggi le istruzioni in tempo reale, il bot ti risponderà. Per vedere i memonto che hai salvato, clicca sul bottone [{}]. Puoi cancellare un memonto cliccando su [{}] e selezionando quello che vuoi eliminare."
                .format(clickables.NEWMEMONTO[IT], clickables.LISTMEMONTOS[IT], clickables.DELETEMEMONTO[IT])
}

HELP2 = {
    EN : "HOW TO MANAGE REMINDERS\n"
            "You should add at least a reminder if you want to be notified by the bot when your memonto is expiring. Go to [{}] and then click on [{}] to add a reminder. First of all, select if you want a reminder of minutes, hours or days; then, insert the corresponding number when requested. The bot is going to send you a message when the time left to expiration is the one you entered. You can add maximum of 10 reminders, but don't worry: you can delete a reminder clicking on the [{}] button in [{}] and selecting the one you want to remove."
                .format(clickables.SETTINGS[EN], clickables.ADDREMINDER[EN], clickables.REMOVEREMINDER[EN], clickables.SETTINGS[EN]),
    IT : "COME GESTIRE I PROMEMORIA\n"
            "Dovresti aggiungere almeno un promemoria se vuoi essere notificato dal bot quando il tuo memonto sta per scadere. Vai su [{}] e poi clicca su [{}] per aggiungere un promemoria. Prima di tutto, seleziona se vuoi un promemoria di minuti, di ore o di giorni; poi, inserisci il numero corrispondente quando richiesto. Il bot ti manderà un messaggio quando il tempo mancante alla scadenza è quello che hai inserito. Puoi aggiungere fino a 10 promemoria, ma non preoccuparti: puoi rimuovere un promemoria cliccando sul bottone [{}] nelle [{}] e selezionando quello che vuoi rimuovere."
                .format(clickables.SETTINGS[IT], clickables.ADDREMINDER[IT], clickables.REMOVEREMINDER[IT], clickables.SETTINGS[IT])
            
}

CHANGELOGS_HEADER = {
    EN : "CHANGELOGS IN VERSION {}:\n\n",
    IT : "NOVITÀ NELLA VERSIONE {} (disponibili solo in inglese):\n\n"
}
NO_CHANGELOGS_MESSAGE = {
    EN : "The nice developer forgot to write changes in version {} :( please contact @NiccoloMorabito to insult him!",
    IT : "Il simpatico sviluppatore si è dimenticato di scrivere le novità della versione {} :( contatta @NiccoloMorabito per insultarlo!"
}