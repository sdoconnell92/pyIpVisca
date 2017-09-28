import threading


class cl1:

    def __init__(self):
        self.ready = False

    def do_something(self):
        if self.ready:
            print("i am ready")
        else:

