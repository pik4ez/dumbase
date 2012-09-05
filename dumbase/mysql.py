# -*- coding: utf-8 -*-

import subprocess
import i18n

_ = i18n.language.ugettext

def check_connection(conn):
    """Checks connection to database

    Returns:
    connection status -- bool
    connection error -- string

    """
    statement = 'SELECT 1'

    try:
        result = execute(conn, statement)
    except UnknownHostError:
        return False, _('unknown host')
    except CanNotConnectError:
        return False, _('failed to connect')
    except AccessDeniedError:
        return False, _('access denied')
    except NoDatabaseSelectedError:
        return False, _('no database specified')
    except UnknownError:
        return False, _('unknown error')

    return True, ''

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

class NoPasswordSpecifiedError(Exception):
    pass

class UnknownError(Exception):
    pass
