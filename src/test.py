#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: main
# Creation: Jul 15, 2015
#

'''
Created on Sep 30, 2015

@author: petragli
'''

import sys
import os
import logging as lg
# Easier to port
home = os.path.expanduser("~")
root = os.path.join(home, 'MyCodes/wb97xdDsC-optim')  # path to wb97xdDsC-optim
sys.path.append(os.path.join(root, 'src/master'))

from config import Config, Presets
from trset import TrainingSet, MolSet
from params import ParamsManager, Optim
from computation import Run

Presets().test()
config = Config().config


def main():
    prms = ParamsManager()

    run = Run(run_name=config['run_name'],
              tset_path=config['training_set_path'])
    run.index = 'DENS-0000'
    trset = TrainingSet(config['training_set_path'],
                        config['training_set_file'])

    prms.prms = dict(tta=[13.300000190734863],
                     ttb=[1.5299999713897705],
                     cxhf=[0.157706],
                     omega=[0.3],
                     cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                     cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                     cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])

    print(prms.prms)
    optim = Optim(['tta', 'cx_aa_0'])
    x0 = [13.3, 0.5]
    print(optim)

    print(compute_error(trset, optim, x0, 'full', 'MAE'))
    print(compute_error(trset, optim, x0, 'func', 'MAE'))


def compute_error(trset, optim, params, kind, error_type):

    optim.set_prms(params)

    if error_type == 'MAE':
        minim = trset.compute_MAE(kind)
    return minim

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
    init_logging()
    main()
