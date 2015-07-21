#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: main
# Creation: Jul 15, 2015
#

"""Main file of the application.

"""
import logging as lg
import make_input as mkinp
import os
import sys
import trset

# import resource
# lg.debug('Memory Usage {} (kb)'.format(
# resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-21"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'

config = dict(
    logfile='wb97xdDsC-optim.log',
    loglevel='DEBUG')


def main():
    init_logging()
    lg.debug('test')
    testing = ['trset_TrainingSet']
#    testing = ['trset_DataSet']

    # Testing make_input
    if 'make_input' in testing:
        newinput = mkinp.Input('test.xyz')
        del newinput

    # Testing Molecule
    if 'trset_Molecule' in testing:
        molpath = '../../example/trset-tree-example/S-022/geometry/001.xyz'
        mol = trset.Molecule(molpath)
        lg.debug(str(mol))

    if 'trset_System' in testing:
        rulep = ('../../example/trset-tree-example/S-022/rule.dat')
        with open(rulep, 'r') as rulef:
            line = rulef.readline()
            while line[0] == '#':
                line = rulef.readline()
        system = trset.System(line, 'S-022')
        lg.info(str(system))
        lg.info(system.fulldft_energy_error())
        lg.info(system.fulldft_energy())
        system.set_fulldft()
        lg.info(system.fulldft_energy())

    if 'trset_DataSet' in testing:
        path = ('../../example/trset-tree-example/S-022')
        dset = trset.DataSet(path)
        print(dset.get_fulldftlist())
        print(dset.get_blacklist())
        dset.add_to_blacklist(['1', '2', '3', '4'])
        dset.add_to_fulldftlist(['5', '6', '3', '4'])
        print(dset.get_fulldftlist())
        print(list(map(lambda x: x.name, dset.get_blacklist())))
        print(list(map(lambda x: x.name, dset.get_fulldftlist())))

    if 'trset_TrainingSet' in testing:
        path = ('../../example/trset-tree-example')
        tset = trset.TrainingSet(path, 'test-tset.dat')
        # print(list(map(str, tset.container)))
        print(tset.get_blacklist())
        print(tset.get_fulldftlist())
        print(tset.compute_MAE())

def init_logging():
    if os.path.isfile(config['logfile']):
        sys.stderr.write('Logging file already existing.\n')
        sys.stderr.write('Remove it before continue.\n')
        sys.stderr.write('STOP\n')
#        sys.exit()
    if config['loglevel'] == 'DEBUG':
        log_format = \
            '%(asctime)s - %(levelname)s:%(module)s:%(funcName)s -> %(message)s'
    else:
        log_format = \
            '%(asctime)s - %(levelname)s -> %(message)s'

    lg.basicConfig(filename=config['logfile'],
                   level=config['loglevel'],
                   format=log_format)

    lg.debug('Logging Initialized')


if __name__ == '__main__':
    main()
