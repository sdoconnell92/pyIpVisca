import threading
import time

class class1:

    def __init__(self):
        self.ready = False

    def wait_for_true(self):
        while True:
            if self.ready:
                print("ready!")


class class2:

    def __init__(self, cl11):
        self.cl1 = cl11

    def make_true(self):
        for i1 in range(0, 10):
            print('loop: ' + str(i1))
            if i1 == 8:
                self.cl1.ready = True
            time.sleep(1)


if __name__ == '__main__':
    cl1 = class1()
    cl2 = class2(cl1)
    p = threading.Thread(target=cl1.wait_for_true, args=())
    c = threading.Thread(target=cl2.make_true, args=())
    p.start()
    c.start()
