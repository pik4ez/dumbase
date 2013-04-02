#!/usr/bin/python
# -*- coding: utf-8 -*-

# [2] добавить русский перевод для строк
import os
import argparse
import sys
import logging
import i18n

from distutils.spawn import find_executable

_ = i18n.language.ugettext
argparse._ = _

import dumbase.mysql
import dumbase.mysqldump

from dumbase.dsn import parse_dsn
from dumbase.getdbuser import getdbuser
from dumbase.getdbpass import getdbpass

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

argparser = argparse.ArgumentParser(
    description=_('Dumping database like a boss.'))

# [1] аргументы
subparsers = argparser.add_subparsers(dest='action')
subparser = subparsers.add_parser(
    'list',
    help=_('lists tables from specified $dsn '
        'using whitelist and blacklist'))
# [1.1] аргумент для указания dsn
subparser.add_argument(
    'source_dsn',
    metavar='$dsn',
    help=_(
        'data source name for da target database: '
        '[$user@[:password]]$host[:$port]/$name'))
subparser.add_argument(
    '-i',
    '--include',
    default=[],
    metavar='$table',
    action='append',
    nargs='+',
    help=_(
        'include table for dumping (regex)'))
subparser.add_argument(
    '-e',
    '--exclude',
    default=[],
    metavar='$table',
    action='append',
    nargs='+',
    help=_(
        'ignores table for dumping (regex)'))
subparser.add_argument(
    '-c',
    '--clean',
    action='store_true',
    help=_('ignores all tables (use -i to specify tables you need)'))
subparser = subparsers.add_parser(
    'dump',
    help=_('dumps data from $source_dsn to $target_dsn'))
subparser.add_argument(
    'source_dsn',
    metavar='$source_dsn',
    help=_(
        'data source name for the source database '
        '(data will be imported from): '
        '[$user@[:password]]$host[:$port]/$name'))
subparser.add_argument(
    'target_dsn',
    metavar='$target_dsn',
    help=_(
        'data source name for the target database '
        '(data will be exported to): '
        '[$user@[:password]]$host[:$port]/$name'))
subparser.add_argument(
    '-f',
    '--force-redump',
    action='store_true',
    help=_(
        'force to make new dump without request'))
subparser.add_argument(
    '-i',
    '--include',
    default=[],
    metavar='$table',
    action='append',
    nargs='+',
    help=_(
        'include table for dumping (regex)'))
subparser.add_argument(
    '-e',
    '--exclude',
    default=[],
    metavar='$table',
    action='append',
    nargs='+',
    help=_(
        'ignores table for dumping (regex)'))
subparser.add_argument(
    '-s',
    '--schema',
    default=[],
    metavar='$schema',
    action='append',
    nargs='+',
    help=_(
        'sets a list of tables for which only schema should be dumped'))
subparser.add_argument(
    '--init-schema',
    action='store_true',
    help=_('make schema for all tables not included to dump with data'))
subparser.add_argument(
    '-c',
    '--clean',
    action='store_true',
    help=_(
        'ignores all tables (use --include to specify tables you need)'))
subparser.add_argument(
    '-t',
    '--triggers',
    default=[],
    action='store_true',
    help=_(
        'includes triggers into database dump (may require root access'))

args = argparser.parse_args()

args.include = [item for sublist in args.include for item in sublist]

if args.clean:
    args.exclude = ['.*']
else:
    args.exclude = [item for sublist in args.exclude for item in sublist]

if args.action == 'list':
    # check if mysql client installed
    if find_executable('mysql') == None:
        sys.stdout.write(_('ERROR: mysql client not installed, you should install it first') + '\n')
        sys.exit(1)

    # parse source dsn
    source_conn = parse_dsn(args.source_dsn)

    # ask for username and password if not present in dsn
    if source_conn['user'] is None:
        source_conn['user'] = getdbuser(args.source_dsn)
    if source_conn['pwd'] is None:
        source_conn['pwd'] = getdbpass(args.source_dsn)

    # check connection to source and target databases
    source_connected, source_error = dumbase.mysql.check_connection(source_conn)
    if not source_connected:
        sys.stdout.write(_('ERROR: failed to connect source database') + '\n')
        sys.stdout.write(source_error + '\n')
        sys.exit(1)

    tables = dumbase.mysql.list(source_conn)
    tables = dumbase.mysqldump.filter(
        tables, whitelist=args.include, blacklist=args.exclude)

    if tables == []:
        sys.stdout.write(_('<no tables>') + '\n')
    for table in tables:
        sys.stdout.write(table + '\n')

