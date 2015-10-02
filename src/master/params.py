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
import re
from utils import sum_is_one, check_list_len
from config import Config
import numpy as np

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-10-02"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'

config = Config().config


class Params(object):

    def __init__(self, init):

        self._plist = ['tta', 'ttb', 'cxhf', 'omega', 'cx_aa', 'cc_aa',
                       'cc_ab']
        self._acceptable_keys = self._plist +\
            [i + '_' + str(j) for i in self._plist[4:] for j in range(0, 5)]
        self._prm = dict()
        self._long_prms = re.compile(r'(\w{2}\_\w{2})(\_(\d))?')
        self._copy = False

        i = init
        for k in self._plist:
            if self._long_prms.match(k):
                self._prm[k] = [float(i + n) for n in range(0, 5)]
                i += 5
            else:
                self._prm[k] = [float(i)]
                i += 1

    def __setitem__(self, key, value):

        long_ = self._long_prms.match(key)

        if not self._copy:
            if key not in self._acceptable_keys or key == 'cxhf':
                msg = '{} is not a valid parameters key!'.format(key)
                lg.critical(msg)
                raise(KeyError(msg))

        if long_ and not long_.group(2):
            if check_list_len(value, 5, key):
                self._prm[key] = list(map(float, value))

        if long_ and long_.group(2):
            if not isinstance(value, list):
                value = [value]
            check_list_len(value, 1, key)
            self._prm[long_.group(1)][int(long_.group(3))] = float(value[0])

        if not long_:
            if not isinstance(value, list):
                value = [value]
            if check_list_len(value, 1, key):
                self._prm[key] = list(map(float, value))

        if not self._copy and long_ and long_.group(1) == 'cx_aa': self._constr()



    def _constr(self):
        if not sum_is_one(abs(self._prm['cxhf'][0]),
                          abs(self._prm['cx_aa'][0])):
            self._prm['cxhf'] = [1.0 - self._prm['cx_aa'][0]]

            if not sum_is_one(abs(self._prm['cxhf'][0]),
                              abs(self._prm['cx_aa'][0])):
                msg = 'Hartree Exchange parameters out of boundary!'
                lg.critical(msg)
                raise(ValueError(msg))


    def __getitem__(self, key):
        long_ = self._long_prms.match(key)

        if long_ and long_.group(2):
            return [self._prm[long_.group(1)][int(long_.group(3))]]
        else:
            return self._prm[key]

    def __missing__(self, key):
        msg = 'Implementation error: requested not existing parameter!'
        lg.critical(msg)
        raise(RuntimeError(msg))

    def __len__(self):
        lenght = 0
        for k in self._plist:
            lenght += len(self._prm[k])
        return lenght

    def __iter__(self):
        self._itcounter = 0
        return self

    def __next__(self):
        if self._itcounter >= len(self):
            raise StopIteration
        else:
            self._itcounter += 1
            return self.tolist()[self._itcounter - 1]

    def __str__(self):
        return self._prm.__str__()

    def tolist(self):
        list_ = []
        for k in self._plist:
            list_ += self._prm[k]
        return list_

    def __sub__(self, other):
        prm_res = Params(0)
        for k in self._plist:
            array_1 = np.array(self._prm[k])
            array_2 = np.array(other._prm[k])
            result = array_1 - array_2
            prm_res._prm[k] = result.tolist()
        return(prm_res)

    def __eq__(self, other):
        for k in self._plist:
            array_1 = np.array(self._prm[k])
            array_2 = np.array(other._prm[k])
            if not np.allclose(array_1, array_2, rtol=0.0,
                               atol=config['precision']):
                return False
        return True

    def __deepcopy__(self, memo=None):
        copy = Params(0)
        copy._copy = True
        for k, v in self._prm.items():
            copy[k] = v
        copy._copy = False
        return copy


