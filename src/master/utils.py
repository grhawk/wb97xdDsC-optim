#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: utils
# Creation: Jul 15, 2015
#

"""Some basic utility.

"""

import os
import mmap
import logging as lg
from config import Config

config = Config().config

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-10-02"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


def file_exists(filep):
    lg.debug('Checking if file {} exists...'.format(filep))
    if not os.path.isfile(filep):
        lg_msg = 'File {} does not exist!'.format(filep)
        lg.critical(lg_msg)
        raise FileNotFoundError(lg_msg)

    lg.debug('{} found!'.format(filep))
    return True


def find_in_file(filep, strings_, reverse=False):
    found_line = []
    returnNone = False
    with open(filep, mode='r') as f:
        try:
            s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except ValueError:
            lg.warning('File {} empty... try increasing sleep time'
                       .format(filep))
            returnNone = True
    if isinstance(strings_, list):
        if returnNone:
            return [None] * len(strings_)
        for string_ in strings_:
            if reverse:
                result = s.rfind(string_)
            else:
                result = s.find(string_)
            if result != -1:
                s.seek(result)
                found_line.append(s.readline())
                s.seek(0)
            else:
                found_line.append(None)
    elif isinstance(strings_, str):
        if returnNone:
            return [None]
        result = s.find(strings_)
        s.seek(result)
        found_line.append(s.readline())
    else:
        msg = 'The second argument can be a string or a list of strings'
        raise ValueError(msg)

    return found_line


def create_dir(path):
    check_path = os.path.exists(path) and not os.path.isdir(path)
    check_path_dir = os.path.exists(path) and os.path.isdir(path)
    if check_path:
        msg = 'Remove the following path before continue:\n'
        msg += '{:s}\n'.format(path)
        lg.critical(msg)
        raise RuntimeError(msg)
    elif check_path_dir:
        return
    else:
        os.makedirs(path)
    return


def sum_is_one(flt1, flt2):
    return abs(1.0 - flt1 - flt2) <= config['precision']


def check_list_len(value, n, prm):
    if not isinstance(value, list) or len(value) != n:
        msg = '{} needs a list of {} element/s!'.format(prm, n)
        lg.critical(msg)
        raise (TypeError(msg))
    return True
