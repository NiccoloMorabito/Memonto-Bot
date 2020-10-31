'''CONSTANTS'''

from languages import IT, EN

# repository of source code
REPOSITORY_URL = "https://github.com/NiccoloMorabito/Memonto-Bot"

# paths
USERS_PATH = "users"
MEMONTOS_PATH = "memontos"
JSON = ".json"
REMINDERS_FILE_PATH = 'reminders.pckl'
LANGUAGE_FILE_PATH = 'language.pckl'

# limits
LIMIT_MEMONTOS = 30
LIMIT_REMINDERS = 10
LIMIT_CHARACTERS_LITTLE = 20
LIMIT_CHARACTERS_MEDIUM = 50
LIMIT_CHARACTERS_BIG = 150

# memonto fields
ID_FIELD = "id"
CATEG_FIELD = "category"
BRAND_FIELD = "brand"
DESCR_FIELD = "description"
CODE_FIELD  = "code"
TIMESTAMP_FIELD = "timestamp"
# memonto fields' texts
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
# memonto categories
CATEGORIES = {
    EN : ["Food", "Clothes", "Travel", "eCommerce", "Games", "Beauty", "Experiences", "Other"],
    IT : ["Cibo", "Vestiti", "Viaggi", "eCommerce", "Giochi", "Cura personale", "Esperienze", "Altro"]
}

# constants for utils
CHANGELOG_PATH = 'CHANGELOG.md'
DATETIME_FORMAT = '%d/%m/%Y %H:%M'
DATE_FORMAT     = '%d/%m/%Y'
MINUTE  = 'm'
HOUR    = 'h'
DAY     = 'd'