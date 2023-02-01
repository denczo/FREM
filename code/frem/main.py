from functools import partial
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
from kivy.logger import Logger
from kivy.clock import Clock
from multiprocessing import Pool
import multiprocessing as mp
import ctypes as c
from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["debug"])
import configparser
import threading
import os

os.environ["KIVY_IMAGE"] = "pil,sdl2"
# os.environ["KIVY_NO_CONSOLELOG"] = "1"
kivy.require('2.0.0')

# settings file
SETTINGS = "./code/frem/config/settings.ini"

samples = 4096
amount_graphs = 4
total_samples = samples * amount_graphs
shared_array = mp.Array(c.c_double, np.zeros(total_samples), lock=False)
shared_array_np = np.ndarray(total_samples, dtype=c.c_double, buffer=shared_array)
# frequencies
shared_value_freq_carrier = mp.Value('i', 5)
plot_x = np.linspace(0, 1, total_samples)
carrier = CarrierWave('#00ff41', chunk_size=samples, frequency=4)


def task():
    # for one waveform
    freq_carrier = 4
    plot_y = carrier.render_wf()
    array =  plot_y
    np.copyto(shared_array_np, array)


cpus = mp.cpu_count()
pool = Pool(cpus)


# FREM
class MainApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = ConfigParser()
        self.app = None
        self.playback_thread = None
        self.playback_process = None
        self.graph_process = None
        
        self.event = Event()

    def build(self):
        self.read_config()
        self.app = MainGrid()
        return self.app

    def init_graph_process(self):
        self.graph_process = Process(target=None)
        # self.graph_process = Process(target=self.app.update_plot)
        self.graph_process.daemon = True
        self.graph_process.start()
        print("Graph Process", self.graph_process.pid, "started")
        # self.exit_graph_process()

    def exit_graph_process(self):
        print("Graph Process", self.graph_process.pid, "ended")
        self.graph_process.join()

    def init_thread(self):
        
        # self.playback_process = Process(target=self.app.player.run, args=(self.event,))
        # self.playback_thread = threading.Thread(target=self.app.player.run)
        # self.playback_thread.setDaemon(True)
        self.playback_process.daemon = True
        self.playback_process.start()
        # print("Playback Thread", self.playback_thread.native_id, "started")
        print("Playback Process", self.playback_process.pid, "started")
        print("Main Thread", threading.main_thread().native_id)

    def exit_thread(self):
        self.event.set()
        self.playback_process.kill()
        self.playback_process.join()
        
        # self.playback_process.close()
        # self.playback_process.join()
        print("Playback Process", self.playback_process.pid, "stopped")
        # print("Playback Thread", self.playback_thread.native_id, "stopped")

    def init_process(self):
        pass

    def exit_process(self):
        pass


    # def exit(self):
    #     App.get_running_app().stop()
    #     self.root_window.close()

    def on_start(self):
        self.config.read(SETTINGS)
        status = self.config.getint('settings', 'first_start')
        if status:
            self.app.show_info()
            self.app.show_warning_popup()
            self.config.set('settings', 'first_start', 0)
            self.config.write()

        # p = Process(target=test_method)
        # p.start()
        print("ON START")

    def read_config(self):
        try:
            Logger.info("settings.ini: "+ "exists: "+str(os.path.exists(SETTINGS)))
            self.config.read(SETTINGS)
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

