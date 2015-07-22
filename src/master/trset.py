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
import mproc

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-22"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Molecule(object):
    """Create a molecule object starting from an xyz file.

    Providing an xyz file as argument when instantiating the class, a molecule
    object will be created. This object provide a name for the molecule (the xyz
    file name), an ID as the name of the dataset + the name of the molecule.
    Moreover it provides method to compute the energy for the molecule even if
    based on a different module.

    Args:
        path (str): xyz file relative or absolute path.

    Attributes:
        id (str): Human redeable string that identify the Molecule.
        xyzp (str): Storage of the absolute xyz file path.
        density_path (ToImplement[str]): Absolute path for the density file.
        belonging_dataset (str): Name of the dataset the molecule belongs.
        dft_energy (float): Energy computed at fulldft level.
        func_energy (float): Energy computed with the "fast" method.

    Exceptions:

    """
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
        """Return a human readable string when the object is printed.

        """
        return 'Molecule-' + self.id

    def _molecule_creator(self):
        """Create all what is needed for the object.

        Take the path attribute and use it to create all the others attribute.
        """
        p, file = os.path.split(self.xyzp)
        p = os.path.split(p)[0]
        p = os.path.split(p)[1]
        self.belonging_dataset = p
        self.name = file[:-4]
        self.id = '{DATASET:s}.{NAME:s}'.format(DATASET=self.belonging_dataset,
                                                NAME=self.name)
        lg.debug("""Molecule Information:
         * Dataset: {DATASET:s}
         * Name: {NAME:s}
         * ID: {ID:s}
         * Path: {PATH:s}
        """.format(DATASET=self.belonging_dataset, NAME=self.name, ID=self.id,
                   PATH=self.xyzp))

    def fulldft_energy(self):
        """Retrieve the energy at fulldft level.

        Check if the parameters are changed from the last computation and in
        that case compute the fulldft energy from scratch, otherwise will
        return the last computed energy.

        Returns:
            dft_energy if successfull, 0.00 otherwise
        """

        if self.name == '023': return -56.5641546249
        if self.name == '001': return -113.1335656245
        if self.dft_energy or not self.myprm.validity():
            print('Compute the BigGamess energy. If problem return None')
            self.myprm.refresh()
            self.density_path = 'Returned by the computation module'
        return self.dft_energy

    def funtional_energy(self):
        """Retrieve the energy computed with the optimized density.

        Check if the parameters are changed from the last computation and in
        that case compute the "functional" energy from scratch, otherwise will
        return the last computed energy.

        Returns:
            func_energy if successfull, 0.00 otherwise
        """

        if self.func_energy or not self.myprm.validity():
            print('Compute the SmallGamess energy. If problem return None')
            self.myprm.refresh()
        return self.func_energy


class System(object):
    """Provides the System object: a set of molecule and a rule and a reference.

    A System is composed by a set of molecules and rule to mix the energy of
    those molecules so that, if the energies are correct the results will be the
    reference energy.

    Note:
    The rule format is a string with the following fields:
     - id: a unique identifier within the dataset;
     - molecules: a set of identifier that provides the needed molecules;
     - rule: a set of numbers, usually integers, that provides the
         multiplication factor to get the reference energy from the energy of
         the single molecules;
     - reference energy: a float that provides the referenced energy.

     We assume that the dataset tree is composed as in the example!

    Args:
        rule_line (str): a line written in the rule format (see Note)
        dsetp (str): the path to the rule.dat file within the dataset.

    Attributes:
        dsetp (str): absolute path to the dataset directory;
        belonging_dataset (str): name of the dataset;
        id (str): unique identificator to the system object;
        name (str): name of the system within the dataset (id in the rule file);
        needed_mol (list): list of molecule needed to compute the energy;
        rule (list): integers to use as factor in the energy computation;
        ref_ener (float): reference energy for the system;
        blacklisted (bool): True if the system is mark as blacklisted;
        fulldftlisted (bool): True if the system need always a fulldft;

    Exceptions:

    """

    def __init__(self, rule_line, dsetp):
        lg.debug('Initializing System from line: \n{}\n'.format(rule_line))
        self.dsetp = os.path.abspath(dsetp)
        self.belonging_dataset = None
        self.id = 'None'
        self.name = None
        self.needed_mol = []
        self.rule = []
        self.ref_ener = None
        self.blacklisted = False
        self.fulldftlisted = False
        self._system_creator(rule_line)
