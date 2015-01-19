'''
Handles visualization server launcher endpoints.
'''

import json
import requests

from django.conf import settings


def new_instance(app='default'):
    '''
    Create a new vtkweb instance.  Returns an object
    containing status/websocket address to the instance.
    '''
    data = {
        'application': app
    }
    resp = requests.post(
        settings.VISUALIZATION_LAUNCHER,
        data=json.dumps(data)
    )
    try:
        return resp.json()
    except Exception:
        return {}


def stop_instance(id):
    requests.delete(
        settings.VISUALIZATION_LAUNCHER + '/' + id
    )


def status(id):
    resp = requests.get(
        settings.VISUALIZATION_LAUNCHER + '/' + id
    )
    try:
        return resp.json()
    except Exception:
        return None
