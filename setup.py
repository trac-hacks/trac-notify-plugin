from setuptools import setup

PACKAGE = 'TracNotify'
VERSION = '0.1'

setup(name=PACKAGE,
      version=VERSION,
      packages=['notify'],
      entry_points={'trac.plugins': '%s = notify' % PACKAGE},
      package_data={'notify': ['templates/*.cs', 'htdocs/images/*.jpg']},
)
