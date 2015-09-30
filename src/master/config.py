#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: config
# Creation: Sep 30, 2015
#

"""Contains all the configurable variable (paths, precisions... etc.).

This module contains a config class with all the variables that depends on the
place where you are running. The class allows also to build preset of values so
that all the program can be easily ported.
"""

"""Example.
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
__updated__ = "2015-09-30"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Config(object):

    _config = dict(
        home = None,
        root = None,
        training_set_file = None,  # Was TrainingSetPath
        run_name = None,
        loglevel = None,
        logfile = None,
        processes = None,
        precision = None,
        wb97x_param_file = None,  # Was ParamFile
        ddsc_param_file = None,  # Was dDsCParamFile
        wait_for_gamess_output = None,  # Was dormi
        wait_to_recheck = None,  # Was dormi-short
        maximum_time_to_recheck = None,  # was timeout_max
        temporary_densities_repo = None,
        gamess_bin = None,
        func_params_prefix = None,  # Was params_dir_func
        full_params_prefix = None,  # Was params_dir
        sbatch_script_prefix = None,
        densities_repo = None,  # Was tmp_density_dir
        command_full = None,
        command_func = None,
    )

    _help = dict(
        home = 'Absolute path to the home',
        root = 'Absolute path to the main directory',
        training_set_file = 'Path to the training_set_file',  # Was TrainingSetPath
        run_name = 'Name of the present run (path where to save the input and output)',
        loglevel = 'Level of the log file',
        logfile = 'Path to the log file',
        processes = 'Maximum number of parallel processes',
        precision = 'Maximum precision in comparing float',
        wb97x_param_file = 'Name of the file containing the wb97x parameters',  # Was ParamFile
        ddsc_param_file = 'Name of the file containing the ddsc parameters',  # Was dDsCParamFile
        wait_for_gamess_output = 'Time to wait before starting checking the gamess output',  # Was dormi
        wait_to_recheck = 'Time to wait if the first cheking fails',  # Was dormi-short
        maximum_time_to_recheck = 'How many check before a msg in the log is printed to tell which file is missing',  # was timeout_max
        temporary_densities_repo = 'Repo where densities are saved on the machine',
        gamess_bin = 'Absolute path to the gamess bin',
        func_params_prefix = 'Path where the big gamess look for parameters files',  # Was params_dir_func
        full_params_prefix = 'Path where the mini gamess look for parameters files',  # Was params_dir
        sbatch_script_prefix = 'Command to queue the big gamess job',
        densities_repo = 'Path to save all the densities',  # Was tmp_density_dir
        command_full = 'Command to execute for the full gamess',
        command_func = 'Command to execute for the mini-gamess',
    )

    @staticmethod
    def set(kw, v):
        __class__._config[kw] = v

    @staticmethod
    def get(kw):
        return __class__._config[kw]

    @staticmethod
    def help(kw):
        if kw == 'all':
            msg = ''
            for k,v in __class__._help.items():
                msg += k + ' --> ' + str(v) + '\n'
            print(msg)
        else:
            print(kw + ' --> ' + str(__class__._help[kw]))

    @staticmethod
    def getall():
        msg = ''
        for k, v in __class__._config.items():
            msg += k + ' --> ' + str(v) + '\n'
        print(msg)
        


class PresetConfig(object):

    def __init__(self):
        pass



def testing_Config():
    print('Testing the Config Class')

    cfg1 = Config()
    cfg2 = Config()

    print(cfg1.get('home'))
    print(cfg2.get('home'))

    print('Set home to HOME on cfg1')
    cfg1.set('home','HOME')
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))

    print('Set home to ASD on cfg2')
    cfg2.set('home','ASD')
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))

    print('Starting cfg3')
    cfg3 = Config()
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))
    print('cfg3', cfg3.get('home'))

    print('Set home to REHOME on cfg3')
    cfg2.set('home','REHOME')
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))
    print('cfg3', cfg3.get('home'))

    cfg3.help('all')
    cfg3.help('home')

    cfg3.getall()

if __name__ == '__main__':
    testing_Config()
