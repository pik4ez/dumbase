# coding=utf8

import subprocess

from dumbase.dsn import parse_dsn

def list(dsn, password):
    output = execute(dsn, password, 'show tables')
    return output.split('\n')

def exec_file(dsn, password, dump):
    output = execute(dsn, password, dump, from_file=True)

def execute(dsn, password, statement, from_file=False):
    if password == '' or password is None:
        raise NoPasswordSpecifiedError(dsn)
    retcode, output = _execute_raw(dsn, password, statement, from_file)
    if retcode == 0:
        # -1, т.к. последяя строка всегда пустая
        return output[:-1]
    if output.startswith('ERROR 2005 '):
        raise UnknownHostError(dsn)
    if output.startswith('ERROR 2003 '):
        raise CanNotConnectError(dsn)
    if output.startswith('ERROR 1045 '):
        raise AccessDeniedError(dsn)
    if output.startswith('ERROR 1046 '):
        raise NoDatabaseSelectedError(dsn)
    raise UnknownError(dsn, output)

def _execute_raw(dsn, password, statement, from_file=False):
    if from_file:
        command = []
        stdin = open(statement, 'r')
    else:
        command = ['-e', statement]
        stdin = None
    conn = parse_dsn(dsn)
    try:
        return 0, subprocess.check_output([
            'mysql',
            '-h', conn['host'],
            '-P', conn['port'],
            '-u', conn['user'],
            '-p' + password,
            '-B',
            '--skip-column-names',
            conn['name']
        ] + command,
        stdin=stdin,
        stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output

class UnknownHostError(Exception):
    pass

class CanNotConnectError(Exception):
    pass

class AccessDeniedError(Exception):
    pass

class NoDatabaseSelectedError(Exception):
    pass

class UnknownError(Exception):
    pass
