#!/home/petragli/Software/anaconda3/bin/python3


import sys, os
import logging as lg
from scipy.optimize import minimize

# Easier to port
home = os.path.expanduser("~")
sys.path.append(os.path.join(home, 'wb97xddsc/wb97xdDsC-optim/src/master'))

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
    init_logging()
    # init computation
    prms = Parameters()
    run = Run(run_name=config['Name'], tset_path=config['TraininSetPath'])
    run.index = 'DENS-0000'
    trset = TrainingSet(config['TraininSetPath'], config['TraininSetName'])
    # MolSet.p_call_mol_energy('full')
    # print('NEEDEDMOL:',list(map(lambda x: x.id,trset.container[0].container[0].needed_mol)))
    # print('UNIENERGY:',list(map(lambda x: x.uni_energy,trset.container[0].container[0].needed_mol)))
    # print('FULLENERGY:',list(map(lambda x: x.full_energy,trset.container[0].container[0].needed_mol)))
    # print('FUNCENERGY:',list(map(lambda x: x.func_energy,trset.container[0].container[0].needed_mol)))
#    sys.exit()
    # MolSet.p_call_mol_energy('func')
    # for mol in MolSet.container:
    #     print(mol.myprm_full.sprms)
    #     print(mol.myprm_func.sprms)


    prms.prms = dict(tta=[13.300000190734863],
                       ttb=[1.5299999713897705],
                       cxhf=[0.157706],
                       omega=[0.3],
                       cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                       cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                       cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])



    prms.optim = ['tta', 'cx_aa_0']
    x0_=[13.30000, 0.8400]

    trset.optimizer(x0_,'full','MAE')
#    print(minimize(trset.optimizer,x0_,args=('func','MAE'),method='BFGS', options={'maxiter':1}))
    # for i in range(10):
    #     trset.optimizer(x0_[:1] + [x0_[1]+float(i)/10.]+ [x0_[2]-float(i)/10.],'func','MAE')
    run.index = 'DENS-0001'
    trset.optimizer([13,0.5],'func','MAE')
    
    # all_x = []
    # all_l = []
    # with open('asd', 'r') as f:
    #     for l in f:
    #         if l.find('PAR:') > -1:
    #             x = l.split()[2:4]
    #             try:
    #                 x = [float(x[0]), float(x[1][:-1])]
    #             except:
    #                 pass
    #             all_x.append(x)
    #             all_l.append(l)    


    # i = 1
    # trset.optimizer([13. ,0.8],'func','MAE')
    # print(all_l[i])

                    
def printer(xc):
    print('END of STEP', xc)



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
