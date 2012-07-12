# coding=utf8

import re
import getpass

# parses dsn in the following format
# user[:pass]@host[:port]/dbname

def parse_dsn(dsn):
    rest, _, name = dsn.partition('/')
    userpwd, _, hostport   = rest.rpartition('@')
    user, _, pwd = userpwd.partition(':')
    host, _, port = hostport.partition(':')

    return {
        'host': host,
        'port': port or '3306',
        'user': user or getpass.getuser(),
        'pwd': pwd or None,
        'name': name
    }