if args.action == 'dump':
    # check if mysql client installed
    if find_executable('mysql') == None:
        sys.stdout.write(_('ERROR: mysql client not installed, you should install it first') + '\n')
        sys.exit(1)

    # check if mysqldump installed
    if find_executable('mysqldump') == None:
        sys.stdout.write(_('ERROR: mysqldump not installed, you should install it first') + '\n')
        sys.exit(1)

    # parse source dsn
    source_conn = parse_dsn(args.source_dsn)

    # ask for username and password if not present in dsn
    if source_conn['user'] is None:
        source_conn['user'] = getdbuser(args.source_dsn)
    if source_conn['pwd'] is None:
        source_conn['pwd'] = getdbpass(args.source_dsn)

    # check connection to source and target databases
    source_connected, source_error = dumbase.mysql.check_connection(source_conn)
    if not source_connected:
        sys.stdout.write(_('ERROR: failed to connect source database') + '\n')
        sys.stdout.write(source_error + '\n')
        sys.exit(1)

    # tables_all        all tables existing in source database
    # tables_data       tables to dump with data
    # tables_schema     tables to dump without data (schema only)

    tables_all = dumbase.mysql.list(source_conn)
    tables_data = dumbase.mysqldump.filter(
        tables_all, whitelist=args.include, blacklist=args.exclude)

    # parse target dsn
    target_conn = parse_dsn(args.target_dsn)

    # ask for username and password if not present in target_dsn
    if target_conn['user'] is None:
        target_conn['user'] = getdbuser(args.target_dsn, tail=_('leave empty if same'), empty=True)
    if target_conn['pwd'] is None:
        target_conn['pwd'] = getdbpass(args.target_dsn, tail=_('leave empty if same'), empty=True)

    # use source username, password and database name if appropriate target fields not specified
    if target_conn['user'] == '':
        target_conn['user'] = source_conn['user']
    if target_conn['pwd'] == '':
        target_conn['pwd'] = source_conn['pwd']
    if target_conn['name'] == '':
        target_conn['name'] = source_conn['name']

    target_connected, target_error = dumbase.mysql.check_connection(target_conn)
    if not target_connected:
        sys.stdout.write(_('failed to connect target database') + '\n')
        sys.stdout.write(target_error + '\n')
        sys.exit(1)

    tables_schema = []

    if args.schema:
        tables_schema = [item for sublist in args.schema for item in sublist]
    elif args.init_schema:
        tables_schema = tables_all

    # do not dump schema for tables included in full dump
    for x in tables_data:
        if x in tables_schema:
            tables_schema.remove(x)

    if tables_schema:
        logging.info(_('dumping schema for tables: <{0}>').format(', '.join(tables_schema)))
        schema_dump = dumbase.mysqldump.dump_schema(source_conn, tables_schema)
        dumbase.mysql.exec_file(target_conn, schema_dump)

    if args.clean and args.include == []:
        logging.error(_(
            'if you use --clean flag, '
            'you must specify at least one matching --include flag'))
        sys.exit(1)

    if not args.force_redump:
        cache = dumbase.mysqldump.check_cache(source_conn)
    else:
        cache = False

    options = []
    if args.triggers:
        options.append('--triggers')

    use_cache = False
    if cache:
        use_cache = True
        choice = raw_input(_(
            'Recent dump found in {0}. '
            'Should I use it? [Y/n]: ').format(cache))
        if choice.lower() == 'n':
            use_cache = False

    if not use_cache:
        dump = dumbase.mysqldump.dump(
            source_conn, tables_data,
            options=[
                '--quick',
                '--skip-lock-tables'
            ] + options)
    else:
        dump = cache

    dumbase.mysql.exec_file(target_conn, dump)

