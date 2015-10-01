#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: config
# Creation: Sep 30, 2015
#

import os

"""Contains all the configurable variable (paths, precisions... etc.).

This module contains a config class with all the variables that depends on the
place where you are running. The class allows also to build preset of values so
that all the program can be easily ported.

Todo: Check if the all the variable related to the params file locations are
    actually needed.
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

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-10-01"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


join = os.path.join  # Just to make shorter lines below


class Config(object):

    config = dict(
        home=None,
        root=None,
        training_set_path=None,  # Was TrainingSetPath
        training_set_file=None,  # Was TrainingSetName
        run_name=None,  # Was Name
        loglevel=None,
        logfile=None,
        processes=None,
        precision=None,
        wb97x_param_file=None,  # Was ParamFile
        ddsc_param_file=None,  # Was dDsCParamFile
        wait_for_gamess_output=None,  # Was dormi
        wait_to_recheck=None,  # Was dormi-short
        maximum_times_to_recheck=None,  # was timeout_max
        temporary_densities_repo=None,
        gamess_bin=None,
        func_params_prefix=None,  # Was params_dir_func
        full_params_prefix=None,  # Was params_dir
        sbatch_script_prefix=None,
        densities_repo=None,  # Was tmp_density_dir
        command_full=None,
        command_func=None,
    )

    _help = dict(
        home='Absolute path to the home',
        root='Absolute path to the main directory',
        training_set_file='Name of the training_set_file',
        training_set_path='Path to the training set tree',
        run_name='Name of the present run (path where to save the'
                ' input and output)',
        loglevel='Level of the log file',
        logfile='Path to the log file',
        processes='Maximum number of parallel processes',
        precision='Maximum precision in comparing float',
        wb97x_param_file='Name of the file containing the wb97x parameters',
        ddsc_param_file='Name of the file containing the ddsc parameters',
        wait_for_gamess_output='Time to wait before starting checking the '
                ' gamess output',
        wait_to_recheck='Time to wait if the first cheking fails',
        maximum_times_to_recheck='How many check before a msg in the log is'
                ' printed to tell which file is missing',
        temporary_densities_repo='Repo where densities are saved on'
                ' the machine',
        gamess_bin='Absolute path to the gamess bin',
        func_params_prefix='Path where the big gamess look for '
                'parameters files',
        full_params_prefix='Path where the mini gamess look for'
                ' parameters files',
        sbatch_script_prefix='Command to queue the big gamess job',
        densities_repo='Path to save all the densities',
        command_full='Command to execute for the full gamess',
        command_func='Command to execute for the mini-gamess',
    )

    @staticmethod
    def set(kw, v):
        __class__.config[kw] = v

    @staticmethod
    def get(kw):
        return __class__.config[kw]

    @staticmethod
    def help(kw):
        if kw == 'all':
            msg = ''
            for k, v in __class__._help.items():
                msg += k + ' --> ' + str(v) + '\n'
            print(msg)
        else:
            print(kw + ' --> ' + str(__class__._help[kw]))

    @staticmethod
    def getall():
        msg = ''
        for k, v in __class__.config.items():
            msg += k + ' --> ' + str(v) + '\n'
        print(msg)


class Presets(object):

    def __init__(self):
        self.default()

    def _insert_in_config(self, dict_):
        for k, v in dict_.items():
            Config.set(k, v)



    def default(self):
        Config.set('home', os.path.expanduser('~'))

    def test(self):
        home = Config.get('home')
        root = join(home, 'MyCodes/wb97xdDsC-optim')  # shortening lines below
        tmp_data = join(root, 'run_example/TMP_DATA')  # shortening lines below
        prst = dict(root=root,
                    training_set_file=join('trset-tree-example'),
                    training_set_path=join(root, 'example/trset-tree-example/'),
                    run_name=join(root, 'run_example/test'),
                    logfile=join(root, 'output_example/logging.log'),
                    loglevel='DEBUG',
                    processes=8,
                    precision=1E-8,
                    wb97x_param_file=join(root, tmp_data, 'FUNC_PAR.dat'),
                    ddsc_param_file=join(root, tmp_data, 'a0b0'),
                    wait_for_gamess_output=1,
                    wait_to_recheck=3,
                    maximum_times_to_recheck=10,
                    temporary_densities_repo=tmp_data,
                    gamess_bin=None,
                    func_params_prefix=tmp_data,
                    full_params_prefix=tmp_data,
                    sbatch_script_prefix=tmp_data,
                    densities_repo=join(root, 'run_example/densities_repo'),
                    command_full='ssh <master> /usr/bin/sbatch',
                    command_func=join(root, 'bin/minigamess.x'),
                    )

        self._insert_in_config(prst)


def testing_Config():
    print('Testing the Config Class')

    cfg1 = Config()
    cfg2 = Config()

    print(cfg1.get('home'))
    print(cfg2.get('home'))

    print('Set home to HOME on cfg1')
    cfg1.set('home', 'HOME')
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))

    print('Set home to ASD on cfg2')
    cfg2.set('home', 'ASD')
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))

    print('Starting cfg3')
    cfg3 = Config()
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))
    print('cfg3', cfg3.get('home'))

    print('Set home to REHOME on cfg3.config')
    cfg3.config['home'] = 'REHOME'
    print('cfg1', cfg1.get('home'))
    print('cfg2', cfg2.get('home'))
    print('cfg3', cfg3.get('home'))

    print('The entire dictionary')
    print(cfg3.config)
    cfg2.config['root'] = 'ROOOOT'
    print(cfg3.config)

    cfg3.help('all')
    cfg3.help('home')

    cfg3.getall()

if __name__ == '__main__':
    testing_Config()
