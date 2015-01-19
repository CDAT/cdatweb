from cdatweb.settings.production import *

import os

TMP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'tmp'))

DEBUG = TEMPLATE_DEBUG = True
SECRET = '42'
print TMP_PATH
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TMP_PATH, 'db.sqlite3'),
    }
}

INTERNAL_IPS = ('127.0.0.1',)

if 'debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += ('debug_toolbar',)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

VISUALIZATION_LAUNCHER = 'http://127.0.0.1:7000/vtk'
DATA_DIRECTORY = os.path.join(TMP_PATH, 'data')

try:
    os.makedirs(DATA_DIRECTORY)
except Exception:
    pass
