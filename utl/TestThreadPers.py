import threading
import time


class ThreadClass:

    def __init__(self):
        self.thr = threading.Thread(target=self.start(), timeout=5)

    def start(self):

        while True:
            print('Thread Running')
            time.sleep(2)


if __name__ == '__main__':

    cl1 = ThreadClass()
    cl1.thr.join()
