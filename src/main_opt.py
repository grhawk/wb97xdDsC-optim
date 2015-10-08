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
from params import ParamsManager, Optim
from computation import Run

Presets().alberto_lcmd30()
config = Config().config

start_time = time.time()

def main():
    init_logging()
    prms = ParamsManager()
    i=0
#    while not prms.check_saved():
    while True:
#       print("Not all Parameters Converged!")
#       print(list(map(str,prms._actual_params)))
       print("BIG GAMESS computation number: "+str(i)) 
       run = Run(run_name=config['run_name'],
                 tset_path=config['training_set_path'])
       run.index = 'DENS-'+str(i)
       trset = TrainingSet(config['training_set_path'],
                           config['training_set_file'])

       prms.prms = dict(tta=[13.300000190734863],
                        ttb=[1.5299999713897705],
                        cxhf=[0.157706],
                        omega=[0.3],
                        cx_aa=[0.842294, 0.726479, 1.04760, -5.70635, 13.2794],
                        cc_aa=[1.000000, -4.33879, 18.2308, -31.7430, 17.2901],
                        cc_ab=[1.000000, 2.37031, -11.3995, 6.58405, -3.78132])

#       optim = Optim(['tta', 'ttb'])
       optim = Optim(['tta', 'ttb', 'cx_aa_0','cx_aa_1','cx_aa_2','cx_aa_3','cc_aa_1','cc_aa_2','c_aa_3','cc_ab_1','cc_ab_2','cc_ab_3'])
       
#       x0_ = [13.3, 1.53]
       with open('/home/afabrizi/wb97xddsc/TMP_DATA/FUNC_PAR.dat','r') as f2:
          OldParams = [line.rstrip('\n') for line in f2]
       print("Old Parameters", OldParams)

       with open('/dev/shm/afabrizi/TMP_DATA/x0','r') as f1:
          x0_ = [line.rstrip('\n') for line in f1]

#       bnds=((None,None),(None,None))
       bnds=((None,None),(None,None),(0,1),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None),(None,None))

       def compute_error(params, trset, optim, kind, error_type):

          optim.set_prms(params)

          if error_type == 'MAE':
              minim = trset.compute_MAE(kind)
          print('PAR: '+" ".join(list(map(str,params)))+' MAE: '+str(minim))
          return minim                 

       print(compute_error(x0_, trset, optim, 'full', 'MAE'))

       def printer(xc):
          print('END of STEP')
          with open('/dev/shm/afabrizi/TMP_DATA/x0','w') as f:
             for s in xc:
                f.write(str(s) + '\n')
          print(xc)

       
       i+=1
       OptRes=minimize(compute_error,x0_,args=(trset,optim,'func','MAE'), method='L-BFGS-B', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-2,'maxiter':100000,'ftol':1e-4})
#       OptRes=minimize(compute_error,x0_,args=(trset,optim,'func','MAE'), method='L-BFGS-B', bounds=bnds, callback=printer, options={'disp': True,'gtol': 1e-2,'maxiter':10000,'ftol':1e-4,'eps':1e-1})
       print(OptRes)
       print("Time for this density: %s seconds ---" % (time.time() - start_time))

       folder = '/dev/shm/afabrizi/tmp_density_dir/'
       for the_file in os.listdir(folder):
          file_path = os.path.join(folder, the_file)
          try:
             if os.path.isfile(file_path):
                os.remove(the_file)
          except:
             pass       

        
       shutil.copy('/dev/shm/afabrizi/TMP_DATA/FUNC_PAR.dat', '/home/afabrizi/wb97xddsc/TMP_DATA/FUNC_PAR.dat')
       shutil.copy('/dev/shm/afabrizi/TMP_DATA/a0b0', '/home/afabrizi/wb97xddsc/TMP_DATA/a0b0')
 
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
