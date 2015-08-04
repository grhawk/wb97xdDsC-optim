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


import time
import shutil
import logging as lg
from make_input import Input
import os

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


class Run(object):

    _inout_id = None
    _config = dict(dormi=60,
                   timout=0,
                   timeout_max=10,
                   densities_repo='/dev/shm',
                   )

    def __init__(self, molID, dset_path):

        self._inout_path = os.path.join(dset_path, 'inout', __class__._inout_id)
        self._inout_path = os.path.abspath(self._inout_path)
        if not os.path.isdir(self._inout_path):
            os.makedirs(self._inout_path)

        self._xyzp = os.path.join(dset_path, 'geometry', molID.split('.')[1])

        self._inout_inp_path = os.path.join(self._inout_path, molID + '.inp')
        self._inout_out_path = os.path.join(self._inout_path, molID + '.log')
        self.molID = molID

    def _write_input(self):
        Input(self._xyzp).write(self._inout_inp_path)

    def _run(self):
        print('Should run {}'.format(self.command))
        out = open(self.name + "log", mode='w')
        subprocess.call(self.command, stdout=out)

    def _readout(self):
        while True:
            time.sleep(self.dormi)
            with open(self._inout_out_path, mode='r') as g:
                for line in g:
                    if "exited gracefully" in line:
                        break
                    else:
                        print('Exited gracefully not found.')

            for self.timeout in enumerate(self.timeoutMAX):
                if int(self.timeout) > int(self.timeoutMAX):
                    print('File not found.')

            self.timeout += 1

    def _move_data(self):
        shutil.copy('PARAM_UNF.dat',
                    os.path.join(__class__.config['densities_repo'],
                                 self.molID + '.dens')
                    )

    def fulldft(self):
        command = ["/software/gamess/rungms", self.name + "inp", "13" , "1"]
        self._write_input()
        self._run()
        self._readout()
        self._move_data()


    def func(self):
        command = ['./START.x']
        self._run()
        self._readout()



