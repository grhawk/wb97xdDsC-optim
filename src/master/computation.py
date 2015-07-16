#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: computation
# Creation: Jul 16, 2015
#

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
  Examples can be given using either the ``Example`` or ``Examples``
  sections. Sections support any reStructuredText formatting, including
  literal blocks::

      $ python example_google.py

Section breaks are created by simply resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
  module_level_variable (int): Module level variables may be documented in
    either the ``Attributes`` section of the module docstring, or in an
    inline docstring immediately following the variable.

    Either form is acceptable, but the two should not be mixed. Choose
    one convention to document module level variables and be consistent
    with it.

.. _Google Python Style Guide:
   http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

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


class GenericRun(object):

    def __init__(self):
        self.command = 'uname -a'
        pass

    def write_input(self):
        pass

    def runall(self):
        print('Should run {}'.format(self.command))
        pass

    def read_out(self):
        pass


class run_gamess(GenericRun):

    def __init__(self):
        self.commanf = 'subgms etc.'
        pass

    def move_density(self):
        pass


class run_density(GenericRun):

    def __init__(self):
        self.command = 'START.F90 o quello che e'
        pass


class run_ddsc(GenericRun):

    def __init__(self):
        self.command = 'Quello che sara'
        pass