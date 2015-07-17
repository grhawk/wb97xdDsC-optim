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
import logging as lg
import os
import math
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
__updated__ = "2015-07-17"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Molecule(object):

    def __init__(self, path):
        lg.debug('Importing Molecule from \n{}\n'.format(path))
        self.id = None  # If none there is some problem!
        self.xyzp = os.path.abspath(path)
        self.density_path = None
        self.belonging_dataset = None
        self.myprm = params.Parameters()
        self.dft_energy = None
        self.func_energy = None
        self._molecule_creator()

    def __str__(self):
        return 'Molecule-' + self.id

    def _molecule_creator(self):
        """Create the id using the path.

        """
        p, file = os.path.split(self.xyzp)
        p = os.path.split(p)[0]
        p = os.path.split(p)[1]
        self.belonging_dataset = p
        self.name = file[:-4]
        self.id = '{DATASET:s}-{NAME:s}'.format(DATASET=self.belonging_dataset,
                                                NAME=self.name)
        lg.debug("""Molecule Information:
         * Dataset: {DATASET:s}
         * Name: {NAME:s}
         * ID: {ID:s}
         * Path: {PATH:s}
        """.format(DATASET=self.belonging_dataset, NAME=self.name, ID=self.id,
                   PATH=self.xyzp))

    def fulldft_energy(self):
        if self.name == '023': return -56.5641546249
        if self.name == '001': return -113.1335656245
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

    def __init__(self, rule_line, dsetp):
        lg.debug('Initializing System from line: \n{}\n'.format(rule_line))
        self.dsetp = dsetp
        self.belonging_dataset = None
        self.id = 'None'
        self.name = None
        self.needed_mol = []
        self.rule = []
        self.ref_ener = None
        self.blacklisted = False
        self.fulldftlisted = False
        self._system_creator(rule_line)

    def __str__(self):
        return 'System-{}'.format(self.id)

    def _system_creator(self, rule_line):
        """Fill the id, needed_mol and rule fields. Remember that needed_mol
            has to be a list of molecule obj

        """
        self.belonging_dataset = os.path.basename(self.dsetp)
        data = rule_line.split()
        self.name = data[0]
        self.id = '{}.{}'.format(self.belonging_dataset, self.name)
        nmol = (len(data) - 2) / 2
        needed_molecules_name = data[1:int(nmol + 1)]
        self._load_molecules(needed_molecules_name)
        self.rule = list(map(int, data[int(nmol + 1):-1]))
        self.ref_ener = float(data[-1])

        lg.debug("""System Information:
         * Dataset: {DATASET:2}
         * Name: {NAME:s}
         * Needed Mol: {NEEDMOL:s}
         * Rule: {RULE:s}
         * Reference Energy: {REFENR:6.3f}
         * Blacklisted: {BLACK:s}
         * Fulldft: {FULLDFT:s}
         * Path: {PATH:s}
        """.format(NAME=str(self.name), DATASET=str(self.belonging_dataset),
                   NEEDMOL=' '.join(map(str, self.needed_mol)),
                   BLACK=str(self.blacklisted),
                   FULLDFT=str(self.fulldftlisted),
                   RULE=' '.join(map(str, self.rule)),
                   REFENR=self.ref_ener, PATH=self.dsetp))

    def _load_molecules(self, names):
        for name in names:
            mol = Molecule(os.path.join(self.dsetp, 'geometry', name + '.xyz'))
            self.needed_mol.append(mol)

    def _apply_rule(self, enrgs):
        if len(enrgs) != len(self.rule):
            lg.critical('Number of coefficient and number of retrieved energies does not corresponds!')
            sys.exit()
        enr = 0.0
        for i, coef in enumerate(self.rule):
            enr += coef * enrgs[i]
        return enr * 627.5096080305927

    def fulldft_energy(self):
        if self.blacklisted: self.blacklisted_error()
        enrgs = []
        for mol in self.needed_mol:
            enrgs.append(mol.fulldft_energy())
        return self._apply_rule(enrgs)

    def func_energy(self):
        if self.blacklisted: self.blacklisted_error()
        if self.fulldftlisted:
            lg.debug('System: {} - Calling fulldft even for func_energy').format(self.id)
            return self.fulldft_energy()
        enrgs = []
        for mol in self.needed_mol:
            enrgs.append(mol.func_energy())
        return self._apply_rule(enrgs)

    def fulldft_energy_error(self):
        return self.fulldft_energy() - self.ref_ener

    def func_energy_error(self):
        return self.func_energy() - self.ref_ener

    def debug_error(self):
        import random
        return random.random()

    def set_black(self):
        self.blacklisted = True
        lg.info('System {} blacklisted'.format(self.id))

    def set_fulldft(self):
        self.fulldftlisted = True
        lg.info('System {} fulldftlisted'.format(self.id))

    def get_listed(self):
        return {'black': self.blacklisted, 'fulldft': self.fulldftlisted}

    def blacklisted_error(self):
        lg.warning('Energy from system {} used even if blacklisted!'.format(self.id))


class Set(object):

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.name = None
        self.id = None
        self.blacklist = []  # Will contains system object
        self.fulldftlist = []
        self.MAE = None
        self.RMSE = None
        self.MRE = None

    def _set_creator(self):
        print('Set self.name and read the lists')
        self.read_blacklist()
        self.read_fulldftlist()

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
        lg.debug('Initializing DataSet from {}'.format(path))
        self.systems = []
        super().__init__(path)
        self._set_creator()

    def _set_creator(self):
        self.name = os.path.basename(self.path)
        self.id = self.name
        with open(os.path.join(self.path, 'rule.dat')) as rulef:
            rulec = rulef.readlines()
        for line in rulec:
            if line.split()[0][0] == '#':
                continue
            self.systems.append(System(line, self.path))
        super()._set_creator()
        lg.debug("""DataSet Information:
         * Name: {NAME:s}
         * ID: {ID:s}
         * Path: {PATH:s}
         """.format(NAME=self.name, ID=self.id, PATH=self.path))


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
