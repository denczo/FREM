from kivy import Config
Config.set('graphics', 'multisamples', '0')
import os
# os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.config import Config
import multiprocessing

class MyApp(App):

    def tower_of_hanoi(self, n, from_rod, to_rod, aux_rod):
        if n == 0:
            return
        self.tower_of_hanoi(n-1, from_rod, aux_rod, to_rod)
        print("Move disk", n, "from rod", from_rod, "to rod", to_rod)
        self.tower_of_hanoi(n-1, aux_rod, to_rod, from_rod)


    def worker(self):
        N = 20
        self.tower_of_hanoi(N, 'A', 'C', 'B')


    def build(self):
        self.p = multiprocessing.Process(target=self.worker)
        self.p.start()
        return Label(text="Tech With Me")

if __name__== "__main__":
    MyApp().run()