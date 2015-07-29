#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Project:  wb97xdDsC-optim
# FileName: mproc
# Creation: Jul 22, 2015
#

import multiprocessing
import multiprocessing.pool

# Try determining the version from git:
try:
    import subprocess
    git_v = subprocess.check_output(['git', 'describe'],
                                    stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    git_v = 'Not Yet Tagged!'


__author__ = 'Riccardo Petraglia'
__credits__ = ['Riccardo Petraglia']
__updated__ = "2015-07-29"
__license__ = 'GPLv2'
__version__ = git_v
__maintainer__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__status__ = 'development'


class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


if __name__ == '__main__':

    import time
    from random import randint

    def sleepwhile(t):
        print("Sleeping %i seconds..." % t)
        time.sleep(t)
        return t

    def work(num_procs):
        print("Creating %i (daemon) workers and jobs in child." % num_procs)
        pool = multiprocessing.Pool(num_procs)

        result = pool.map(sleepwhile,
                          [randint(1, 5) for x in range(num_procs)])
        pool.close()
        pool.join()
        return result

    def test():
        print("Creating 5 (non-daemon) workers and jobs in main process.")
        pool = MyPool(5)
        result = pool.map(work, [randint(1, 5) for x in range(5)])
        pool.close()
        pool.join()
        print(result)

    test()
