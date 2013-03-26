# -*- coding: utf-8 -*-

import sys
import getpass
import gettext
import logging
import i18n

_ = i18n.language.ugettext

prompt = _('Enter username for <{0}> ({1}): ')

def getdbuser(dsn, tries=3, empty=False, tail=_('CTRL-D to abort')):
    for i in range(tries):
        try:
            username = getpass.getpass(prompt.format(dsn, tail))
        except EOFError:
            return None
        if not empty and username == '':
            logging.error(_('You must enter non-empty username!'))
        else:
            return username
