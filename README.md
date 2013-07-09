dumbase
=======

Creates database dump from one server and uploads it to another server.


Features
--------

* List tables in database
* Whitelisting or blacklisting of tables to be dumped
* Last dump reusage
* Easy localization


Installation
------------

1. Clone repo (`git clone`)
1. Allow execution (`chmod +x dumbase.py`)
1. Generate locale files (see below)


Usage
-----

### List tables ###

```
./dumbase.py list $dsn
  $dsn  source database DSN [$user@]$host[:$port]/$dbname
```

Additional help: `dumbase.py list -h`


### Dump ###

```
./dumbase.py dump $source_dsn $target_dsn
  $source_dsn  source database DSN
  $target_dsn  destination database DSN
```

Additional help: `dumbase.py dump -h`

#### Additional parameters ####

`-e` excludes table or a set of tables (separated by space) from dump

`-i` includes table or a set of tables into dump (useful with flag `-c`)

`-c` excludes all tables from dump, use with flag `-i`

`-t` includes triggers into database dump (root access may be required)

`-f` force create dump even if there is valid cache

`-s` list of tables, for which only schema will be dumped

`--init-schema` automatically create schema for tables excluded from dump

#### Examples ####

`./dumbase.py dump -c -i t1 -- $source $target`
dumps one table `t1` including data

`./dumbase.py dump -e t2 t3 -- $source $target`
dumps all tables with data except `t2` and `t3`

`./dumbase.py dump --init-schema -e t1 t2 -- $source $target`
dumps all tables with data except `t1` and `t2`, creates empty tables
`t1` and `t2` (because they were excluded from dump and `--init-schema`
flag is set)

`./dumbase.py dump -c -i t1 -s t2 t3 -- $source $target`
dumps table `t1` with data, creates empty tables `t2` and `t3`

`./dumbase.py dump -f $source $target`
dumps all tables with data ignoring cache


Localization files generation
-----------------------------

Plain text localization files stored in `locale` directory. It is required to generate
binary files to make localization works. One may use any utility that make .mo files
from plain text .po files. For example, one may choose msgfmt.py.

Example for ru\_RU locale:
```
cd /path/to/dumbase
msgfmt -o locale/ru_RU/LC_MESSAGES/dumbase.mo locale/ru_RU/LC_MESSAGES/dumbase.po
```


Autocomplete
------------

```
pip install argcomplete
activate-global-python-argcomplete
```

Additional info: https://argcomplete.readthedocs.org/en/latest/


