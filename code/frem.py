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


class CarrierWave:
    def __init__(self, color, chunk_size=5000, waveform='Sine'):
        self._waveform = waveform
        self.chunk_size = chunk_size
        self._graph_active = False
        self._frequency = 1
        self._x = np.linspace(0, 1, chunk_size)
        self._y = 0
        self.formula = ''
        self.render_wf()
        self.render_equation()
        self.color = color

    @property
    def waveform(self):
        return self._waveform

    @waveform.setter
    def waveform(self, value):
        self._waveform = value

    @property
    def graph_active(self):
        return self._graph_active

    @graph_active.setter
    def graph_active(self, value):
        self._graph_active = value

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        self._frequency = value

    @property
    def y(self):
        return self._y

    def render_wf(self, m=0, c=0):
        #print(isinstance(self, ModulationWave))
        # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
        self._y = current_trigon_wf(self._waveform, 0.5, self.frequency, self._x, c, m)

    def render_equation(self):
        return current_equation(self._waveform, 'Trigonometric function')


class ModulationWave(CarrierWave):
    def __init__(self, color):
        super().__init__(color)
        self._int_active = False
        self._mod_index = 0.1
        self.graph_active = True

    @property
    def int_active(self):
        return self._int_active

    @int_active.setter
    def int_active(self, value):
        self._int_active = value

    @property
    def mod_index(self):
        return self._mod_index

    @mod_index.setter
    def mod_index(self, value):
        self._mod_index = value / self.frequency

    def apply_modulation(self, status):
        if status:
            return self.render_wf()
        else:
            return 0


class MainGrid(BoxLayout):

    def __init__(self, wf_amp='Sine', wf_mod='Triangle', wf_car='Sine'):
        super(MainGrid, self).__init__()
        self.mod_wave_1 = ModulationWave('#08F7FE')
        self.mod_wave_2 = ModulationWave('#FE53BB')
        self.carrier = CarrierWave('#00ff41')
        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]

        self._current_tab = 'WF_M1'

        self.fig = plt.figure(facecolor='#212946')
        self.ax = self.fig.add_subplot(111)
        self.plot = FigureCanvasKivyAgg(self.fig)

        self.chunk_size = 5000
        self.ids.modulation.add_widget(self.plot)
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)
        self.formula = ''
        self.update_plot()

    @property
    def current_tab(self):
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        self._current_tab = value

    def update_equation(self):
        if self._current_tab == 'WF_M1':
            self.formula = self.mod_wave_1.render_equation()
        elif self._current_tab == 'WF_M2':
            self.formula = self.mod_wave_2.render_equation()
        elif self._current_tab == 'WF_C':
            self.formula = self.carrier.render_equation()

    def update_plot(self):

        plt.setp(self.ax.spines.values(), linewidth=3, color='grey', alpha=0.2)
        self.ax.cla()

        self.update_equation()

        mod_wave = 0
        for i in range(len(self.waveforms)):
            wf = self.waveforms[i]
            wf_y = wf.y
            if isinstance(wf, ModulationWave):
                if wf.int_active:
                    # constant c need to be 0 for integral
                    wf.render_wf(m=mod_wave, c=0)
                    wf_y = wf.y
                    wf_y = running_sum(wf_y, 0)
                    wf_y = normalize(wf_y)
                else:
                    wf.render_wf(0, c=0.5)
                    wf_y = wf.y
                mod_wave = wf_y * wf.mod_index
            else:
                wf.render_wf(m=mod_wave, c=0.5)

            if wf.graph_active:
                self.plot_graph(self.ax, self.plot_x, wf_y, wf.color)


        mod_color = '#08F7FE'
        amp_color = '#FE53BB'
        car_color = '#00ff41'
        symbol = 'f(x)'
        # if self.int_active:
        #     symbol = 'F(x)'
        #     self.formula = r'$\int$ ' + self.formula
        #     mod_color = '#F5D300'

        # if self._car_active:
        #     self.plot_graph(self.ax, self.plot_x, self.car_y, car_color)
        #
        # if self._mod_active:
        #     self.plot_graph(self.ax, self.plot_x, self.mod_y, mod_color)
        #     self.ax.annotate(symbol, xy=(0.02, 0.93), xycoords='axes fraction',
        #                      fontsize=8, color=mod_color, bbox=dict(boxstyle="round", fc='black', ec='None', alpha=0.4))

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
