import kivy
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph
from kivy.properties import NumericProperty, ObjectProperty

from utils.infotext import InfoText
from utils.tools import *
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.config import ConfigParser
from kivy.uix.popup import Popup

import configparser
import threading
import os

os.environ["KIVY_IMAGE"] = "pil,sdl2"
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
kivy.require('2.0.0')


# FREM
class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = ConfigParser()
        self.app = None
        self.playback_thread = None

    def build(self):
        self.read_config()
        self.app = MainGrid()
        return self.app

    def init_thread(self):
        self.playback_thread = threading.Thread(target=self.app.play_result)
        self.playback_thread.setDaemon(True)
        self.playback_thread.start()

    def exit(self):
        App.get_running_app().stop()
        self.root_window.close()

    def on_start(self):
        self.config.read('./config/settings.ini')
        status = self.config.getint('settings', 'first_start')
        if status:
            self.app.show_info()
            self.app.show_warning_popup()
            self.config.set('settings', 'first_start', 0)
            self.config.write()

    def read_config(self):
        try:
            self.config.read('./config/settings.ini')
            self.config.get('settings', 'first_start')
        except configparser.NoSectionError:
            self.config.add_section('settings')
            self.config.set('settings', 'first_start', 1)
            self.config.set('settings', 'quality', 'Performance')
            self.config.write()


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
    settings = ObjectProperty(Settings)

    def __init__(self, **kw):
        super(MainGrid, self).__init__(**kw)
        self.config = ConfigParser()
        self.config.read('./config/settings.ini')
        self.settings = Settings.best_performance
        self.change_settings(self.config.get('settings', 'quality'))
        chunk_size = self.settings.chunk_size
        self.builder = Builder
        self.chunk_size = chunk_size
        self.rate = self.settings.sampling_rate
        self.wf_labels = ['Sine', 'Triangle', 'Sawtooth', 'Square Wave']
        self.max_minima = {}
        self.init_max_min()
        self.mod_wave_1 = ModulationWave('#08F7FE', waveform='Sine', chunk_size=self.chunk_size,
                                         max_minima=self.max_minima)
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
        hint.popupWindow = Popup(title="", content=hint, separator_height=0, background_color=[0.8, 0.8, 0.8, 0.8],
                                 size_hint=(0.75, 0.6))
        hint.popupWindow.open()

    @staticmethod
    def show_warning_popup():
        warning = Warning()
        warning.popupWindow = Popup(title="Caution!", content=warning, separator_height=1,
                                    background_color=[0, 0, 0, 0.5], size_hint=(0.75, 0.6))
        warning.popupWindow.open()

    @staticmethod
    def show_settings():
        settings_page = SettingsPage()
        settings_page.popupWindow = Popup(title="Settings", content=settings_page, separator_height=1,
                                          background_color=[0, 0, 0, 0.5])
        settings_page.popupWindow.open()

    # "Music of the 70s and 80s used lots of synthesizers which generate synthetic audio signals with all " \
    #                                     "kind of effects. One of those is the vibrato effect which sounds like this. There are analog and digital synthesizers" \
    #                                     "While analog synthesizer use physical components to generate the audio signal, digital synthesizer are doing this only with" \
    #                                     "mathematics and a digital computer chip. The vibrato effect can be realised mathematically by using frequency modulation." \
    #                                     "This App demonstrates it in an intuitive way and shows what else is possible with this concept."
    # "To render a waveform with a " \
    # "given frequency the amount of samples needs to be at least 2 times the frequency."\
    # "If you would like to render a waveform with 20khz (20.000hz) which is the highest"\
    # "frequency most people are able to hear, you would at least require 40.000 samples."\
    # "Therefore in the music industry often a samplingrate of 44.1khz is used which " \
    # "basically tells us that the audio is rendered with 44.100 samples per second." \
    @staticmethod
    def show_info():
        info = Info()  # Create a new instance of the P class
        # info.popupWindow = Popup(title="Info", content=info, separator_height=1, background_color=[0, 0, 0, 0.5])
        info.popupWindow = Popup(title="", content=info, separator_height=0, background_color=[0, 0, 0, 0.5])
        # Create the popup window
        info.popupWindow.open()  # show the popup
        info.ids.infoText_p1.text = InfoText.part1
        info.ids.infoText_p2.text = InfoText.part2
        info.ids.infoText_p3.text = InfoText.part3
        info.ids.infoText_p4.text = InfoText.part4
        info.ids.infoText_p5.text = InfoText.part5

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

    def audio_settings(self, value):
        self.config.set('settings', 'quality', value)
        self.config.write()

    def change_settings(self, value):
        if value == "Performance":
            self.settings = Settings.best_performance
        elif value == "Balanced":
            self.settings = Settings.balanced
        elif value == "Quality":
            self.settings = Settings.best_quality
        elif value == "Extreme":
            self.settings = Settings.extreme_quality

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
        if self.ids.play.state == 'down':
            self.ids.play.text = '[b]STOP[/b]'
            self.player.run()
        else:
            self.ids.play.text = '[b]PLAY[/b]'
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


class Info(FloatLayout):
    pass


class SettingsPage(FloatLayout):
    pass


class WarningPage(FloatLayout):
    pass


class Hint(FloatLayout):
    pass


class Intro(FloatLayout):
    pass


MainApp().run()
