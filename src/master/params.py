#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: params
# Creation: Jul 16, 2015
#

"""Implements everything on the parameters and take care of the param files.

"""


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
__updated__ = "2015-07-24"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Parameters(object):

    _parameters = dict(tta=[],
                       ttb=[],
                       cxhf=[],
                       omega=[],
                       cx_aa=[],
                       cc_aa=[],
                       cc_ab=[])

    _to_optimize = []

    def __init__(self, kvd):
        self.prms = kvd
        self.sorted = sorted(list(__class__._parameters.keys()))

    @property
    def prms(self):

        return __class__._parameters

    @prms.setter
    def prms(self, kvd):
        """Sets all the class parameters and write them on the right file.

        Sets the parameters taking care of the constraints.

        Args:
            kvd (list or dict): can be a dictionary with parameters: value or a
                list with all the parameters

        """
        if isinstance(kvd, list):
            if len(kvd) != 19:
                msg = 'The list must contains 19 elements!'
                lg.critical(msg)
                raise IndexError(msg)
            self.convert2dict(kvd)

        if isinstance(kvd, dict):
            for k in kvd.keys():
                if k in __class__._parameters:
                    if len(kvd[k]) == len(__class__._parameters[k]):
                        __class__._parameters[k] = kvd[k]
                    else:
                        msg = 'The number of parameters specified does not\
                        match the expected number'
                        lg.error(msg)
                else:
                    msg = 'The dict contains keys not present in the parameters\
                    dict. Those will be ignored.'
                    lg.error(msg)

    def convert2dict(self, list_):
        keys = sorted(list(__class__._parameters.keys()))
        l = 0
        for i, k in enumerate(keys):
            i += l
            if k[2] == '_':
                __class__._parameters[k] = list_[i:i + 5]
                l += 4
            else:
                __class__._parameters[k] = [list_[i]]

    def convert2list(self):
        list_ = []
        for k, v in sorted(__class__._parameters.items()):
            print(k, v)
            list_ += v
        return list_


    def get(self):
        """Return a dictionary with parameter: value.

        """
        pass

    def validity(self):
        """Check if the instantiated parameters are the same as the class one.

        This method should be used to check if a new computation is actually
        needed.

        Not sure to implement... and do some test before...

        """
        pass

    def refresh(self):
        """Copy the class parameter to the instantiated ones.

        After calling refresh the validity test will be true.

        """
