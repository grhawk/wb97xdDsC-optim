#!/home/petragli/Software/anaconda3/bin/python3


import sys, os
import logging as lg

sys.path.append('/home/petragli/wb97xddsc/gamess-opt/wb97xdDsC-optim/src/master')

from trset import TrainingSet, MolSet
from computation import Run

config = dict(TraininSetPath = '../example/trset-tree-example/',
              TraininSetName = 'trset-tree-example',
              Name = 'test1',
              logfile = 'logging.log',
              loglevel = 'DEBUG',
              
              )

def main():
    init_logging()
    #init computation
    Run(run_name=config['Name'], tset_path=config['TraininSetPath']).index='DENS-0000'
    trset = TrainingSet(config['TraininSetPath'], config['TraininSetName'])
#    print(trset.container[0].container[0].p_compute_MAE('full'))
#    print(trset.container[0].container[0].p_compute_MAE('func'))
    # trset.container[0].p_compute_MAE('full')
    # print(trset.container[0].MAE)
    # trset.container[0].p_compute_MAE('func')
    # print(trset.container[0].MAE)
    # trset.p_compute_MAE('full')
    # print(trset.MAE)
    # trset.p_compute_MAE('func')
    # print(trset.MAE)
    #    print(trset.compute_MAE('fulldft'))
    # print(MolSet.container)
    # print(MolSet.container[0] is MolSet.to_compute[0])
    # print(MolSet.to_compute[0].myprm_full.sprms)
    # print(MolSet.to_compute[1].myprm_full.sprms)
    # MolSet.to_compute[0].myprm_full.refresh()
    # print(MolSet.container[0] is MolSet.to_compute[0])
    # print(MolSet.container[0].myprm_full.sprms)
    # print(MolSet.to_compute[1].myprm_full.sprms)
    # print(MolSet.container[0].id,MolSet.container[0].myprm_full.sprms)
    # print(MolSet.to_compute[0].id,MolSet.to_compute[0].myprm_full.sprms, MolSet.to_compute[0].full_energy)
    # print(MolSet.to_compute[1].id,MolSet.to_compute[1].myprm_full.sprms)
    # print(MolSet.to_compute[0].id,MolSet.to_compute[0].myprm_full.sprms)
    MolSet.p_call_mol_energy('full')
    for mol in MolSet.container:
        print(mol.myprm_full.sprms)
#        print('FULL ENERGY',mol.full_energy)
#    print(MolSet.container[0].full_energy)
#    print(trset.compute_MAE('full'))


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
