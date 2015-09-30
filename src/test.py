'''
Created on Sep 30, 2015

@author: petragli
'''

import sys, os
import logging as lg
from scipy.optimize import minimize
import shutil

# Easier to port
root = os.getcwd()
sys.path.append(os.path.join(root, 'src/master'))

from trset import TrainingSet, MolSet
from params import Parameters
from computation import Run

config = dict(TraininSetPath='../example/trset-tree-example/',
              TraininSetName='trset-tree-example',
              Name='test1',
              logfile='logging.log',
              loglevel='DEBUG',
              )


def main():
    prms = Parameters()

    run = Run(run_name=config['Name'], tset_path=config['TraininSetPath'])
    run.index = 'DENS-0000'
    trset = TrainingSet(config['TraininSetPath'], config['TraininSetName'])

    prms.prms = dict(tta=[13.300000190734863],
                     ttb=[1.5299999713897705],
                     cxhf=[0.157706],
                     omega=[0.3],
                     cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                     cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                     cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])

    print(prms._parameters)
    prms.optim = ['tta', 'cx_aa_0']
    x0 = [13.3, 0.5]
    print(prms.optim)

    print(trset.optimizer(x0, 'full', 'MAE'))
    print(trset.optimizer(x0, 'func', 'MAE'))


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
