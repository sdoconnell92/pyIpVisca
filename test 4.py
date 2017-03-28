import multiprocessing as mp

from multiprocessing import Process
import os
import time

def info(title):
    print(title)
    print('module name:', __name__)
    if hasattr(os, 'getppid'):  # only available on Unix
        print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name):
    info('function f')
    print('hello', name)
    idx = 1
    while True:
        print(idx)
        idx += 1
        time.sleep(1)

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
