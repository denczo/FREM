from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import numpy as np

from tools import current_trigon_wf


class PlotterApp(App):

    def build(self):
        return MainGrid()


class MainGrid(BoxLayout):

    def __init__(self):
        global canvas
        super(MainGrid, self).__init__()
        canvas = FigureCanvasKivyAgg(plt.gcf(), size_hint=(1, 0.5), pos_hint={'top': 1})
        self.ids.plot.add_widget(canvas)
        self.chunk_size = 3000
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.label = 'Sine'
        self.update_plot()

    def switch_wf(self, label):
        self.label = label
        self.update_plot()

    def update_plot(self):
        plt.gcf()
        # label, a, fm, x, c, lfo=0
        plot_y = current_trigon_wf(self.label, 0.5, self.ids.slider.value, self.plot_x, 0.5)
        plt.cla()
        plt.plot(self.plot_x, plot_y)
        plt.yticks([0, 1])
        canvas.draw()


PlotterApp().run()