class Visuals():
    def __init__(self) -> None:
        self.chunk_size = 1024
        self.graph_max_x = self.chunk_size + 1
        self.graph_min_x = 0
        self.draw_border = False
        # self.test = Queue()

        self.graph = Graph(y_ticks_major=0.275, x_ticks_major=self.chunk_size / 8, x_grid_label=True,
                           border_color=[0, 1, 1, 1], tick_color=[0, 0, 0, 1],
                           x_grid=True, y_grid=True, xmin=self.graph_min_x, xmax=self.graph_max_x, ymin=-0.55,
                           ymax=0.56, draw_border=self.draw_border)

    def test_method(self):
        print("test")

    def update_plot(self, wf_carrier):
        print("UPDATE")
        wf_y = wf_carrier.y
        for j in range(len(wf_carrier.plot)):
            print(len(wf_carrier.plot))
            # self.graph.remove_plot(wf_carrier.plot[j])
            if wf_carrier.graph_active:
                print("YEAH", wf_carrier.plot[j].points)
                self.test.put([(i, wf_y[i]) for i in range(self.chunk_size)])
                wf_carrier.plot[j].points = [(i, wf_y[i]) for i in range(self.chunk_size)]
                # self.test.put(wf_carrier.plot[j].points)
                # print("UH", self.test.get())
                # self.graph.add_plot(self.test.get())
                self.graph.add_plot(wf_carrier.plot[j])


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
        self.config.read(SETTINGS)
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
        # self.graph_max_x = self.chunk_size + 1
        # self.graph_min_x = 0
        # self.graph = Graph(y_ticks_major=0.275, x_ticks_major=self.chunk_size / 8, x_grid_label=True,
        #                    border_color=[0, 1, 1, 1], tick_color=[0, 0, 0, 1],
        #                    x_grid=True, y_grid=True, xmin=self.graph_min_x, xmax=self.graph_max_x, ymin=-0.55,
        #                    ymax=0.56, draw_border=self.draw_border)
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)
        
        self.visuals = Visuals()
        self.ids.modulation.add_widget(self.visuals.graph)
        # self.visuals.update_plot(self.mod_wave_1)
        # self.p = Process(target=partial(self.visuals.update_plot, self.mod_wave_1))

        self.formula = ''
        self.old_formula = ''
        self.lines = []
        # self.update_plot()
        self.update_equations()
        

    @staticmethod
    def show_hint():
        hint = Hint()
        hint.popupWindow = Popup(title="", content=hint, separator_height=0, background_color=[0.8, 0.8, 0.8, 0.8],
                                 size_hint=(0.75, 0.6))
        hint.popupWindow.open()

    @staticmethod
    def show_info():
        info = Info()
        info.popupWindow = Popup(title="Info", content=info, separator_height=1, background_color=[0, 0, 0, 0.5])
        info.popupWindow.open()

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

    @staticmethod
    def show_help():
        help = Help()  # Create a new instance of the P class
        # info.popupWindow = Popup(title="Info", content=info, separator_height=1, background_color=[0, 0, 0, 0.5])
        help.popupWindow = Popup(title="", content=help, separator_height=0, background_color=[0, 0, 0, 0.5])
        # Create the popup window
        help.popupWindow.open()  # show the popup
        help.ids.infoText_p1.text = InfoText.part1
        help.ids.infoText_p2.text = InfoText.part2
        help.ids.infoText_p3.text = InfoText.part3
        help.ids.infoText_p4.text = InfoText.part4
        help.ids.infoText_p5.text = InfoText.part5

    def init_max_min(self):
        for wf in self.wf_labels:
            max_minima = MaxMinima(self.rate, self.chunk_size, wf)
            self.max_minima[wf] = max_minima

    def update_zoom(self, value):
        # if value == '+' and self.zoom < 8:
        #     self.zoom *= 2
        #     self.graph.x_ticks_major /= 2
        # elif value == '-' and self.zoom > 1:
        #     self.zoom /= 2
        #     self.graph.x_ticks_major *= 2
        # self.p = Process(target=partial(self.visuals.update_plot, self.mod_wave_1))
        # self.p = Process(target=self.visuals.test_method)
        # self.p.daemon = True
        # self.p.start()
        # self.p.join()
            # self.visuals.update_plot(self.mod_wave_1)
        pass

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
            print("PLAY")
            self.ids.play.text = '[b]STOP[/b]'
            # works with onpress event
            #self.test()

            App.get_running_app().init_thread()
        else:
            print("STOP")
            self.ids.play.text = '[b]PLAY[/b]'
            # self.player.stop()
            App.get_running_app().exit_thread()

    def update_equations(self):
        self.ids.equ_wf_1.text = self.mod_wave_1.equation
        self.ids.equ_wf_2.text = self.mod_wave_2.equation
        self.ids.equ_wf_3.text = self.carrier.equation

    #TODO run in own thread/process
    def update_plot(self):
        wf_mod = 0
        for i in range(len(self.waveforms)):
            wf_carrier = self.waveforms[i]
            wf_carrier.render_equation()
            wf_carrier.change_mod_wave(wf_mod)
            wf_y = wf_carrier.y

            self.update_equation()
            for j in range(len(wf_carrier.plot)):
                # self.graph.remove_plot(wf_carrier.plot[j])
                self.visuals.graph.remove_plot(wf_carrier.plot[j])
                if wf_carrier.graph_active:
                    wf_carrier.plot[j].points = [(i, wf_y[i]) for i in range(self.chunk_size)]
                    # self.graph.add_plot(wf_carrier.plot[j])
                    self.visuals.graph.add_plot(wf_carrier.plot[j])

            if isinstance(wf_carrier, ModulationWave) and wf_carrier.int_active:
                wf_mod = wf_carrier.y * wf_carrier.mod_index
        if self.width > self.height:
            self.update_equations()


    def update_plot_multicore(self):
        #mod = 0
        print("multicore")
        # pool.apply(task)
        # self.plot.points = [(x, shared_array_np[x]) for x in range(self.samples)]

class Help(FloatLayout):
    pass


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
