#!/home/petragli/Software/anaconda3/bin/python3


import sys, os
import logging as lg

sys.path.append('/home/petragli/wb97xddsc/gamess-opt/wb97xdDsC-optim/src/master')

from trset import TrainingSet

config = dict(TraininSetPath = '../example/trset-tree-example/',
              TraininSetName = 'trset-tree-example',
              logfile = 'logging.log',
              loglevel = 'DEBUG',
              )

def main():
    init_logging()
    trset = TrainingSet(config['TraininSetPath'], config['TraininSetName'])
    print(trset.compute_MAE('func'))


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
