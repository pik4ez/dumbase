# -*- coding: utf-8 -*-

import re
import getpass

# expands lists in args
# for example, value 'a,b,c' would be expanded to ['a', 'b', 'c']
def expand_lists(args):
    for i, arg in enumerate(args):
        if re.search(r",", arg):
            del(args[i])
            args.extend(arg.split(','))

    return args

