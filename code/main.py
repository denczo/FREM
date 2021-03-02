import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from time import sleep

import kivy
kivy.require('2.0.0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
# from scipy.io import wavfile
from pylatexenc.latex2text import LatexNodes2Text
from kivy.properties import StringProperty
from kivy.config import Config
from tools import *

Config.set('graphics', 'width', '576')
Config.set('graphics', 'height', '1024')



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

    def __init__(self):
        super(MainGrid, self).__init__()
        chunk_size = 1024
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=chunk_size)
        self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=chunk_size, frequency=2)
        self.carrier = CarrierWave('#00ff41', chunk_size=chunk_size, frequency=4)
        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        self._current_tab = 'WF_M1'
        self.old_tab = ''
        self.equ_color = self.mod_wave_1.color
        self.player = AudioPlayer(1, 44100, 1024, self.waveforms)

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

    def test(self):
        print(self.ids.play.state)
        #self.ids.play.state = 'normal'

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

            if isinstance(wf_carrier, ModulationWave) and wf_carrier.int_active:
                wf_mod = wf_carrier.y * wf_carrier.mod_index


MainApp().run()

