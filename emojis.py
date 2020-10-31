"EMOJIS"

from emoji import emojize

def get_emoji(name):
    return emojize(name, use_aliases=True)

PLUSSIGN    = get_emoji(":heavy_plus_sign:")
OPENFOLDER  = get_emoji(":open_file_folder:")
TRASH       = get_emoji(":wastebasket:")
GEAR        = get_emoji(":gear:")
BELL        = get_emoji(":bell:")
NOBELL      = get_emoji(":no_bell:")
GLOBE       = get_emoji(":globe_with_meridians:")
QUESTIONMARK = get_emoji(":question:")
INFO        = get_emoji(":information_source:")
BACK        = get_emoji(":back:")
CROSS       = get_emoji(":x:")