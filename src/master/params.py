#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: params
# Creation: Jul 16, 2015
#

"""Implements everything on the parameters

"""

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-16"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Parameters(object):

    def __init__(self):
        self.allpar = dict(cc_aa_1=0.000)

    def set(self, p):
        """Sets all the parameters.

        Sets the parameters taking care of the constraints.

        Args:
            p (list or dict): can be a dictionary with parameters: value or a
                list with all the parameters

        """
        pass

    def get(self):
        """Return a dictionary with parameter: value.

        """
        pass

    def check(self):
        """Check if the instantiated parameters are the same as the class one.

        This method should be used to check if a new computation is acutally
        needed.

        Not sure to implement... and do some test before...
        """
        pass
