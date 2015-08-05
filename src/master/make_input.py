#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: make_input
# Creation: Jul 14, 2015
#

"""Building Gamess input file for single point.

Building Gamess input file for single point used in the wb97x-dDsC optimization.
The input will be created reading an xyz file where the comment line contains
the charge and multiplicity.

"""

import utils as uts
import re
import logging as lg


# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-15"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class Input(object):
    def __init__(self, filep):
        uts.file_exists(filep)
        self.config = dict(basis_set='6-31G')

        self.atoms = []
        self.x = []
        self.y = []
        self.z = []
        self.charge = ''
        self.multiplicity = ''
        self.title = ''

        self._template()

        self._basis_set_conversion(self.config['basis_set'])
        self._read_xyz(filep)

    def _basis_set_conversion(self, name):
        pople_reg = re.compile(r'([36])\-([23]1\d?)G(\*?\*?)')
        matching_pople = pople_reg.match(name)
        if matching_pople:
            self.gamess['BASIS']['GBASIS'] = 'N' + str(matching_pople.group(2))
            self.gamess['BASIS']['NGAUSS'] = str(matching_pople.group(1))
            if matching_pople.group(3):
                lg_msg = 'Polarized pople basis function not defined'
                lg.critical(lg_msg)
                raise(NotImplementedError(lg_msg))
        else:
            lg_msg = 'Basis function not implemented in the script'
            lg.critical(lg_msg)
            raise(NotImplementedError(lg_msg))

    def _read_xyz(self, filep):
        with open(filep, 'r') as xyzf:
            xyzf.readline()
            self.charge, self.multiplicity = xyzf.readline().split()
            for line in xyzf:
                if len(line.split()) == 4:
                    line = line.strip()
                    atom, xt, yt, zt = line.split()
                    self.atoms.append(atom)
                    self.x.append(xt)
                    self.y.append(yt)
                    self.z.append(zt)
                elif (len(line.split()) > 0):
                    lg_msg = '{} is not an xyz file'.format(filep)
                    lg.critical(lg_msg)
                    raise(TypeError(lg_msg))
                else:
                    break

    def _building_data(self):
        self.gamess['DATA'] = [' ' + self.title, ' C1']
        for i, atom in enumerate(self.atoms):
            txt = ' {:3s} {:6.2f} {:12.6f} {:12.6f} {:12.6f}'.format(atom,
                    float(atnum(atom)), float(self.x[i]), float(self.y[i]),
                    float(self.z[i]))
            self.gamess['DATA'].append(txt)

    def write(self, filep):
        self._building_data()
        txt = ''
        for kw in self.gamess:
            txt += ' $' + kw + ' '
            if kw == 'DATA':
                txt += '\n'
                txt += '\n'.join(self.gamess['DATA'])
                txt += '\n $END\n'
                continue
            for k, v in self.gamess[kw].items():
                txt += str(k) + '=' + str(v) + ' '
            txt += '$END\n'

        with open(filep, 'w') as outfp:
            outfp.write(txt)

    def _template(self):
        self.gamess = {'BASIS': dict(GBASIS='',
                                     NGAUSS=''),
                       'CONTRL': dict(EXETYP='RUN',
                                      SCFTYP='ROHF',
                                      RUNTYP='ENERGY',
                                      DFTTYP='wB97X',
                                      MAXIT='200',),
                       'DATA': [],
                       'DFT': dict(DDSC='.t.'),
                       'SYSTEM': dict(MWORDS='8')}


def atnum(atom_label):
    at_num = dict(O=8,
                  H=1,
                  C=6,
                  S=16,
                  N=7,
                  Al=13,
                  Cl=17,
                  F=9,
                  B=5,
                  Be=4,
                  Si=14,
                  Li=3,
                  Na=11,
                  P=15)
    if not (atom_label in at_num):
        lg_msg = 'Number of electons not defined for {}.'.format(atom_label)
        lg.critical(lg_msg)
        raise(NotImplementedError(lg_msg))

    return at_num[atom_label]


if __name__ == '__main__':

    def test_read_xyz():
        print('**** Testing read_xyz ****')
        xyzc = """3
        0 1
        O 0. 0. 0.
        H 0. 0. 1.
        H 0. .7 .4
        """
        with open('test.xyz', 'w') as testxyz:
            testxyz.write(xyzc)
        newinput = Input('test.xyz')
        print(newinput.atoms)
        if newinput.atoms == ['O', 'H', 'H']:
            print('  ** Test Passed **  ')
        return newinput

    def test_building_data():
        newinput = test_read_xyz()
        newinput.write('asd.inp')

    tests = [test_read_xyz, test_building_data]
    for test in tests:
        test()
