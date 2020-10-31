import os
import json
import pickle

from languages import IT, EN
from constants import USERS_PATH, MEMONTOS_PATH, JSON, LIMIT_MEMONTOS, ID_FIELD, CATEG_FIELD, BRAND_FIELD, DESCR_FIELD, CODE_FIELD, TIMESTAMP_FIELD, FIELD_TEXT

class Memonto:

    def __init__(self, user):
        self.user = user
        self.id = self.__generate_memonto_id() # id is generated
        self.category = {EN : "", IT : ""}
        self.brand = ""
        self.description = ""
        self.code = ""
        self.timestamp = ""
        
    
    def __generate_memonto_id(self):
        '''Dump and load of the MEMONTO_ID_COUNT variable. The value of this variable is used to assign an id to each memonto.'''
        COUNTER_FILE_PATH = 'counter.pckl'

        with open(COUNTER_FILE_PATH, 'rb') as f:
            counter = pickle.load(f)
            counter += 1
        with open(COUNTER_FILE_PATH, 'wb') as f:
            pickle.dump(counter, f)
            
        return counter
    
    def save(self):
        '''Saves the object as json into the user folder.'''
        file_path = get_memonto_path_of(self.user, self.id)
        with open(file_path, 'w') as f:
            json.dump(self.__dict__, f)
    
    def delete(self):
        '''Delete the file corresponding to the object.'''
        return delete_memonto(self.user, self.id)
            
    def to_string(self, lang):
        '''It returns a string correctly formatted with all the fields of memonto.'''
        category = self.category[lang]
        brand = self.brand
        description = self.description
        code = self.code
        timestamp = self.timestamp

        if brand == "":
            string = FIELD_TEXT[BRAND_FIELD][lang]
            brand = "\\_"*(30 - len(string))
        if description == "":
            string = FIELD_TEXT[DESCR_FIELD][lang]
            description = "\\_"*(30 - len(string))
        if code == "":
            string = FIELD_TEXT[CODE_FIELD][lang]
            code = "\\_"*(30 - len(string))
        else:
            code = f"```\n{self.code}```"
        if timestamp == "":
            string = FIELD_TEXT[TIMESTAMP_FIELD][lang]
            timestamp = "\\_"*(30 - len(string))
        return \
            f"*{FIELD_TEXT[CATEG_FIELD][lang]}*: {category}\n"          +\
            f"*{FIELD_TEXT[BRAND_FIELD][lang]}*: {brand}\n"             +\
            f"*{FIELD_TEXT[DESCR_FIELD][lang]}*: {description}\n"       +\
            f"*{FIELD_TEXT[CODE_FIELD][lang]}*: {code}\n"               +\
            f"*{FIELD_TEXT[TIMESTAMP_FIELD][lang]}*: {timestamp}"
    
    def to_little_string(self, lang):
        '''It returns a compacted string with brand and
        description to summarize the memonto.'''
        if len(self.brand) > 10:
            brand = f"[{self.brand[:7]}...]"
        else:
            brand = f"[{self.brand}]"
        return f"{brand} {self.description}"

def create_memonto(user):
    '''It creates and dumps an empty memonto with an incremental id in the user folder.'''
    # check if limit of memonto reached
    memontos_folder = get_memontos_path_of(user)
    n = len(os.listdir(memontos_folder)) + 1
    if n > LIMIT_MEMONTOS:
        return None
    
    return Memonto(user)

def load_memonto(json_data, user):
    '''Create a new memonto but with all the data taken from json_data.'''
    memonto = Memonto(user)
    memonto.id          = json_data[ID_FIELD]
    memonto.category    = json_data[CATEG_FIELD]
    memonto.brand       = json_data[BRAND_FIELD]
    memonto.description = json_data[DESCR_FIELD]
    memonto.code        = json_data[CODE_FIELD]
    memonto.timestamp   = json_data[TIMESTAMP_FIELD]
    
    return memonto

def get_memontos_path_of(user):
    '''Returns the path in which there are all the memontos (json files) of user.'''
    return os.path.join(USERS_PATH, user, MEMONTOS_PATH)
    
def get_memonto_path_of(user, id_memonto):
    '''Returns the path of the memonto file for the user passed with the id passed.'''
    return os.path.join(get_memontos_path_of(user), str(id_memonto) + JSON)

def delete_memonto(user, id_memonto):
    '''It deletes the memonto with memonto_id as id from the memontos of user.'''
    file_path = get_memonto_path_of(user, id_memonto)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False

def get_memontos_list(user):
    '''It returns a list of all the memontos created by the user.'''
    memontos = list()
    
    memontos_path = get_memontos_path_of(user)
    for file in os.listdir(memontos_path):
        file_path = os.path.join(memontos_path, file)
        with open(file_path, 'r') as f:
            memonto = load_memonto(json.load(f), user)
            memonto.user = user
        memontos.append(memonto)
    
    return memontos

def get_memontos_ids_list(user):
    '''It returns a list of ids, where each id corresponds to a memonto of user.'''
    paths = list()
    
    for file in os.listdir(get_memontos_path_of(user)):
        paths.append(file.split(JSON)[0])
        
    return paths

def get_string_of_memontos(lang, memontos):
    '''It returns the concatenation of the to_string of each memonto in memontos.'''
    return "\n\n".join([m.to_string(lang) for m in memontos])