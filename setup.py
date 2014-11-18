from setuptools import setup, find_packages
from cdatweb import __version__

setup(
    name='cdatweb',
    version=__version__,

    url='https://github.com/UV-CDAT/cdatweb',
    author='ACME Team',
    author_email='email@nobody.com',

    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/manage.py'],

    install_requires=(
        'django>=1.7',
    )
)
