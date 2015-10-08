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
__updated__ = "2015-10-05"
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
        self._acceptable_keys = self._plist + \
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
            if key == 'cxhf':
                msg = 'Warning: You are using cxhf instead of cx_aa_1.\n'\
                    'IGNORE this message if settings default params'
                lg.warning(msg)

            if key not in self._acceptable_keys:
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

        if not self._copy and long_ and \
            long_.group(1) == 'cx_aa': self._constr()

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

        if not isinstance(key, str):
            msg = '{} is not a string type'.format(key)
            lg.critical(msg)
            raise(TypeError(msg))

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
        with open(config['wb97x_params_writing'], 'w') as pf:
            list_ = ['cxhf', 'cx_aa', 'omega', 'cc_aa', 'cc_ab']
            for k in list_:
                for i, v in enumerate(__class__._actual_params[k]):
                    msg += str(k) + str(i) + '   ' + str(v) + '\n'
            pf.write(msg)
        msg = ''
        with open(config['ddsc_params_writing'], 'w') as pf2:
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
    def prms_saved(self):
        return __class__._saved_params

    @property
    def sprms(self):
        return self._instance_params

    @sprms.setter
    def sprms(self, dict_):
        self._general_setter(dict_, self._instance_params)

    @sprms.getter
    def sprms(self):
        return self._instance_params

    def check_prms(self):
        return __class__._actual_params == self._instance_params

    def check_saved(self):
        return __class__._saved_params == self._actual_params

    def refresh(self):
        """Copy the class parameter to the instantiated ones.

        After calling refresh the validity test will be true.

        Note: Consider to put this method at the end of the check_prms method
        """
        self._instance_params = copy.deepcopy(__class__._actual_params)

    def save(self):
        __class__._saved_params = copy.deepcopy(__class__._actual_params)


class Optim(object):

    _to_optimize = []

    def __init__(self, list_):
        __class__._to_optimize = list_

    def __len__(self):
        return len(__class__._to_optimize)

    def __getitem__(self, key):

        if not isinstance(key, int):
            msg = '{} is not an integer type'.format(key)
            lg.critical(msg)
            raise(TypeError(msg))

        return __class__._to_optimize[key]

    def __setitem__(self, key, value):
        raise(NotImplementedError)

        if not isinstance(key, int):
            msg = '{} is not an integer type'.format(key)
            lg.critical(msg)
            raise(TypeError(msg))

        __class__._to_optimize[key] = value

    def __str__(self):
        return __class__._to_optimize.__str__()

    def set_prms(self, params):
        dict_ = {}
        if len(params) != len(self):
            msg = 'Parameters number do not corresponds'
            lg.critical(msg)
            raise(RuntimeError(msg))

        for i, p in enumerate(__class__._to_optimize):
            dict_[p] = params[i]
        ParamsManager().prms = dict_


if __name__ == '__main__':
    from nose.tools import assert_raises

    Config.set('precision', 1E-6)
    Config.set('wb97x_params_writing', 'unittest_param_wb97x')
    Config.set('ddsc_params_writing', 'unittest_param_ddsc')

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
    assert param_9['cc_ab'] == [23, 24, 25, 26, 27], \
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
    print('..Done\n')

    print('Checking sprms property')
    prm_man_1 = ParamsManager()
    params_0 = Params(0)
    assert prm_man_1.sprms == params_0
    prm_man_1.sprms = {'ttb': 1}
    assert prm_man_1.sprms['ttb'] == [1.0]
    print('..Done\n')

    print('Checking prms_saved property')
    assert prm_man_1.check_saved == False
    assert prm_man_1.prms != prm_man_1.prms_saved
    prm_man_1.save()
    assert prm_man_1.prms == prm_man_1.prms_saved
    prm_man_2 = ParamsManager()
    assert prm_man_2.prms == prm_man_1.prms_saved
    print('...Done\n')

    print('Checking prms_old property')
    tpar = copy.deepcopy(prm_man_1.prms)
    prm_man_1.prms['tta'] = 1000
    assert prm_man_1.prms_old == tpar
    assert prm_man_1.prms != tpar
    print('...Done\n')

    print('\n Checking Optim Class')
    print('Check creation\n')
    optim = Optim(['tta', 'ttb'])
    assert optim._to_optimize == ['tta', 'ttb']
    optim.set_prms([1, 2])
    prm_man_1 = ParamsManager()
    assert prm_man_1._actual_params['tta'] == [1.0]
    assert prm_man_1._actual_params['ttb'] == [2.0]
    print('...Done')
