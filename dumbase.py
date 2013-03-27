#!/usr/bin/python
# -*- coding: utf-8 -*-

# [2] добавить русский перевод для строк
import os
import argparse
import sys
import logging
import i18n

_ = i18n.language.ugettext
argparse._ = _

from dumbase.dsn import parse_dsn

import dumbase.mysql
import dumbase.mysqldump

from dumbase.getdbuser import getdbuser
from dumbase.getdbpass import getdbpass
from dumbase.args import expand_lists

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

argparser = argparse.ArgumentParser(
    description=_('Dumping database like a boss.'))

# [1] аргументы
subparsers = argparser.add_subparsers(dest='action')
subparser = subparsers.add_parser(
    'list',
    help=_('lists tables from specified $dsn '
        'using blacklisting and whitelisting'))
# [1.1] аргумент для указания dsn
subparser.add_argument(
    'source_dsn',
    metavar='$dsn',
    help=_(
        'data source name for da target database: '
        '[$user@[:password]]$host[:$port]/$name'))
subparser = subparsers.add_parser(
    'dump',
    help=_('dumping data from $source_dsn into $target_dsn'))
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
# #3 принудительное снятие дампа, даже при наличии кэша
subparser.add_argument(
    '--force-redump',
    '-fr',
    action='store_true',
    help=_(
        'force to make new dump without request'))
# [1.2] аргумент для указания пароля
# [1.3] аргумент для указания whitelist
argparser.add_argument(
    '--white',
    '--include',
    default=[],
    metavar='$table',
    action='append',
    help=_(
        'white table for dumping (regex)'))
# [1.4] аргумент для указания blacklist
argparser.add_argument(
    '--black',
    '--exclude',
    '--ignore',
    default=[],
    metavar='$table',
    action='append',
    help=_(
        'ignores table for dumping (regex)'))
argparser.add_argument(
    '--black-all',
    '--exclude-all',
    '--ignore-all',
    action='store_true',
    help=_(
        'sets to ignore all tables (use --white to specify tables you need)'))
argparser.add_argument(
    '--triggers',
    default=[],
    action='store_true',
    help=_(
        'includes triggers into database dump'))
# [1.5] аргумент для указания формата даты

args = argparser.parse_args()

if args.black_all:
    args.black = ['.*']

# expand lists of tables in --black and --white args
if args.black:
    args.black = expand_lists(args.black)
if args.white:
    args.white = expand_lists(args.white)

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
    sys.stdout.write(_('failed to connect source database') + '\n')
    sys.stdout.write(source_error + '\n')
    sys.exit(1)

tables = dumbase.mysql.list(source_conn)
tables = dumbase.mysqldump.filter(
    tables, whitelist=args.white, blacklist=args.black)

if args.action == 'list':
    if tables == []:
        sys.stdout.write(_('<no tables>') + '\n')
    for table in tables:
        sys.stdout.write(table + '\n')

if args.action == 'dump':
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

    if args.black_all and args.white == []:
        logging.error(_(
            'if you use --black-all flag, '
            'you must specify at least one matching --white flag'))
        sys.exit(1)

    if args.force_redump == False:
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
            source_conn, tables,
            options=[
                # TODO: комментарии
                '--quick',
                '--skip-lock-tables'
        ] + options)
    else:
        dump = cache

    dumbase.mysql.exec_file(target_conn, dump)

