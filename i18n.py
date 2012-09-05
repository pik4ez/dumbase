# -*- coding: utf-8 -*-

import os
import sys
import locale
import gettext

DOMAIN = 'dumbase'
LOCALE_DIR = os.path.join(os.getcwd(), 'locale')
DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES += ['en_US']

lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

languages += DEFAULT_LANGUAGES

gettext.install(True, localedir = None, unicode = 1)
gettext.find(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
gettext.bind_textdomain_codeset(DOMAIN, 'UTF-8')
language = gettext.translation(DOMAIN, LOCALE_DIR, languages = languages, fallback = True)

ug = language.ugettext
language.ugettext = lambda t: ug(t).encode('utf-8')

