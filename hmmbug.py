import multiprocessing


class testclass:

    def __init__(self):
        self.var = None
        p = multiprocessing.Process(target=self.afunction)
        p.start

    def afunction(self):
        print("afunctionstuff")

    def anotherfunction(self, q1):
        print("anotherfunction")



if __name__ == "__main__":
    things = testclass