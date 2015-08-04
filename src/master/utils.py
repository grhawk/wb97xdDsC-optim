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

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-08-04"
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
        raise(FileNotFoundError(lg_msg))

    lg.debug('{} found!'.format(filep))
    return True


def find_in_file(filep, strings_):
    with open(filep, mode='r') as f:
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    if isinstance(strings_, list):
        for string_ in strings_:
            result = s.find(string_)
            if result != -1:
                break
    else:
        result = s.find(strings_)

    if result != -1:
        s.seek(result)
        return s.readline()

    return None
