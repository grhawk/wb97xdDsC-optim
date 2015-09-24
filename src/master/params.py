#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: params
# Creation: Jul 16, 2015
#

"""Implements everything on the parameters and take care of the param files.

"""


import logging as lg
import copy
import os
import re
from utils import sum_is_one
import sys

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-09-07"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'

home = os.path.expanduser("~")
config = dict(Precision=1E-18,
              ParamFile=os.path.join(home, 'wb97xddsc/TMP_DATA/FUNC_PAR.dat'),
	      dDsCParamFile=os.path.join(home, 'wb97xddsc/TMP_DATA/a0b0'))


class Parameters(object):

    _parameters = dict(tta=[100],
                       ttb=[101],
                       cxhf=[102],
                       omega=[103],
                       cx_aa=[104, 105, 106, 107, 108],
                       cc_aa=[109, 111, 112, 113, 114],
                       cc_ab=[115, 116, 117, 118, 119])

    _parameters_old = dict(tta=[100],
                           ttb=[101],
                           cxhf=[102],
                           omega=[103],
                           cx_aa=[104, 105, 106, 107, 108],
                           cc_aa=[109, 111, 112, 113, 114],
                           cc_ab=[115, 116, 117, 118, 119])

    _to_optimize = []

    def __init__(self):
        self._sparameters = copy.deepcopy(__class__._parameters)
        self.sprms = {'tta' : [1]}

    def _constr(self):
        cx = __class__._parameters['cxhf'][0]
        cx0 = __class__._parameters['cx_aa'][0]
        if sum_is_one(cx, cx0):
            pass
            #print('UEG, OK')
        else:
            print('UEG, wrong. ALPHAC will be changed.')
            __class__._parameters['cxhf']=[1.0-cx0]
            if not sum_is_one(__class__._parameters['cxhf'][0], __class__._parameters['cx_aa'][0]):
                msg = 'Hartree Exchange parameters out of boundary!'
                lg.critical(msg)
                print(msg)
                sys.exit()

    @property
    def optim(self):
        return __class__._to_optimize

    @optim.setter
    def optim(self, list_):
        # possible_parameters = list(__class__._parameters.keys())
        # to_add = ['cx_aa', 'cc_aa', 'cc_ab']
        # tmp = []
        # for p in possible_parameters:
        #     if p in to_add:
        #         for i in range(0, 5):
        #             tmp.append('{}_{:1d}'.format(p, int(i)))
        # for p in to_add:
        #     possible_parameters.remove(p)
        # possible_parameters += tmp

        # tmp = copy.deepcopy(__class__._parameters)

        # for k, v in dict_.items():
        #     if k not in possible_parameters:
        #         msg = 'Parameter {} cannot be used!'.format(k)
        #         lg.error(msg)
        #         raise TypeError(msg)
        #     __class__._to_optimize.append(k)

        #     try:
        #         if int(k[-1]) < 5 and int(k[-1]) > -1:
        #             tmp[k[:-2]][int(k[-1])] = float(v)
        #     except ValueError:
        #         pass

        #     tmp[k] = [float(v)]
        __class__._to_optimize = list_

        # self.prms = copy.deepcopy(tmp)

    @optim.getter
    def optim(self):
        return __class__._to_optimize

    @property
    def prms(self):
        return __class__._parameters

    @prms.setter
    def prms(self, kvd):
        """Sets all the class parameters and write them on the right file.

        Sets the parameters taking care of the constraints.

        Args:
            kvd (list or dict): can be a dictionary with parameters: value or a
                list with all the parameters

        """
        __class__._parameters_old = copy.deepcopy(__class__._parameters)
        self.general_setter(kvd, __class__._parameters)
        # Decidere quali dei parametri "legati" vogliamo poter cambiare
        # e cambiare l'altro di conseguenza. Se viene cambiato l'altro (ovvero
        # il valore passato per l'altro parametro e' diverso da None) allora
        # raise un warning. Poi settare i parametri in modo che siano sempre
        # consistenti e scriverli nel giusto file con la giusta formattazione!
        self._constr()
        msg=''
        with open(config['ParamFile'], 'w') as pf:
            list_=['cxhf','cx_aa','omega','cc_aa','cc_ab']
            for k in list_:
                for i, v in enumerate(__class__._parameters[k]):
#                    print(k,i,v)
                    msg += str(k)+str(i)+'   '+str(v)+'\n'
            pf.write(msg)
        msg=''
        with open(config['dDsCParamFile'], 'w') as pf2:
            list_=['tta','ttb']
            for k in list_:
                for i, v in enumerate(__class__._parameters[k]):
