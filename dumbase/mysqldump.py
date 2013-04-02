# -*- coding: utf-8 -*-

import re
import tempfile
import os
import os.path
import subprocess
import logging
import i18n

_ = i18n.language.ugettext

from tempfile import mkstemp, gettempdir

def dump(conn, tables, options, output = None):
    for table in tables:
        logging.info(_('dumping table <{0}>').format(table))
    
    if not output:
        output = get_dump_filename(conn)

    logging.info(_('writing dump into <{0}>').format(output))
    retcode, stderr = _raw_execute(
        conn, tables, output, options)
    for line in stderr:
        if re.search('^mysqldump: .* has insufficent privileges', line):
            raise InsufficentPrivilegesError(conn, line)
    return output

def dump_schema(conn, tables):
    output = get_dump_filename(conn, '-schema')
    return dump(conn, tables, ['--no-data'], output)

def filter(tables, whitelist=[], blacklist=[]):
    filtered = set()
    filtered |= set([t for t in tables if not _check_list(t, blacklist)])
    filtered |= set([t for t in tables if _check_list(t, whitelist)])
    return list(filtered)

def check_cache(conn):
    path = get_dump_filename(conn)
    if os.path.exists(path):
        return path
    else:
        return False

def get_dump_filename(conn, postfix = ''):
    # OPTIMIZE: rewrite using map to get rid of duplication
    u = re.sub('[^a-z0-9]', '_', conn['user'])
    p = re.sub('[^a-z0-9]', '_', conn['port'])
    h = re.sub('[^a-z0-9]', '_', conn['host'])
    n = re.sub('[^a-z0-9]', '_', conn['name'])

    filename = u + '_' + h + '_' + p + '_' + n + postfix +'.sql'
    result = os.path.join(gettempdir(), filename)

    return result

def _raw_execute(conn, tables, output, options):
    fd_stdout = open(output, 'w')
    fd_stderr = open(mkstemp()[1], 'r+')

    retcode = subprocess.call([
            'mysqldump',
            '-h', conn['host'],
            '-P', conn['port'],
            '-u', conn['user'],
            '-p' + conn['pwd'],
            '--verbose',
            conn['name']
        ] + options + ['--'] + tables,
        stdout=fd_stdout,
        stderr=fd_stderr)
    fd_stderr.seek(0)
    stderr = fd_stderr.readlines()
    os.unlink(fd_stderr.name)
    return retcode, stderr


def _check_list(item, control_list):
    return [p for p in control_list if re.match(p, item)] != []

class InsufficentPrivilegesError(Exception):
    pass
