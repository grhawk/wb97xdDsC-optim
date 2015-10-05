#!/home/petragli/Software/anaconda3/bin/python3


import sys
import os
import logging as lg
from scipy.optimize import minimize
import shutil
import time

# Easier to port
home = os.path.expanduser("~")
sys.path.append(os.path.join(home, 'wb97xddsc/wb97xdDsC-optim/src/master'))

from config import Config, Presets
from trset import TrainingSet, MolSet
from params import Parameters
from computation import Run

Presets().Alberto()
config = Config().config

start_time = time.time()

def main():
    init_logging()
    prms = Parameters()
    i=0
    while True:
       index='DENS-'+str(i)
       print("BIG GAMESS computation number: ", index)

       run=Run(run_name=config['run_name'],
               tset_path=config['training_set_path'])
       run.index = index
       trset = TrainingSet(config['training_set_path'],
                           config['training_set_file'])

       prms.prms = dict(tta=[13.300000190734863],
                        ttb=[1.5299999713897705],
                        cxhf=[0.157706],
                        omega=[0.3],
                        cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                        cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                        cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])


       prms.optim = ['tta', 'cx_aa_0','cx_aa_1','cx_aa_2','cx_aa_3','cc_aa_1','cc_aa_2','cc_aa_3','cc_ab_1','cc_ab_2','cc_ab_3','ttb']
       print(prms.optim)

       with open('/home/afabrizi/wb97xddsc/TMP_DATA/FUNC_PAR.dat','r') as f2:
          OldParams = [line.rstrip('\n') for line in f2]
       print("Old Parameters", OldParams)

       with open('/scratch/TMP_DATA/x0','r') as f1:
          x0_ = [line.rstrip('\n') for line in f1]

       def printer(xc):
          print('END of STEP')
          with open('/scratch/TMP_DATA/x0','w') as f:
             for s in xc:
                f.write(str(s) + '\n')
          print(xc)

       bnds=((None,None),(0,1),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None))
       print(trset.optimizer(x0_,'full','MAE'))
#TNC GOOD       print(minimize(trset.optimizer,x0_,args=('func','MAE'), method='TNC', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-2, 'maxiter':10000}))
       i+=1
       print(minimize(trset.optimizer,x0_,args=('func','MAE'), method='L-BFGS-B', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-2,'maxiter':10000,'ftol':1e-4}))
       print("Time for this density: %s seconds ---" % (time.time() - start_time))

       folder = '/dev/shm/tmp_density_dir/'
       for the_file in os.listdir(folder):
          file_path = os.path.join(folder, the_file)
          try:
             if os.path.isfile(file_path):
                os.remove(the_file)
          except:
             pass

       with open('/home/afabrizi/wb97xddsc/TMP_DATA/FUNC_PAR.dat','r') as f3:
          NewParams = [line.rstrip('\n') for line in f3]
       print("New Parameters", NewParams)

       if all(x in OldParams for x in NewParams):
          print("Total time: %s seconds ---" % (time.time() - start_time))
          break
       else:
          print("Not all parameters converged.")
          pass

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
