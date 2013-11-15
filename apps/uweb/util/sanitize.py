import re
import unicodedata

def sanitize_filename(in_str):
    '''
    Cleans-up a string so that it can be used as a filename.
    Based on Django's "slugify"
    '''
    in_str = unicodedata.normalize('NFKD', in_str).encode('ascii', 'ignore')
    in_str = unicode(re.sub('[^\w\s-]', '', in_str).strip().lower())
    # replace whitespace with underscores
    in_str = re.sub('[\s]+', '_', in_str)
    return in_str