class ParamsManager(object):

    _actual_params = Params(100)
    _old_params = Params(-100)
    _saved_params = Params(-100)

    def __init__(self):
        self._instance_params = Params(0)

    def _general_setter(self, dict_, params_obj):
        for k, v in dict_.items():
            params_obj[k] = v

    @property
    def prms(self):
        """Sets the actual parameters and write them on the right file.

        Sets the parameters taking care of the constraints and writes them,
        with the right format, on the right file.

        Args:
            dict_: (dict) contains couples parameters: value
        """
        return __class__._actual_params

    @prms.setter
    def prms(self, dict_, save=False):

        self._general_setter(dict_, __class__._actual_params)

        __class__._old_params = copy.deepcopy(__class__._actual_params)
        if save:
            __class__._saved_params = copy.deepcopy(__class__._actual_params)

        msg = ''
        with open(config['wb97x_param_file'], 'w') as pf:
            list_ = ['cxhf', 'cx_aa', 'omega', 'cc_aa', 'cc_ab']
            for k in list_:
                for i, v in enumerate(__class__._actual_params[k]):
                    msg += str(k) + str(i) + '   ' + str(v) + '\n'
            pf.write(msg)
        msg = ''
        with open(config['ddsc_param_file'], 'w') as pf2:
            list_ = ['tta', 'ttb']
            for k in list_:
                for i, v in enumerate(__class__._actual_params[k]):
                    msg += str(v) + '\n'
            pf2.write(msg)

    @prms.getter
    def prms(self, key=None):
        return __class__._actual_params

    @property
    def prms_old(self):
        return __class__._old_params

    @property
    def sprms(self):
        return self._instance_params

    @sprms.setter
    def sprms(self, kvd):
        self.general_setter(kvd, self._sparameters)

    @sprms.getter
    def sprms(self):
        return self.convert2list(self._sparameters)



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
            # print('UEG, OK')
        else:
            lg.info('UEG adjusted to sum to 1.0')
            __class__._parameters['cxhf'] = [1.0 - cx0]

            if not sum_is_one(__class__._parameters['cxhf'][0], __class__._parameters['cx_aa'][0]):
                msg = 'Hartree Exchange parameters out of boundary!'
                lg.critical(msg)
                raise(ValueError(msg))


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
        msg = ''
        with open(config['wb97x_param_file'], 'w') as pf:
            list_ = ['cxhf', 'cx_aa', 'omega', 'cc_aa', 'cc_ab']
            for k in list_:
                for i, v in enumerate(__class__._parameters[k]):
                    msg += str(k) + str(i) + '   ' + str(v) + '\n'
            pf.write(msg)
        msg = ''
        with open(config['ddsc_param_file'], 'w') as pf2:
            list_ = ['tta', 'ttb']
            for k in list_:
                for i, v in enumerate(__class__._parameters[k]):
                    msg += str(v) + '\n'
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
                        if abs(v - vh[i]) > config['precision']:
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