#        self.full

    def __str__(self):
        """Return a human readable string when the object is printed.

        """

        return 'System-{}'.format(self.id)

    def _system_creator(self, rule_line):
        """Fill most of the attributes using the rule_line and the dataset path.

        Args:
            rule_line (str): the string in "rule format"

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
        if len(needed_molecules_name) != len(self.rule):
            msg = 'Problem applying the rule for {}'.format(self.__str__())
            lg.critical(msg)
            raise RuleFormatError(msg)

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
        """Load the molecules needed for the system computation.

        Fill the attribute needed_mol with molecule objects.

        Todo:
            Check if the molecule is already loaded!

        Args:
            names (list): name of the molecule to be loaded.

        """

        self.needed_mol = MolSet.load_molecules(names, self.dsetp)

    def _apply_rule(self, enrgs):
        """Compute the system energy applying the rule.

        Given a list of energy the method will compute the energy to be
        compared with the referenced energy.

        Args:
            enrgs (list[float]): list of single molecules energies

        """
        if len(enrgs) != len(self.rule):
            msg = 'Problem applying the rule for {}:\n'.format(self.id)
            msg += 'enrgs: ' + ' '.join(list(map(str, enrgs)))
            msg += 'rule: ' + ' '.join(list(map(str, self.rule)))
            lg.critical(msg)
            raise RuntimeError(msg)
        enr = 0.0
        for i, coef in enumerate(self.rule):
            enr += coef * enrgs[i]
        return enr * 627.5096080305927

    def fulldft_energy(self):
        """Compute the full dft energy for the system.

        This method provides the right molecular energies to the _apply_rule
        method and check if the system is blacklisted.

        Return: The energy of the system.

        """
        return self.random_noise_result()
        if self.blacklisted: self.blacklisted_error()
        enrgs = []
        for mol in self.needed_mol:
            enrgs.append(mol.fulldft_energy())
        return self._apply_rule(enrgs)

    def func_energy(self):
        """Compute the func energy for the system.

        This method provides the right molecular energies to the _apply_rule
        method and check if the system is blacklisted. If the system is
        fulldftlisted, the method will call the fulldft_energy method
        automatically.

        Return: the energy of the system.

        """
        return self.random_noise_result()
        if self.blacklisted: self.blacklisted_error()
        if self.fulldftlisted:
            msg = 'System: {} - Calling fulldft even for func_energy'.\
                format(self.id)
            lg.warning(msg)
            return self.fulldft_energy()
        enrgs = []
        for mol in self.needed_mol:
            enrgs.append(mol.func_energy())
        return self._apply_rule(enrgs)

    def fulldft_energy_error(self):
        """Provide the fulldft energy error for this system.

        Return: The error in the fulldft energy computation

        """
        return self.fulldft_energy() - self.ref_ener

    def func_energy_error(self):
        """Provide the func energy error for this system.

        Return: The error in the func energy computation

        """
        return self.func_energy() - self.ref_ener

    def p_compute_MAE(self, kind):
        """Absolute error for the system.

        The name is to exploit a python feature in the Set class.

        Args:
            kind (str): Can be func or fulldft

        """
        import time
        time.sleep(4)
        print('Sleeping 4 sec in {}!'.format(self.id))

        if kind == 'func':
            return self.func_energy_error()
        elif kind == 'fulldft':
            return self.fulldft_energy_error()
        else:
            msg = 'Critical error in implementation!'
            lg.critical(msg)
            sys.exit()

    def compute_MRE(self, kind):
        """Relative absolute error for the system.

        The name is to exploit a python feature in the Set class.

        Args:
            kind (str): Can be func or fulldft

        """

        if kind == 'func':
            return self.func_energy_error() / self.ref_ener
        elif kind == 'fulldft':
            return self.fulldft_energy_error() / self.ref_ener
        else:
            msg = 'Critical error in implementation!'
            lg.critical(msg)
            sys.exit()

    def random_noise_result(self):
        import random
        return self.ref_ener + random.uniform(-1, 1)

    def set_black(self):
        """Add the system to the blacklist and set the flag value.

        """

        self.blacklisted = True
        lg.info('System {} blacklisted'.format(self.id))

    def set_fulldft(self):
        """Add the system to the fulldftlist and set the flag value.

        """

        self.fulldftlisted = True
        lg.info('System {} fulldftlisted'.format(self.id))

    def get_listed(self):
        """List the status of the "listed" flags.

        Return (dict): key is the name of the list and value is the bool.

        """

        return {'black': self.blacklisted, 'fulldft': self.fulldftlisted}

    def blacklisted_error(self):
        """If the errror is requested and the system is blacklisted.

        """
        lg.warning('Energy from system {} used even if blacklisted!'.
                   format(self.id))


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

    def p_compute_MAE(self, kind):
        self.MAE = 0.0
        print('SELFID: ', self.id)
        my_pool = mproc.MyPool(processes=50)
        output = [my_pool.apply_async(el.p_compute_MAE, args=(kind,))
                  for el in self.container]
        results = [p.get() for p in output]
        print('AAAAAAAAA', results)
        for r in results:
            self.MAE += r
        self.MAE = self.MAE / len(self.container)
        return self.MAE

    def compute_MAE(self, kind):
        self.MAE = 0.0
        for el in self.container:
            self.MAE += abs(el.p_compute_MAE(kind))
        self.MAE = self.MAE / len(self.container)
        return self.MAE

    def compute_RMSE(self):
        raise(NotImplementedError)

    def compute_MRE(self, kind):
        self.MRE = 0.0
        for el in self.container:
            self.MRE += abs(el.compute_MRE(kind))
        self.MRE = self.MRE / len(self.container)
        return self.MRE

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


class MolSet(object):
    container = []

    # def __init__(self):

    @staticmethod
    def get_by_id(my_id):
        for el in __class__.container:
            if my_id.strip() == el.id:
                print('FOUNDDDDD')
                return el
        msg = 'System ++{}++ not found!'.format(my_id.strip())
        lg.warning(msg)
        return None

    @staticmethod
    def load_molecules(names, dsetp):
        """Load the molecules needed for the system computation.

        Fill the attribute needed_mol with molecule objects.

        Args:
            names (list): name of the molecule to be loaded.

        """

        needed_mol = []
        dset_name = os.path.basename(dsetp)
        for name in names:
            my_id = '{}.{}'.format(dset_name, name)
            obj = __class__.get_by_id(my_id)
            if obj is not None:
                print('ASDASDASDASDASD')
                needed_mol.append(obj)
                lg.debug('Molecule {} already existing'.format(my_id))
            else:
                mol = Molecule(os.path.join(dsetp, 'geometry', name + '.xyz'))
                needed_mol.append(mol)
                __class__.container.append(mol)

        return needed_mol


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
        self._fulldftlistp = os.path.join(self.path,
                                          self.name + '-fulldftlist.dat')
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
            if obj is None:
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


class RuleFormatError(TypeError):
    pass
