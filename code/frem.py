from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import numpy as np
from kivy.clock import Clock

from tools import *


class FremApp(App):

    def build(self):
        # Clock.schedule_interval(lambda dt: print("FPS: ", Clock.get_fps()), 1)
        return MainGrid()


colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
]


class MainGrid(BoxLayout):

    def __init__(self, wf_amp='Sine', wf_mod='Triangle', wf_car='Sine'):
        super(MainGrid, self).__init__()
        self._wf_amp = wf_amp
        self._wf_mod = wf_mod
        self._wf_car = wf_car
        self._int_active = False
        self._amp_active = False
        self._mod_active = True
        self._car_active = False
        self._current_tab = None
        self.beta = 0.1

        self.fig = plt.figure(facecolor='#212946')
        self.ax = self.fig.add_subplot(111)
        self.plot = FigureCanvasKivyAgg(self.fig)

        self.chunk_size = 5000
        self.amp_y = np.zeros(self.chunk_size)
        self.mod_y = np.zeros(self.chunk_size)
        self.car_y = np.zeros(self.chunk_size)

        self.ids.modulation.add_widget(self.plot)
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)
        self.formula = ''
        self.update_plot()

    @property
    def wf_amp(self):
        return self._wf_amp

    @wf_amp.setter
    def wf_amp(self, value):
        self._wf_amp = value

    @property
    def wf_mod(self):
        return self._wf_mod

    @wf_mod.setter
    def wf_mod(self, value):
        self._wf_mod = value

    @property
    def wf_car(self):
        return self._wf_car

    @wf_car.setter
    def wf_car(self, value):
        self._wf_car = value

    @property
    def int_active(self):
        return self._int_active

    @int_active.setter
    def int_active(self, value):
        self._int_active = value

    @property
    def amp_active(self):
        return self._amp_active

    @amp_active.setter
    def amp_active(self, value):
        self._amp_active = value

    @property
    def mod_active(self):
        return self._mod_active

    @mod_active.setter
    def mod_active(self, value):
        self._mod_active = value

    @property
    def car_active(self):
        return self._car_active

    @car_active.setter
    def car_active(self, value):
        self._car_active = value

    @property
    def current_tab(self):
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        self._current_tab = value


    def modulating_wave(self):

        if 'AM':
            pass



    def update_plot(self):

        self._current_tab = 'FM Signal'

        if self._current_tab == 'AM Signal':
            pass
        elif self._current_tab == 'FM Signal':
            self.formula = current_equation(self.wf_mod, 'Trigonometric function')
        elif self._current_tab == 'Carrier \nSignal':
            self.formula = current_equation(self.wf_car, 'Trigonometric function')

        mod_wave = 0

        if self._int_active:
            # constant c need to be 0 for integral
            self.mod_y = current_trigon_wf(self.wf_mod, 0.5, self.ids.freq_mod.value, self.plot_x, 0)
            self.mod_y = running_sum(self.mod_y, 0)
            self.mod_y = normalize(self.mod_y)
            mod_wave = self.mod_y * (self.ids.mod_index.value / self.ids.freq_car.value)
        else:
            self.mod_y = current_trigon_wf(self.wf_mod, 0.5, self.ids.freq_mod.value, self.plot_x, 0.5)

        self.car_y = current_trigon_wf(self.wf_car, 0.5, self.ids.freq_car.value, self.plot_x, 0.5, mod_wave)

        mod_color = '#08F7FE'
        amp_color = '#FE53BB'
        car_color = '#00ff41'
        symbol = 'f(x)'
        if self.int_active:
            symbol = 'F(x)'
            self.formula = r'$\int$ ' + self.formula
            mod_color = '#F5D300'

        plt.setp(self.ax.spines.values(), linewidth=3, color='grey', alpha=0.2)
        self.ax.cla()

        if self._amp_active:
            pass

        if self._car_active:
            self.plot_graph(self.ax, self.plot_x, self.car_y, car_color)

        if self._mod_active:
            self.plot_graph(self.ax, self.plot_x, self.mod_y, mod_color)
            self.ax.annotate(symbol, xy=(0.02, 0.93), xycoords='axes fraction',
                          fontsize=8, color=mod_color, bbox=dict(boxstyle="round", fc='black', ec='None', alpha=0.4))

        self.ax.tick_params(left=False, bottom=False, labelbottom=False, labelleft=False)
        self.ax.set_facecolor('#212946')

        self.ax.annotate(self.formula, xy=(0.5, -0.26), xycoords='axes fraction',
                         fontsize=9, color=mod_color, bbox=dict(boxstyle="round", fc='black', ec="None", alpha=0.2),
                         ha='center',
                         va='center')

        plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.3)
        plt.grid(color='grey', alpha=0.2)
        self.plot.draw()

    @staticmethod
    def plot_graph(ax, x, y, color):
        ax.plot(x, y, linewidth=1.5, alpha=1, color=color)
        # glow effect
        ax.plot(x, y, linewidth=6, alpha=0.1, color=color)


FremApp().run()
