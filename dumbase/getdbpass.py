# -*- coding: utf-8 -*-

import sys
import getpass
import gettext
import logging
import i18n

_ = i18n.language.ugettext

prompt = _('Enter password for <{0}> ({1}): ')

def getdbpass(dsn, tries=3, empty=False, tail=_('CTRL-D to abort')):
    for i in range(tries):
        try:
            password = getpass.getpass(prompt.format(dsn, tail))
        except EOFError:
            return None
        if not empty and password == '':
            logging.error(_('You must enter non-empty password!'))
        else:
            return password