if __name__ == '__main__':
    from nose.tools import assert_raises

    Config.set('precision', 1E-6)
    Config.set('wb97x_param_file', './unittest_param_wb97x')
    Config.set('ddsc_param_file', './unittest_param_ddsc')



    dict_100 = {'omega': [103],
                'cx_aa': [104, 105, 106, 107, 108],
                'ttb': [101],
                'tta': [100],
                'cxhf': [102],
                'cc_ab': [114, 115, 116, 117, 118],
                'cc_aa': [109, 110, 111, 112, 113]}
    dict_9 = {'cc_aa': [18, 19, 20, 21, 22],
              'tta': [9],
              'cx_aa': [13, 14, 15, 16, 17],
              'omega': [12],
              'ttb': [10],
              'cxhf': [11],
              'cc_ab': [23, 24, 25, 26, 27]}

    print('Checking __init__:')
    assert dict_9 == Params(9)._prm, 'Creation of dictionary not working 1'
    assert dict_100 == Params(100)._prm, 'Creation of dictionary not working 2'
    print('...Done\n')

    print('Checking __setitem__:')
    dict_9['tta'] = [1]
    dict_9['cc_aa'][0] = 2
    dict_9['cx_aa'] = [0.5, 101, 102, 103, 104]
    dict_9['cxhf'] = [0.5]
    param_9 = Params(9)
    param_9['tta'] = [1]
    param_9['cc_aa_0'] = [2]
    param_9['cx_aa'] = [0.5, 101, 102, 103, 104]
    assert dict_9 == param_9._prm, 'Changing dictionary values not working 1'
    param_9['tta'] = 1
    param_9['cc_aa_0'] = 2
    assert dict_9 == param_9._prm, 'Changing dictionary values not working 2'

    def check_wrong_list_elements_number_1():
        param_9['tta'] = [1, 2]

    def check_wrong_list_elements_number_2():
        param_9['cc_aa'] = [1, 2]

    def check_wrong_list_elements_number_3():
        param_9['cc_aa'] = [1, 2, 3, 4, 5, 6]

    def check_wrong_list_elements_number_4():
        param_9['cc_aa'] = 1

    def check_wrong_list_elements_number_5():
        param_9['cc_aa_1'] = [1, 2]

    assert_raises(TypeError, check_wrong_list_elements_number_1)
    assert_raises(TypeError, check_wrong_list_elements_number_2)
    assert_raises(TypeError, check_wrong_list_elements_number_3)
    assert_raises(TypeError, check_wrong_list_elements_number_4)
    assert_raises(TypeError, check_wrong_list_elements_number_5)

    def check_wrong_constr():
        param_9['cx_aa_0'] = 2
    assert_raises(ValueError, check_wrong_constr)
    param_9['cx_aa_0'] = .8
    assert param_9['cxhf'][0] - 0.2 <= config['precision']
    print('...Done\n')

    print('Checking __getitem__:')
    assert param_9['ttb'] == [10], 'Retriving values not working 1'
    assert param_9['cc_ab'] == [23, 24, 25, 26, 27],\
        'Retriving values not working 2'
    assert param_9['cc_ab_4'] == [27], 'Retriving values not working 3'
    print('...Done\n')

    print('Checking __len__:')
    assert len(param_9) == 19, 'Wrong lenght'
    print('...Done\n')

    # Reset the parameters
    param_10 = Params(10)
    param_9 = Params(9)

    print('Checking .tolist():')
    assert param_9.tolist() == [i for i in range(9, 9 + len(param_9))]
    print('...Done\n')

    print('Checking iteretor:')
    assert [i for i in param_9] == [i for i in range(9, 9 + len(param_9))]
    print('...Done\n')

    print('Cheking __sub__:')
    assert [i for i in (param_9 - param_10)] == [-1] * len(param_10)
    assert [i for i in (param_10 - param_9)] == [1] * len(param_10)
    print('...Done\n')

    param_9a = Params(9)
    print('Checking __eq__:')
    assert param_9 == param_9a
    assert param_9 != param_10
    assert param_10 != param_9
    assert param_10 != (param_9 - param_10)
    print('...Done\n')

    print('Checking __deepcopy__:')
    param_9a = copy.deepcopy(param_9)
    assert param_9a == param_9
    param_9a['cc_ab_4'] = 1
    assert param_9['cc_ab_4'] == [27.0]
    assert param_9a['cc_ab_4'] == [1.0]
    assert id(param_9a) != id(param_9)
    param_9a = param_9
    assert id(param_9a) == id(param_9)
    print('...Done\n')

    print('\n Checking ParamsManager\n')
    print('Checking prms property')
    prm_man_1 = ParamsManager()
    params_100 = Params(100)
    assert prm_man_1.prms == params_100
    prm_man_1.prms = {'ttb': 1}
    assert prm_man_1.prms['ttb'] == [1.0]
    print('..Done')
