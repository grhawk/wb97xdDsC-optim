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
import sys
import copy

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-21"
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
        return self.random_noise_result()
        if self.blacklisted: self.blacklisted_error()
        enrgs = []
        for mol in self.needed_mol:
            enrgs.append(mol.fulldft_energy())
        return self._apply_rule(enrgs)

    def func_energy(self):
        return self.random_noise_result()
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

    def random_noise_result(self):
        import random
        return self.ref_ener + random.uniform(-1, 1)

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
        self.container = []
        self.path = os.path.abspath(path)
        self.name = None
        self.id = None
        self.blacklist = []  # Will contains system object
        self.fulldftlist = []
        self.MAE = None
        self.RMSE = None
        self.MRE = None

    def get_blacklist(self):
        tmp = []
        for s in self.blacklist:
            tmp.append(s)
        return tmp

    def get_fulldftlist(self):
        tmp = []
        for s in self.fulldftlist:
            tmp.append(s)
        return tmp

    def compute_MAE(self):
        self.MAE = 0.0
        for el in self.container:
            self.MAE += el.compute_MAE()
        self.MAE = self.MAE / len(self.container)
        return self.MAE

    def compute_RMSE(self):
        raise(NotImplementedError)

    def compute_MRE(self):
        raise(NotImplementedError)

    def compute_all_errors(self):
        self.compute_MAE()
        self.compute_MRE()
        self.compute_RMSE()

    def get_by_name(self, name):
        for el in self.container:
            if name.strip() == el.name:
                return el
        msg = 'System ++{}++ not found!'.format(name.strip())
        lg.warning(msg)
        return None

    def __str__(self):
        return 'obj-' + self.name

    def flush_list(self, file, list_to_save):
        listp = os.path.join(self.path, file)
        with open(listp, 'w') as listf:
            try:
                listf.write('\n'.join(map(lambda x: x.name, list_to_save)))
            except AttributeError:
                listf.write('\n'.join(list_to_save))


class DataSet(Set):
    """Here all the container are called with only a number and is obvious that
        the number has to be inside the DATASET directory """

    def __init__(self, path):
        lg.debug('Initializing DataSet from {}'.format(path))
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
            self.container.append(System(line, self.path))
        lg.debug("""DataSet Information:
         * Name: {NAME:s}
         * ID: {ID:s}
         * Path: {PATH:s}
         """.format(NAME=self.name, ID=self.id, PATH=self.path))

    def name_conversion(self, system):
        return self.id + '.' + str(system).split('.')[1]

    def __str__(self, *args, **kwargs):
        return Set.__str__(self, *args, **kwargs)

    def _add_to_list(self, name_list, black_or_fulldft):
        tmp = []
        for name in name_list:
            obj = self.get_by_name(name)
            tmp.append(obj)
        tmp = [x for x in tmp if x is not None]
        if black_or_fulldft == 'black':
            for obj in tmp:
                obj.set_black()
            self.blacklist = copy.deepcopy(tmp)
            self.flush_list('blacklist.dat', self.blacklist)
        elif black_or_fulldft == 'fulldft':
            for obj in tmp:
                obj.set_fulldft()
            self.fulldftlist = copy.deepcopy(tmp)
            self.flush_list('fulldftlist.dat', self.fulldftlist)
        else:
            lg.critical('Critical error in implementation!')
            sys.exit()

    def add_to_fulldftlist(self, name_list):
        self._add_to_list(name_list, 'fulldft')

    def add_to_blacklist(self, name_list):
        self._add_to_list(name_list, 'black')


class TrainingSet(Set):

    def __init__(self, path, file):
        super().__init__(path)
        self.name = file[:-4]
        self.filep = os.path.join(self.path, file.strip())
        self._set_creator()

    def name_conversion(self, name):
        """Return a tuple with dataset and system number.

        """
        if len(name.split('.')) == 2:
            return tuple(name.split('.'))
        else:
            msg = """Name {} has a wrong syntax:
                     Should be DATSET.SYSTEM""".format(name)
            lg.error(msg)
            return None

    def _set_creator(self):
        self.id = self.name
        self._blacklistp = os.path.join(self.path, self.name + '-blacklist.dat')
        self._fulldftlistp = os.path.join(self.path, self.name + '-fulldftlist.dat')
        with open(self.filep, 'r') as filec:
            for line in filec:
                if line.split()[0][0] == '#':
                    continue
                dsetp = os.path.join(self.path, line.strip())
                self.container.append(DataSet(dsetp))
        self.read_allist()

    def _read_list(self, listp):
        readlist = []
        if os.path.isfile(listp):
            with open(listp, 'r') as listf:
                for line in listf:
                    if line.split()[0][0] != '#':
                        readlist.append(line.strip())
        return readlist

    def read_allist(self):
        self.add_to_blacklist(self._read_list(self._blacklistp))
        self.add_to_fulldftlist(self._read_list(self._fulldftlistp))

    def _add_to_list(self, name_list, black_or_fulldft):
        tmp = {}
        uncoded_name_list = list(map(self.name_conversion, name_list))
        uncoded_name_list = [x for x in uncoded_name_list if x is not None]
        for name in uncoded_name_list:
            if name not in tmp:
                tmp[name[0]] = []
            tmp[name[0]].append(name[1])

        for dset, systems in tmp.items():
            obj = self.get_by_name(dset)
            if obj == None:
                continue
            if black_or_fulldft == 'black':
                obj.add_to_blacklist(systems)
                self.blacklist = name_list
                self.flush_list(self._blacklistp, self.blacklist)
            elif black_or_fulldft == 'fulldft':
                obj.add_to_fulldftlist(systems)
                self.fulldftlist = name_list
                self.flush_list(self._fulldftlistp, self.fulldftlist)
            else:
                lg.critical('Critical error in implementation!')
                sys.exit()

    def add_to_fulldftlist(self, name_list):
        self._add_to_list(name_list, 'fulldft')

    def add_to_blacklist(self, name_list):
        self._add_to_list(name_list, 'black')
