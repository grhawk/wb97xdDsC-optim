#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: trset
# Creation: Jul 16, 2015
#

"""Implements all the objects regarding the training set.

"""

import params

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-16"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Molecule(object):

    def __init__(self, path):
        self.id = None  # If none there is some problem!
        self.xyzpath = path
        self.density_path = None
        self.myprm = params.Parameters()
        self.dft_energy = None
        self.func_energy = None
        pass

    def _id_creator(self):
        """Create the id using the path.

        """
        self.name = 'DATASET-MOLNUMBER'
        self.id = 'Molecule number'  # It is obvious to which dataset belongs
        pass

    def density_optim(self):
        if self.dft_energy or not self.myprm.validity():
            print('Compute the BigGamess energy. If problem return None')
            self.myprm.refresh()
            self.density_path = 'Returned by the computation module'
        pass

    def funtional_energy(self):
        if self.func_energy or not self.myprm.validity():
            print('Compute the SmallGamess energy. If problem return None')
            self.myprm.refresh()
        pass


class System(object):

    def __init__(self, rule_line):
        self.id = 'Number'
        self.needed_mol = []
        self.rule = []
        self.ref_ener = None
        self.blacklisted = False
        self.fulldftlisted = False
        self._compile_system()
        pass

    def _compile_system(self):
        """Fill the id, needed_mol and rule fields. Remember that needed_mol
            has to be a list of molecule obj

        """
        pass

    def fulldft_energy(self):
        print("If blacklisted and called return some error")
        pass

    def func_energy(self):
        print("If blacklisted and called return some error")
        print("If fulldftlisted call directly fulldft_energy")
        pass

    def set_blacklist(self):
        self.blacklisted = True

    def set_fulldftlist(self):
        self.fulldftlisted = True

    def get_listed(self):
        return {'black': self.blacklisted, 'fulldft': self.fulldftlisted}

class Set(object):

    def __init__(self, path):
        self.path = path
        self.name = None
        self.blacklist = []  # Will contains system object
        self.fulldftlist = []
        self.MAE = None
        self.RMSE = None
        self.MRE = None
        pass

    def _compile_dataset(self):
        print('Set self.name and read the lists')
        self.read_blacklist()
        self.read_fulldftlist()
        pass

    def add_to_blacklist(self, system_list):
        raise(NotImplementedError)

    def add_to_fulldftlist(self, system_list):
        raise(NotImplementedError)

    def read_blacklist(self):
        raise(NotImplementedError)

    def read_fulldftlist(self):
        raise(NotImplementedError)

    def get_blacklist(self):
        raise(NotImplementedError)

    def get_fulldftlist(self):
        raise(NotImplementedError)

    def compute_MAE(self):
        raise(NotImplementedError)

    def compute_RMSE(self):
        raise(NotImplementedError)

    def compute_MRE(self):
        raise(NotImplementedError)

    def compute_all_errors(self):
        self.compute_MAE()
        self.compute_MRE()
        self.compute_RMSE()

class DataSet(Set):
    """Here all the systems are called with only a number and is obvious that
        the number has to be inside the DATASET directory """

    def __init__(self, path):
        self.systems = []
        super().__init__(path)


    def name_conversion(self, system):
        print('Return the name as DATASET-NUMBER of a given system')
        pass

    def read_blacklist(self):
        print('Readed from self.path/blacklist')
        pass

    def read_fulldftlist(self):
        print('Readed from self.path/fulldftlist')
        pass

    def get_blacklist(self):
        tmp = []
        for s in self.blacklist:
            tmp.append(self.name_conversion(s))
        return tmp

    def get_fulldftlist(self):
        tmp = []
        for s in self.fulldftlist:
            tmp.append(self.name_conversion(s))
        return tmp


class TrainingSet(Set):

    def __init__(self, path):
        self.datasets = []
        super().__init__(path)

    def name_conversion(self, name):
        """Return a tuple with dataset and system number.

        """
        pass

    def _compile_dataset(self):
        print('Set self.name and read the lists')
        self.read_blacklist()
        self.read_fulldftlist()
        pass

    def add_to_blacklist(self, systems_list):
        for s in systems_list:
            system, number = self.name_conversion(systems_list)
            system.add_to_blacklist(number)
        pass

    def add_to_fulldftlist(self, systems_list):
        for s in systems_list:
            system, number = self.name_conversion(systems_list)
            system.add_to_fulldftlist(number)
        pass

    def read_blacklist(self):
        raise(NotImplementedError)

    def read_fulldftlist(self):
        raise(NotImplementedError)

    def get_blacklist(self):
        raise(NotImplementedError)

    def get_fulldftlist(self):
        raise(NotImplementedError)
