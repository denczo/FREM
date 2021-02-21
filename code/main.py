import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.graph import Graph, LinePlot
#import pyaudio
import numpy as np
#from kivy.clock import Clock
#from scipy.io import wavfile
from pylatexenc.latex2text import LatexNodes2Text
from kivy.properties import ListProperty, StringProperty

from tools import *


# FREM
class MainApp(App):

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
    def __init__(self, color, chunk_size, waveform='Sine'):
        self.plot = []
        self.chunk_size = chunk_size
        self.graph_active = False
        self.waveform = waveform
        self.frequency = 1
        self.mod_wave = 0
        self.equation = ''
        self.color = color
        self.x = np.linspace(0, 1, chunk_size)
        self.init_plot(hex_to_rgb_array(color))

        self.y = 0
        self.formula = ''
        self.symbol = 'f(x)'
        self.render_wf()
        self.render_equation()

    def init_plot(self, color):
        max_width = 3.5
        end = 4
        for i in range(1, end):
            width = max_width / i
            color[-1] = i / (end - 1)
            self.plot.append(LinePlot(line_width=width, color=color))

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


# class AudioMaker:
#     def __init__(self, rate=44100, chunk_size=1024, gain=0.25):
#         self.rate = int(rate)
#         self.chunk_size = chunk_size
#         self.p = pyaudio.PyAudio()
#         self.stream = self.settings(1, self.rate, 1, self.chunk_size)
#         self.stream.start_stream()
#
#     def create_samples(self, start, end):
#         return np.arange(start, end) / self.rate
#
#     def settings(self, channels, rate, output, chunk_size):
#         return self.p.open(format=pyaudio.paFloat32,
#                            channels=channels,
#                            rate=rate,
#                            output=output,
#                            frames_per_buffer=chunk_size)
#
#     def render_audio(self, chunk, length=0):
#         self.stream.write(chunk.astype(np.float32).tobytes())
#         wavfile.write('recorded.wav', 44100, chunk)
#         # start = end
#         # end += self.chunk_size


class MainGrid(BoxLayout):

    equ_color = StringProperty('#08F7FE')
    formula = StringProperty('')

    def __init__(self):
        super(MainGrid, self).__init__()
        chunk_size = 1024
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=chunk_size)
        self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=chunk_size)
        self.carrier = CarrierWave('#00ff41', chunk_size=chunk_size)
        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        self.audio = AudioMaker()
        self._current_tab = 'WF_M1'
        self.old_tab = ''
        self.equ_color = self.mod_wave_1.color

        # self.fig = plt.figure(facecolor='#212946')

        self.graph = Graph(y_ticks_major=0.275, x_ticks_major=275,
                           border_color=[0, 1, 1, 1], tick_color=[0, 1, 1, 0.5],
                           x_grid=True, y_grid=True, xmin=-50, xmax=1050, ymin=-0.05, ymax=1.05, draw_border=True)

        self.chunk_size = chunk_size
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)

        self.ids.modulation.add_widget(self.graph)
        self.formula = ''
        self.old_formula = ''
        self.lines = []
        self.update_plot()

    @property
    def current_tab(self):
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        self._current_tab = value

    @staticmethod
    def lerp(c1, c2, t):
        r = c1.r + (c2.r - c1.r) * t
        g = c1.g + (c2.g - c1.g) * t
        b = c1.b + (c2.b - c1.b) * t
        a = c1.a + (c2.a - c1.a) * t
        return Color(r, g, b, a)

    def update_equation(self):
        if self._current_tab == 'WF_M1':
            self.formula = LatexNodes2Text().latex_to_text(self.mod_wave_1.equation)
            self.equ_color = self.mod_wave_1.color
        elif self._current_tab == 'WF_M2':
            self.formula = LatexNodes2Text().latex_to_text(self.mod_wave_2.equation)
            self.equ_color = self.mod_wave_2.color
        elif self._current_tab == 'WF_C':
            self.formula = LatexNodes2Text().latex_to_text(self.carrier.equation)
            self.equ_color = self.carrier.color

        if self.formula != self.old_formula or self.current_tab != self.old_tab:

            self.old_formula = self.formula
            self.old_tab = self.current_tab

    def init_plot(self):
        self.ax.tick_params(left=False, bottom=False, labelbottom=False, labelleft=False)
        self.ax.set_facecolor('#212946')

        plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.3)
        plt.grid(color='grey', alpha=0.2)

    def update_plot(self):

        wf_mod = 0
        for i in range(len(self.waveforms)):
            wf_carrier = self.waveforms[i]
            wf_carrier.change_mod_wave(wf_mod)
            wf_y = wf_carrier.y

            self.update_equation()
            for j in range(len(wf_carrier.plot)):
                self.graph.remove_plot(wf_carrier.plot[j])
                if wf_carrier.graph_active:
                    wf_carrier.plot[j].points = [(i, wf_y[i]) for i in range(self.chunk_size)]
                    self.graph.add_plot(wf_carrier.plot[j])
            pass
            if isinstance(wf_carrier, ModulationWave):
                wf_mod = wf_carrier.y * wf_carrier.mod_index

    # if self.int_active:
    #     symbol = 'F(x)'
    #     self.formula = r'$\int$ ' + self.formula
    #     mod_color = '#F5D300'

MainApp().run()
