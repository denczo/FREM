from multiprocessing import Process
import time

def helper(x):
    return x.f(2)

class A:
    def f(self, x):
        print("Process", multiprocessing.current_process().pid)
        return x * x

    def test_function(self, name):
        print("PROCESS ",name)
        print(name, "COUNTDOWN IN")
        for i in range(5):
            time.sleep(0.5)
            print(name, i)
        print(name, "BOOM")

    def test(self):
        process = Process(target=self.test_function, args=('Master',))
        process2 = Process(target=self.test_function, args=("Slave",))
        process3 = Process(target=self.test_function, args=("Padawan",))
        process.start()
        process2.start()
        process3.start()
        process.join()
        process2.join()
        process3.join()
        #with multiprocessing.Pool(processes=3) as pool:
            #print("HAKUNA MATATA")
            #test = [A()]
            #print (pool.map(helper, [A]*3))
            #pool.map()
            #pass


a = A()
a.test()