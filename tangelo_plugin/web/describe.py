
import tangelo
from apps.util import applications as _application


@tangelo.restful
def get(name=None):
    if name is None:
        return {
            k: v['description'] for k, v in _application.iteritems()
        }
    elif kw['name'] in _application:
        return {
            kw['name']: kw['name']['description']
        }
    else:
        tangelo.http_status(400, "Unknown application")
        return None
