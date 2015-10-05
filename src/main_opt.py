#!/home/petragli/Software/anaconda3/bin/python3


import sys
import os
import logging as lg
from scipy.optimize import minimize
import shutil

# Easier to port
home = os.path.expanduser("~")
sys.path.append(os.path.join(home, 'wb97xddsc/wb97xdDsC-optim/src/master'))

from config import Config, Presets
from trset import TrainingSet, MolSet
from params import ParamsManager, Optim
from computation import Run

Presets().riccardo_lcmdlc2()
config = Config().config

optim = Optim(['tta', 'cx_aa_0'])


def main():
    init_logging()
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

    print(prms._parameters)
    x0 = [13.3, 0.5]
    print(optim)

    sys.exit()

    print(compute_error(x0, 'full', 'MAE'))


def printer(xc):
    print('END of STEP')
    print(xc)


def compute_error(params, kind, error_type):

    optim.set_prms(params)

    if error_type == 'MAE':
        minim = TrainingSet().compute_MAE(kind)
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
    main()
