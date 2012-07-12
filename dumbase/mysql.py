# coding=utf8

import subprocess

def list(conn):
    output = execute(conn, 'show tables')
    return output.split('\n')

def exec_file(conn, dump):
    output = execute(conn, dump, from_file=True)

def execute(conn, statement, from_file=False):
    if conn['pwd'] == '' or conn['pwd'] is None:
        raise NoPasswordSpecifiedError(conn)
    retcode, output = _execute_raw(conn, statement, from_file)
    if retcode == 0:
        # -1, т.к. последяя строка всегда пустая
        return output[:-1]
    if output.startswith('ERROR 2005 '):
        raise UnknownHostError(conn)
    if output.startswith('ERROR 2003 '):
        raise CanNotConnectError(conn)
    if output.startswith('ERROR 1045 '):
        raise AccessDeniedError(conn)
    if output.startswith('ERROR 1046 '):
        raise NoDatabaseSelectedError(conn)
    raise UnknownError(conn, output)

def _execute_raw(conn, statement, from_file=False):
    if from_file:
        command = []
        stdin = open(statement, 'r')
    else:
        command = ['-e', statement]
        stdin = None
    try:
        return 0, subprocess.check_output([
            'mysql',
            '-h', conn['host'],
            '-P', conn['port'],
            '-u', conn['user'],
            '-p' + conn['pwd'],
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
