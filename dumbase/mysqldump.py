# coding=utf8

import re
import tempfile
import os
import os.path
import subprocess
import logging

from dumbase.dsn import parse_dsn
from tempfile import mkstemp, gettempdir

def dump(dsn, password, tables, options):
    for table in tables:
        logging.info(_('dumping table <{0}>').format(table))
    output = get_dump_filename(dsn)
    logging.info(_('writing dump into <{0}>').format(output))
    retcode, stderr = _raw_execute(
        dsn, password, tables, output, options)
    for line in stderr:
        if re.search('^mysqldump: .* has insufficent privileges', line):
            raise InsufficentPrivilegesError(dsn, line)
    return output

def filter(tables, whitelist=[], blacklist=[]):
    filtered = set()
    filtered |= set([t for t in tables if not _check_list(t, blacklist)])
    filtered |= set([t for t in tables if _check_list(t, whitelist)])
    return list(filtered)

def check_cache(dsn):
    path = get_dump_filename(dsn)
    if os.path.exists(path):
        return path
    else:
        return False

def get_dump_filename(dsn):
    sanitized_dsn = re.sub('[^a-z0-9]', '_', dsn)
    return os.path.join(gettempdir(), sanitized_dsn + '.sql')

def _raw_execute(dsn, password, tables, output, options):
    conn = parse_dsn(dsn)
    fd_stdout = open(output, 'w')
    fd_stderr = open(mkstemp()[1], 'r+')
    retcode = subprocess.call([
            'mysqldump',
            '-h', conn['host'],
            '-P', conn['port'],
            '-u', conn['user'],
            '-p' + password,
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
