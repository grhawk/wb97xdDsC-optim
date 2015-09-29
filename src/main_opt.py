#!/home/petragli/Software/anaconda3/bin/python3


import sys, os
import logging as lg
from scipy.optimize import minimize
import shutil

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
    prms = Parameters()

    for i in range(0,1):
       indice='DENS-'+str(i)
       print("ALBERTOOOOOO", indice)
#      try:
#         del(run)
#      except:
#         pass

       run=Run(run_name=config['Name'], tset_path=config['TraininSetPath']).index = indice 
       trset = TrainingSet(config['TraininSetPath'], config['TraininSetName'])
 
       prms.prms = dict(tta=[13.300000190734863],
                        ttb=[1.5299999713897705],
                        cxhf=[0.157706],
                        omega=[0.3],
                        cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                        cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                        cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])



       print(prms._parameters)
#    prms.prms = {'cx_aa_0': 0.5, 'cc_aa_2':12000, 'tta':100}
#    print(trset.compute_MAE('full'))
#    print(prms._parameters)
       prms.optim = ['tta', 'cx_aa_0','cx_aa_1','cx_aa_2','cx_aa_3']
#       prms.optim = ['tta', 'cx_aa_0','cx_aa_1','cx_aa_2','cx_aa_3','cc_aa_1','cc_aa_2','cc_aa_3','cc_ab_1','cc_ab_2','cc_ab_3']
       print(prms.optim)
       with open('/scratch/TMP_DATA/x0','r') as f1:
          x0_ = [line.rstrip('\n') for line in f1] 

       def printer(xc):
          print('END of STEP')
          print(xc)
       bnds=((None,None),(0,1),(None,None),(None,None),(None,None))
# good for final       bnds=((None,None),(0,1),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None))
       print(trset.optimizer(x0_,'full','MAE'))
       print(minimize(trset.optimizer,x0_,args=('func','MAE'), method='TNC', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-11,'maxiter':1}))
# possible choice       print(minimize(trset.optimizer,x0_,args=('func','MAE'), method='L-BFGS-B', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-2,'maxiter':1 }))
#       shutil.copy('/scratch/TMP_DATA/FUNC_PAR.dat', '/home/afabrizi/wb97xddsc/TMP_DATA/FUNC_PAR.dat')
#       shutil.copy('/scratch/TMP_DATA/a0b0', '/home/afabrizi/wb97xddsc/TMP_DATA/a0b0')

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
