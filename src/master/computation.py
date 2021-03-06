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
from random import randint
import shutil
import logging as lg
from make_input import Input
import os
from utils import find_in_file, file_exists, create_dir
from config import Config

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-10-05"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


config = Config().config
config['well_finished_strings'] = [b'exit gracefully',
                                   b'FINAL ENERGY INCLUDING dDsC DISPERSION:',
                                   b'DFT EXCHANGE + CORRELATION ENERGY =',
                                   b'Final Energy']


class Run(object):

    _inout_id = None
    _run_name = None
    _tset_path = None

    def __init__(self, molID=None, dset=None, run_name=None, tset_path=None):

        if molID and dset and not run_name and not tset_path:
            if not __class__._run_name or not __class__._tset_path:
                msg = 'run_name has to be specified before to instance a'\
                    ' useful class!'
                lg.critical(msg)
                raise RuntimeError(msg)
            self._inout_path = os.path.join(__class__._run_name, dset,
                                            'inout', __class__._inout_id)
            self._inout_path = os.path.abspath(self._inout_path)

            create_dir(self._inout_path)

            self._xyzp = os.path.join(__class__._tset_path, dset,
                                      'geometry', molID.split('.')[1] + '.xyz')

            self._inout_inp_path = os.path.join(self._inout_path,
                                                molID + '.inp')
            self._inout_out_path = os.path.join(self._inout_path,
                                                molID + '.log')
            self.molID = molID

            create_dir(config['densities_repo'])

            self._wb97x_saves = os.path.join(config['densities_repo'],
                                             self.molID + '.wb97x')
            self._ddsc_saves = os.path.join(config['densities_repo'],
                                            self.molID + '.ddsc')
            self._sbatch_file = \
                os.path.join(config['sbatch_script_prefix'],
                             self.molID)
        elif not molID and not dset and run_name and tset_path:
            __class__._run_name = run_name
            __class__._tset_path = tset_path
        else:
            msg = 'You cannot specify run_name, dset_path and molID all'\
                ' together in Run'
            lg.critical(msg)
            raise AttributeError(msg)

    @property
    def index(self):
        return __class__._inout_id

    @index.setter
    def index(self, index):
        lg.debug('Index set to {}'.format(index))
        __class__._inout_id = index

    def _write_input(self):
        Input(self._xyzp).write(self._inout_inp_path)

    def _run(self, command):
        lg.debug('Should run {}'.format(command))
        return subprocess.check_output(command)

    def _readout(self):
        timeout = 0
        not_found = False
        while True:
            timeout += 1
            time.sleep(config['wait_for_gamess_output'])
            if timeout % config['maximum_times_to_recheck'] == 0:
                not_found = True
                lg.warning('Final energy not found for file {}... '
                           'Do something!!'.format(self._inout_out_path))

            if not os.path.exists(self._inout_out_path): continue

            find = find_in_file(self._inout_out_path,
                                config['well_finished_strings'],
                                reverse=True)

            if find[1] and find[2] and find[3]:
                if not_found:
                    lg.warning('Final energy for file {} found!!'
                               .format(self._inout_out_path))
                if abs(float(find[1].split()[5])) < float(b'0.0E-8'):
                    msg = 'Energy in Gamess is almost zero: {:f}'.\
                        format(float(find[1].split()[5]))
                    lg.critical(msg)
                    raise(RuntimeError(msg))

                return (float(find[1].split()[5]),
                        float(find[2].split()[6]), float(find[3].split()[2]))

    def _move_data(self):
        dens_orig = os.path.join(config['temporary_densities_repo'],
                                 self.molID + '.wb97x')
        ddsc_orig = os.path.join(config['temporary_densities_repo'],
                                 self.molID + '.ddsc')
        while True:
            time.sleep(config['wait_to_recheck'])
            allfile = True
            for filep in [dens_orig, ddsc_orig]:
                try:
                    file_exists(filep)
                except FileNotFoundError:
                    allfile = False
            if allfile: break
        shutil.move(dens_orig, self._wb97x_saves)
        shutil.move(ddsc_orig, self._ddsc_saves)

    def _write_sbatch(self):
        input_path, input_file = os.path.split(self._inout_inp_path)
        del(input_path)
        txt = '#!/bin/bash\n'
        txt += '#SBATCH -J {TITLE:s}\n'.format(TITLE=self.molID)
        txt += '#SBATCH -o ' + os.path.join(self._inout_path,
                                            self.molID + '.stdout') + '\n'
        txt += '#SBATCH -e ' + os.path.join(self._inout_path,
                                            self.molID + '.stderr') + '\n'
        txt += '#SBATCH --mem=64000\n'
        txt += '#SBATCH --nodes=1\n'
        txt += '#SBATCH --ntasks-per-node=8\n'
