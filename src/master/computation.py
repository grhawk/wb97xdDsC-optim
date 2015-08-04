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
import shlex
import shutil
import logging as lg
from make_input import Input
import os
import mmap

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
                   gamess_bin='/home/petragli/wb97xddsc/gamess-opt/GAMESS',
                   params_dir='/home/petragli/wb97xddsc/USED_PARAMS',
                   sbatch_script_prefix='/home/petragli/wb97xddsc/USED_PARAMS',
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

    def _run(self, command):
        print('Should run {}'.format(command))
        out = open(self.name + "log", mode='w')
        subprocess.call(self.command, stdout=out)

    def _readout(self):
        while True:
            time.sleep(self.dormi)
            with open(self._inout_out_path, mode='r') as f:
                s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                for string_ in __class__._config['well_finished']:
                    if s.find(string_) != -1:
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

    def _write_sbatch(self):
        txt = '#!/bin/bash'
        txt += '#SBATCH -J {TITLE:s}'.format(TITLE=self.molID)
        txt += '#SBATCH -o /home/petragli/err/{TITLE:s}.stdout_%j'.\
            format(TITLE=self.molID)
        txt += '#SBATCH -e /home/petragli/err/{TITLE:s}.stderr_%j'.\
            format(TITLE=self.molID)
        txt += '#SBATCH --mem=8000'
        txt += '#SBATCH --nodes=1'
        txt += '#SBATCH --ntasks-per-node=1'
        txt += 'source /software/ENV/set_mkl-110.sh'
        txt += 'source /software/ENV/set_impi_410.sh'
        txt += 'export EXTBAS=/dev/null'
        txt += 'export SLURM_NODEFILE=$SLURM_TMPDIR/machines'
        txt += 'srun --ntasks=$SLURM_NNODES hostname -s > $SLURM_NODEFILE'
        txt += 'cd $SLURM_SUBMIT_DIR'
        txt += 'cp {PARAMS_DIR:s}/a0b0 $SLURM_TMPDIR'.\
            format(PARAMS_DIR=__class__._config['params_dir'])
        txt += 'cp {PARAMS_DIR:s}/FUNC_PAR.dat $SLURM_TMPDIR'.\
            format(PARAMS_DIR=__class__._config['params_dir'])
        txt += '{BIN:s}/rungmsQUEUE {INPUT:s} 00 1 $SLURM_CPUS_ON_NODE &> {OUTPUT:s}'.\
            format(INPUT=self._inout_inp_path,
                   OUTPUT=self._inout_out_path,
                   BIN=__class__._config['GAMESS_BIN'])
        txt += 'joberror=$?'
        txt += 'cp -r $SLURM_TMPDIR/PARAM_UNF.dat {DENSITY_DEST}'.\
            format(DENSITY_DEST='')
        txt += 'cp -r $SLURM_TMPDIR/dDsC_PAR {dDSC_DEST}'.\
            format(dDSC_DEST='')
        txt += 'exit'

        self._sbatch_file = \
            os.path.join(__class__._config['sbatch_script_prefix'], self.molID)

        with open(self._sbatch_file, 'w') as f:
            f.write(txt)

    def fulldft(self):
        command = shlex.split('/bin/sbatch {SBATCH_FILE:s}'
                              .format(self._sbatch_file))
        self._write_input()
        self._run(command)
        self._readout()
        self._move_data()

    def func(self):
        command = ['./START.x']
        self._run(command)
        self._readout()



