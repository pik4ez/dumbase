# coding=utf8

import re
import getpass

def parse_dsn(dsn):
    rest = dsn
    rest, _, name = rest.partition('/')
    rest, _, port   = rest.partition(':')
    user, _, host   = rest.rpartition('@')
    return {
        'host': host,
        'port': port or '3306',
        'user': user or getpass.getuser(),
        'name': name
    }