#        txt += '#SBATCH --partition=debug\n'
        txt += '\n'
#        txt += 'module load intel/14.0.2\n'
        txt += 'export EXTBAS=/dev/null\n'
        txt += 'echo $PWD\n'
        txt += 'WORKINGDIR=$PWD\n'
        txt += 'cd $SLURM_TMPDIR\n'
        txt += 'cp {INPUTFILE:s} $SLURM_TMPDIR\n'\
            .format(INPUTFILE=self._inout_inp_path)
        txt += 'cp {PARAMS_DIR:s}/a0b0 $SLURM_TMPDIR\n'\
            .format(PARAMS_DIR=config['full_params_prefix'])
        txt += 'cp {PARAMS_DIR:s}/FUNC_PAR.dat $SLURM_TMPDIR\n'.\
            format(PARAMS_DIR=config['full_params_prefix'])
        txt += '{BIN:s}/rungms {INPUT:s} 00 8 &> {OUTPUT:s}\n'.\
            format(INPUT=input_file,
                   OUTPUT=self._inout_out_path,
                   BIN=str(config['gamess_bin']))
        txt += 'joberror=$?\n'
        txt += 'cat $SLURM_TMPDIR/*.data > $SLURM_TMPDIR/PARAM_UNF.dat\n'
        txt += 'cp -r $SLURM_TMPDIR/PARAM_UNF.dat {DENSITY_DEST}\n'.\
            format(DENSITY_DEST=os.path.join(config['temporary_densities_repo'],
                                             self.molID + '.wb97x'))
        txt += 'cp -r $SLURM_TMPDIR/dDsC_PAR {dDSC_DEST}\n'.\
            format(dDSC_DEST=os.path.join(config['temporary_densities_repo'],
                                          self.molID + '.ddsc'))
#        txt += 'cp -ar $SLURM_TMPDIR $WORKINGDIR\n'
        txt += 'exit\n'

        with open(self._sbatch_file, 'w') as f:
            f.write(txt)

    def full(self):

        command = shlex.split('{COMMAND:s} {SBATCH_FILE:s}'
                              .format(COMMAND=config['command_full'],
                                      SBATCH_FILE=self._sbatch_file))
        self._write_input()
        time.sleep(randint(1,10))
        self._write_sbatch()
        if os.path.dirname(config['ddsc_params_writing']) != config['full_params_prefix']:
            shutil.copy(config['ddsc_params_writing'], config['full_params_prefix'])
        if os.path.dirname(config['wb97x_params_writing']) != config['full_params_prefix']:
            shutil.copy(config['wb97x_params_writing'], config['full_params_prefix'])
        if config['gamess_bin']: self._run(command)
        energies = self._readout()
        if config['gamess_bin']: self._move_data()
        return energies

    def func(self):
        multiplicity=Input(self._xyzp).mult()
        if int(multiplicity) > 1:
           unrestricted='U'
        else:
           unrestricted='R'

        wb97x_param = os.path.join(config['func_params_prefix'],
                                   config['wb97x_params_file'])
        ddsc_param = os.path.join(config['func_params_prefix'],
                                  config['ddsc_params_file'])
        command = '{COMMAND:s} {WB97X_DATA:s} {DDSC_DATA:s} '\
            ' {WB97X_PARAM:s} {DDSC_PARAM:s} {UNRESTRICTED:s}'\
            .format(COMMAND=config['command_func'],
                    WB97X_DATA=self._wb97x_saves,
                    DDSC_DATA=self._ddsc_saves,
                    WB97X_PARAM=wb97x_param,
                    DDSC_PARAM=ddsc_param,
                    UNRESTRICTED=unrestricted)
        command = shlex.split(command)
        return (float(self._run(command).split()[1]))
