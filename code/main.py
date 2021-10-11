import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from time import sleep
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
import kivy
from kivy.core.window import Window

kivy.require('2.0.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
from pylatexenc.latex2text import LatexNodes2Text
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.config import Config
from tools import *
from kivy.lang import Builder


#orientation = 'portrait'

orientation = 'landscape'
width = ''
height = ''
draw_border = True

# if orientation == 'landscape':
#     height = '576'
#     width = '1024'
#     Builder.unload_file('portrait.kv')
#     Builder.load_file('landscape.kv')
#     draw_border = False
#
# elif orientation == 'portrait':
#     width = '576'
#     height = '1024'
#     Builder.unload_file('landscape.kv')
#     Builder.load_file('portrait.kv')
#     draw_border = True

# Config.set('graphics', 'width', width)
# Config.set('graphics', 'height', height)
# Builder.load_file('portrait.kv')
# width = '576'
# height = '1024'
# Config.set('graphics', 'width', width)
# Config.set('graphics', 'height', height)
# Builder.load_file('portrait.kv')
Builder.load_file('landscape.kv')


# FREM
class MainApp(App):

    def build(self):

        return MainGrid()


colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
]


class MainGrid(BoxLayout):
    equ_color = StringProperty('#08F7FE')
    formula = StringProperty('')
    zoom = NumericProperty(1)
    mod_wave_1 = ObjectProperty(ModulationWave)
    mod_wave_2 = ObjectProperty(ModulationWave)
    carrier = ObjectProperty(CarrierWave)

    def __init__(self, **kw):
        super(MainGrid, self).__init__(**kw)
        chunk_size = 1024
        self.builder = Builder
        self.chunk_size = chunk_size
        self.rate = 44100
        self.wf_labels = ['Sine', 'Triangle', 'Sawtooth', 'Square Wave']
        self.max_minima = {}
        self.init_max_min()
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=chunk_size, max_minima=self.max_minima)
        self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=chunk_size, max_minima=self.max_minima, frequency=2)
        self.carrier = CarrierWave('#00ff41', chunk_size=chunk_size, frequency=4)
        self.draw_border = False

        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        self._current_tab = 'WF_M1'
        self.old_tab = ''
        self.equ_color = self.mod_wave_1.color
        self.player = AudioPlayer(1, 44100, 4096, self.waveforms)

        self.graph_max_y = 1100
        self.graph_min_y = -76
        self.graph = Graph(y_ticks_major=0.275, x_ticks_major=50,
                           border_color=[0, 1, 1, 1], tick_color=[0, 1, 1, 0.5],
                           x_grid=True, y_grid=True, xmin=self.graph_min_y, xmax=self.graph_max_y, ymin=-0.55, ymax=0.55, draw_border=self.draw_border)

        self.chunk_size = chunk_size
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)

        self.ids.modulation.add_widget(self.graph)
        self.formula = ''
        self.old_formula = ''
        self.lines = []
        self.update_plot()
        self.update_equations()

    def init_max_min(self):
        for wf in self.wf_labels:
            max_minima = MaxMinima(self.rate, self.chunk_size, wf)
            self.max_minima[wf] = max_minima

    def update_zoom(self, value):
        if value == '+' and self.zoom < 16:
            self.zoom *= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2

    @property
    def current_tab(self):
        return self._current_tab

    @current_tab.setter
    def current_tab(self, value):
        self._current_tab = value

    def update_equation(self):
        if self._current_tab == 'WF_M1':
            self.formula = LatexNodes2Text().latex_to_text(self.mod_wave_1.equation)
            self.equ_color = self.mod_wave_1.color

            if self.mod_wave_1.int_active:
                self.formula = LatexNodes2Text().latex_to_text(r'$\int$ ' + self.formula)

        elif self._current_tab == 'WF_M2':
            self.formula = LatexNodes2Text().latex_to_text(self.mod_wave_2.equation)
            self.equ_color = self.mod_wave_2.color

            if self.mod_wave_2.int_active:
                self.formula = LatexNodes2Text().latex_to_text(r'$\int$ ' + self.formula)

        elif self._current_tab == 'WF_C':
            self.formula = LatexNodes2Text().latex_to_text(self.carrier.equation)
            self.equ_color = self.carrier.color

        if self.formula != self.old_formula or self.current_tab != self.old_tab:
            self.old_formula = self.formula
            self.old_tab = self.current_tab

    def play_result(self):
        if self.ids.play.state == 'down':
            self.player.run()
        else:
            self.player.stop()

    def update_equations(self):
        self.ids.equ_wf_1.text = self.mod_wave_1.equation
        self.ids.equ_wf_2.text = self.mod_wave_2.equation
        self.ids.equ_wf_3.text = self.carrier.equation

    def update_plot(self):

        wf_mod = 0
        for i in range(len(self.waveforms)):
            wf_carrier = self.waveforms[i]
            wf_carrier.render_equation()
            wf_carrier.change_mod_wave(wf_mod)
            wf_y = wf_carrier.y

            self.update_equation()
            for j in range(len(wf_carrier.plot)):
                self.graph.remove_plot(wf_carrier.plot[j])
                if wf_carrier.graph_active:
                    wf_carrier.plot[j].points = [(i, wf_y[i]) for i in range(self.chunk_size)]
                    self.graph.add_plot(wf_carrier.plot[j])

            if isinstance(wf_carrier, ModulationWave) and wf_carrier.int_active:
                wf_mod = wf_carrier.y * wf_carrier.mod_index
        if self.width > self.height:
            self.update_equations()


MainApp().run()