#                    print(k,i,v)
                    msg += str(v)+'\n'
            pf2.write(msg)
            

    @prms.getter
    def prms(self):
        return self.convert2list(__class__._parameters)

    @property
    def prms_old(self):
        return __class__._parameters_old

    @prms_old.getter
    def prms_old(self):
        return self.convert2list(__class__._parameters_old)

    @property
    def sprms(self):
        return self._sparameters

    @sprms.setter
    def sprms(self, kvd):
        self.general_setter(kvd, self._sparameters)

    @sprms.getter
    def sprms(self):
        return self.convert2list(self._sparameters)

    def general_setter(self, kvd, prms):
        if isinstance(kvd, list):
            if len(kvd) != 19:
                msg = 'The list must contains 19 elements!'
                lg.critical(msg)
                raise IndexError(msg)
            self.convert2dict(kvd, prms)

        if isinstance(kvd, dict):
            expand_params = re.compile(r'\w{2}\_\w{2}\_\d')
            expanded_selection = False
            for k in kvd.keys():
                if expand_params.match(k):
                    # print(expand_params.match(k))
                    expanded_selection = True
                    break

            if expanded_selection:
                dict_ = kvd
                possible_parameters = list(__class__._parameters.keys())
                to_add = ['cx_aa', 'cc_aa', 'cc_ab']
                tmp = []
                for p in possible_parameters:
                    if p in to_add:
                        for i in range(0, 5):
                            tmp.append('{}_{:1d}'.format(p, int(i)))
                for p in to_add:
                    possible_parameters.remove(p)
                possible_parameters += tmp

#                print(possible_parameters)
                
                tmp = copy.deepcopy(__class__._parameters)

                for k, v in dict_.items():
                    if k not in possible_parameters:
                        msg = 'Parameter {} cannot be used!'.format(k)
                        lg.error(msg)
                        raise TypeError(msg)
                    
#                    __class__._to_optimize.append(k)

                    try:
                        if int(k[-1]) < 5 and int(k[-1]) > -1:
                            tmp[k[:-2]][int(k[-1])] = float(v)
                    except ValueError:
                        tmp[k] = [float(v)]

                __class__._parameters = copy.deepcopy(tmp)
                
            else:
                for k in kvd.keys():
                    if k in prms.keys():
                        if len(kvd[k]) == len(prms[k]):
                            prms[k] = kvd[k]
                        else:
                            msg = 'The number of parameters specified does not\
                            match the expected number'
                            lg.error(msg)
                    else:
                        msg = 'The dict contains keys not present in the parameters\
                        dict. Those will be ignored.'
                        lg.error(msg)

    def convert2dict(self, list_, to_dict):
        keys = sorted(list(to_dict.keys()))
        l = 0
        for i, k in enumerate(keys):
            i += l
            if k[2] == '_':
                to_dict[k] = list_[i:i + 5]
                l += 4
            else:
                to_dict[k] = [list_[i]]

    def convert2list(self, dict_):
        list_ = []
        for k, v in sorted(dict_.items()):
            list_ += v
        del(k)
        return list_

    def get(self):
        """Return a dictionary with parameter: value.

        """
        pass

    def check_prms(self):
        return self._compare(__class__._parameters, self._sparameters)[0]

    def check_old(self):
        return self._compare(__class__._parameters, __class__._parameters_old)

    def _compare(self, prm1, prm2):
        """Check if the instantiated parameters are the same as the class one.

        This method should be used to check if a new computation is actually
        needed.

        """
        compare = True
        parameters_differences = {}
        for k, vh in prm1.items():
            if k in prm2:
                vs = prm2[k]
                if len(vs) == len(vh):
                    tmp = []
                    for i, v in enumerate(vs):
                        tmp.append(v - vh[i])
                        if abs(v - vh[i]) > config['Precision']:
                            compare = False
                    parameters_differences[k] = tmp
                else:
                    msg = 'Implementation error!'
                    lg.critical(msg)
                    raise RuntimeError(msg)
            else:
                    msg = 'Implementation error!'
                    lg.critical(msg)
                    raise RuntimeError(msg)
        return (compare, parameters_differences)

    def refresh(self):
        """Copy the class parameter to the instantiated ones.

        After calling refresh the validity test will be true.

        Note: Consider to put this method at the end of the check_prms method
        """
        self._sparameters = copy.deepcopy(__class__._parameters)
