from cdatweb.settings.production import *

import os

TMP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'tmp'))
ALLOWED_HOSTS = ['*']
DEBUG = TEMPLATE_DEBUG = True
SECRET = '42'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TMP_PATH, 'db.sqlite3'),
    }
}

INTERNAL_IPS = ('127.0.0.1',)

# if 'debug_toolbar' not in INSTALLED_APPS:
#     INSTALLED_APPS += ('debug_toolbar',)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# VISUALIZATION_LAUNCHER = 'http://aims1.llnl.gov/vtk'
VISUALIZATION_LAUNCHER = 'http://localhost:7000/vtk'
DATA_DIRECTORY = os.path.join(TMP_PATH, 'data')

SECRET_KEY = '62u8^z_p#^z0!!0xx-2e)vd_6b^m@49ecx8qs##e-w7um)&n_$'

try:
    os.makedirs(DATA_DIRECTORY)
except Exception:
    pass
