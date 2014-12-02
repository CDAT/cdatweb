
import tangelo
from app import query_key


@tangelo.restful
def get(key=None):
    return query_key(key)
