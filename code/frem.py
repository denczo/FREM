import os
#os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pyaudio
import numpy as np
from kivy.clock import Clock


from tools import *


class FremApp(App):

    def build(self):
        Clock.schedule_interval(lambda dt: print("FPS: ", Clock.get_fps()), 1)
        return MainGrid()


colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
]


class CarrierWave:
    def __init__(self, color, chunk_size, waveform='Sine'):
        self.chunk_size = chunk_size
        self.graph_active = False
        self.waveform = waveform
        self.frequency = 1
        self.mod_wave = 0
        self.equation = ''
        self.color = color
        self.x = np.linspace(0, 1, chunk_size)
        self.y = 0
        self.formula = ''
        self.symbol = 'f(x)'
        self.render_wf()
        self.render_equation()

    def change_waveform(self, wf):
        self.waveform = wf
        self.render_wf()
        self.render_equation()

    def change_frequency(self, f):
        self.frequency = f
        self.render_wf()

    def change_mod_wave(self, m):
        self.mod_wave = m
        self.render_wf()

    def render_wf(self):
        # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
        self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0.5, self.mod_wave)

    def render_equation(self):
        self.equation = current_equation(self.waveform, 'Trigonometric function')


class ModulationWave(CarrierWave):
    def __init__(self, color, chunk_size, waveform='Triangle'):
        self.int_active = False
        super().__init__(color, chunk_size, waveform)
        self.mod_index = 0.1
        self.graph_active = True

    def calculate_integral(self, value):
        self.int_active = value
        self.render_wf()

    def discrete_integration(self):
        self.y = running_sum(self.y, 0)
        self.y = normalize(self.y)

    def render_wf(self):
        if self.int_active:
            self.symbol = 'F(x)'
            # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0, self.mod_wave)
            self.discrete_integration()
        else:
            self.symbol = 'f(x)'
            # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0.5, self.mod_wave)

    def change_mod_index(self, mi):
        self.mod_index = mi / self.frequency
        self.render_wf()


class AudioMaker:
    def __init__(self, rate=44100, chunk_size=1024, gain=0.25):
        self.rate = int(rate)
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream = self.settings(1, self.rate, 1, self.chunk_size)
        self.stream.start_stream()

    def settings(self, channels, rate, output, chunk_size):
        return self.p.open(format=pyaudio.paFloat32,
                           channels=channels,
                           rate=rate,
                           output=output,
                           frames_per_buffer=chunk_size)

    def render_audio(self, length):

        self.stream.write(self.chunk.astype(np.float32).tostring())
        start = end
        end += self.chunk_size


class MainGrid(BoxLayout):

    def __init__(self):
        super(MainGrid, self).__init__()
        chunk_size = 2000
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=chunk_size)
        self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=chunk_size)
        self.carrier = CarrierWave('#00ff41', chunk_size=chunk_size)
        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        self._current_tab = 'WF_M1'

        self.fig = plt.figure(facecolor='#212946')
        self.ax = self.fig.add_subplot(111)
        self.ann = None
        self.ann_color = None
        self.plot = FigureCanvasKivyAgg(self.fig)
        self.plot_buffer = []

        self.chunk_size = chunk_size
        self.ids.modulation.add_widget(self.plot)
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)
        self.formula = ''
        self.old_formula = ''
        self.lines = []
        self.init_plot()
        self.update_plot()

    @property
    def current_tab(self):
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        self._current_tab = value

    def update_equation(self):
        if self._current_tab == 'WF_M1':
            self.formula = self.mod_wave_1.equation
            self.ann_color = self.mod_wave_1.color
        elif self._current_tab == 'WF_M2':
            self.formula = self.mod_wave_2.equation
            self.ann_color = self.mod_wave_2.color
        elif self._current_tab == 'WF_C':
            self.formula = self.carrier.equation
            self.ann_color = self.carrier.color

        if self.formula != self.old_formula:
            if self.ann is not None:
                self.ann.remove()
            self.ann = self.ax.annotate(self.formula, xy=(0.5, -0.26), xycoords='axes fraction',
                             fontsize=9, color=self.ann_color, bbox=dict(boxstyle="round", fc='black', ec="None", alpha=0.2),
                             ha='center',
                             va='center')
            self.old_formula = self.formula
            self.plot.draw()

    def init_plot(self):
        self.ax.tick_params(left=False, bottom=False, labelbottom=False, labelleft=False)
        self.ax.set_facecolor('#212946')

        plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.3)
        plt.grid(color='grey', alpha=0.2)

    def update_plot(self):

        #self.ax.cla()
        for ln in self.lines:
            ln.remove()
        self.lines.clear()
        wf_mod = 0
        for i in range(len(self.waveforms)):
            wf_carrier = self.waveforms[i]
            wf_carrier.change_mod_wave(wf_mod)
            wf_y = wf_carrier.y

            if wf_carrier.graph_active:
                self.update_equation()
                self.plot_graph(self.ax, self.plot_x, wf_y, wf_carrier.color)
                #self.ax.annotate(wf_carrier.symbol, xy=(0.02, 0.93), xycoords='axes fraction', fontsize=8, color='#F5D300', bbox=dict(boxstyle="round", fc='black', ec='None', alpha=0.4))

            if isinstance(wf_carrier, ModulationWave):
                print('TEST')
                wf_mod = wf_carrier.y * wf_carrier.mod_index

        # if self.int_active:
        #     symbol = 'F(x)'
        #     self.formula = r'$\int$ ' + self.formula
        #     mod_color = '#F5D300'

        self.plot.draw()

    def plot_graph(self, ax, x, y, color):

        ln, = ax.plot(x, y, linewidth=1.5, alpha=1, color=color)
        self.lines.append(ln)
        # glow effect
        ln, = ax.plot(x, y, linewidth=6, alpha=0.1, color=color)
        self.lines.append(ln)


FremApp().run()
