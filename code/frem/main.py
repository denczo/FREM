import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivy.uix.image import Image
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, LinePlot
from kivy.properties import NumericProperty
from tools import *
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
kivy.require('2.0.0')


# FREM
class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None

    def build(self):
        self.app = MainGrid()
        return self.app

    def on_start(self):
        self.app.show_warning_popup()


colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
]


class RotatedImage(Image):
    angle = NumericProperty()


class MainGrid(BoxLayout):
    equ_color = StringProperty('#08F7FE')
    formula = StringProperty('')
    zoom = NumericProperty(1)
    mod_wave_1 = ObjectProperty(ModulationWave)
    mod_wave_2 = ObjectProperty(ModulationWave)
    carrier = ObjectProperty(CarrierWave)

    def __init__(self, **kw):
        super(MainGrid, self).__init__(**kw)
        self.settings = Settings.best_quality
        chunk_size = self.settings.chunk_size
        self.builder = Builder
        self.chunk_size = chunk_size
        self.rate = self.settings.sampling_rate
        self.wf_labels = ['Sine', 'Triangle', 'Sawtooth', 'Square Wave']
        self.max_minima = {}
        self.setup()
        # self.init_max_min()
        # self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=chunk_size, max_minima=self.max_minima)
        # self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=chunk_size,
        #                                  max_minima=self.max_minima, frequency=2)
        # self.carrier = CarrierWave('#00ff41', chunk_size=chunk_size, frequency=4)
        # self.draw_border = False
        #
        # self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        # self._current_tab = 'WF_M1'
        # self.old_tab = ''
        # self.equ_color = self.mod_wave_1.color
        # self.player = AudioPlayer(1, self.rate, self.chunk_size, self.settings.fade_seq, self.waveforms)
        # self.graph_max_x = self.chunk_size + 1
        # self.graph_min_x = 0
        # self.graph = Graph(y_ticks_major=0.275, x_ticks_major=self.chunk_size/8, x_grid_label=True,
        #                    border_color=[0, 1, 1, 1], tick_color=[0, 0, 0, 1],
        #                    x_grid=True, y_grid=True, xmin=self.graph_min_x, xmax=self.graph_max_x, ymin=-0.55,
        #                    ymax=0.56, draw_border=self.draw_border)
        # self.plot_x = np.linspace(0, 1, self.chunk_size)
        # self.plot_y = np.zeros(self.chunk_size)
        #
        # self.ids.modulation.add_widget(self.graph)
        # self.formula = ''
        # self.old_formula = ''
        # self.lines = []
        # self.update_plot()
        # self.update_equations()
        self.show_warning_popup()

    def on_start(self):
        self.show_popup()

    def setup(self):
        self.init_max_min()
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=self.chunk_size, max_minima=self.max_minima)
        self.mod_wave_2 = ModulationWave('#FE53BB', waveform='Triangle', chunk_size=self.chunk_size,
                                         max_minima=self.max_minima, frequency=2)
        self.carrier = CarrierWave('#00ff41', chunk_size=self.chunk_size, frequency=4)
        self.draw_border = False

        self.waveforms = [self.mod_wave_1, self.mod_wave_2, self.carrier]
        self._current_tab = 'WF_M1'
        self.old_tab = ''
        self.equ_color = self.mod_wave_1.color
        self.player = AudioPlayer(1, self.rate, self.chunk_size, self.settings.fade_seq, self.waveforms)
        self.graph_max_x = self.chunk_size + 1
        self.graph_min_x = 0
        self.graph = Graph(y_ticks_major=0.275, x_ticks_major=self.chunk_size / 8, x_grid_label=True,
                           border_color=[0, 1, 1, 1], tick_color=[0, 0, 0, 1],
                           x_grid=True, y_grid=True, xmin=self.graph_min_x, xmax=self.graph_max_x, ymin=-0.55,
                           ymax=0.56, draw_border=self.draw_border)
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)

        self.ids.modulation.add_widget(self.graph)
        self.formula = ''
        self.old_formula = ''
        self.lines = []
        self.update_plot()
        self.update_equations()


    @staticmethod
    def show_hint():
        hint = Hint()
        hint.popupWindow = Popup(title="Hint!", content=hint, separator_height=1, background_color=[0, 0, 0, 0.5])
        hint.popupWindow.open()

    @staticmethod
    def show_warning_popup():
        warning = Warning()
        warning.popupWindow = Popup(title="Caution!", content=warning, separator_height=1, background_color=[0, 0, 0, 0.5])
        warning.popupWindow.open()

    @staticmethod
    def show_popup():
        show = P()  # Create a new instance of the P class
        show.popupWindow = Popup(title="Info", content=show, separator_height=1, background_color=[0, 0, 0, 0.5])
        # Create the popup window
        show.popupWindow.open()  # show the popup
        show.ids.infoText.text = "[b]Welcome to FREM [/b] \n\n[b]FREM[/b] is a tool to show how frequency modulation " \
                                 "mathematically works which is also widely used in synthesizers (e.g. vibrato " \
                                 "effect). For frequency modulation you will need at least two waveforms. One acts " \
                                 "as [b]Modulating Wave[/b], the other one as [b]Carrier Wave[/b]. This tool provides "\
                                 "[b]three[/b] waveforms, which means two modulating waves can be applied on one " \
                                 "carrier wave. \n\n\n[b]How to use FREM?[/b]\n\nFor each waveform it can be switched "\
                                 "between four types: [b]Sine[/b], [b]Sawtooth[/b], [b]Triangle[/b] and [b]Square[/b]."\
                                 " Each type has a different formula which will be shown and also can be visualized. " \
                                 "For a closer look you can also zoom in." \
                                 "\n\n[b]visible Graph: [/b] visualises the graph of the current selected waveform. " \
                                 "The graph represents [color=FF0000]one second[/color]. The audio however is rendered"\
                                 " in realtime as long as it's played. The played audio is not a loop!" \
                                 "\n\n[b]Modulation Index: [/b] describes the factor, how much the modulation will be "\
                                 "applied on the carrier wave \n\n[b]calculate F(x): [/b] integrates the formula of " \
                                 "the selected waveform and enables the [b]Modulation Index[/b] \n\n[b]Carrier Wave: " \
                                 "[/b] each waveform can be the carrier wave on which the modulating wave will be " \
                                 "applied. E.g. [color=08F7FE]Modulating Wave[/color] [color=FE53BB]Carrier " \
                                 "Wave[/color] or [color=FE53BB]Modulating Wave[/color] [color=00ff41]Carrier " \
                                 "Wave[/color] \n\n[b]Modulating Wave: [/b] each waveform can be also the modulating " \
                                 "wave except for the [color=00ff41]last one[/color]. " \
                                 "To apply the modulating wave onto the carrier wave, the discrete integration of the "\
                                 "waveform needs to be calculated ([b] calculate F(x)[/b] ).\n\n[b]PLAY:[/b] plays " \
                                 "the carrier wave with it's applied modulation."

    def init_max_min(self):
        for wf in self.wf_labels:
            max_minima = MaxMinima(self.rate, self.chunk_size, wf)
            self.max_minima[wf] = max_minima

    def update_zoom(self, value):
        if value == '+' and self.zoom < 8:
            self.zoom *= 2
            self.graph.x_ticks_major /= 2
        elif value == '-' and self.zoom > 1:
            self.zoom /= 2
            self.graph.x_ticks_major *= 2

    def change_settings(self, value):
        if value == "Performance":
            self.settings = Settings.best_performance
        elif value == "Balanced":
            self.settings = Settings.balanced
        elif value == "Quality":
            self.settings = Settings.best_quality
        elif value == "Extreme":
            self.settings = Settings.extreme_quality
        self.ids.modulation.remove_widget(self.graph)
        self.graph.clear_widgets()
        self.apply_settings()
        self.player.end()
        del self.player

        self.setup()

    def apply_settings(self):
        self.chunk_size = self.settings.chunk_size
        self.rate = self.settings.sampling_rate
        self.fade_seq = self.settings.fade_seq

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
        print("still running")
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


class P(FloatLayout):
    pass


class Warning(FloatLayout):
    pass


class Hint(FloatLayout):
    pass


MainApp().run()
