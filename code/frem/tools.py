import numpy as np
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty
from kivy_garden.graph import LinePlot
from pylatexenc.latex2text import LatexNodes2Text

from waveform import Triangle, Sawtooth, SquareWave, Sine
from audiostream import get_output, AudioSample


# discrete integration where s is your signal as array and l is your first entry
def running_sum(s, l):
    y = np.zeros(len(s))
    y[0] = s[0] + l
    for n in range(1, len(s)):
        y[n] = s[n] + y[n - 1]
    return y


# normalize between -0.5 and 0.5
def normalize(y):
    return (y - y.min(axis=0)) / (y.max(axis=0) - y.min(axis=0)) - 0.5


def normalize_fixed(y, max, min):
    #return 2*((y - min) / (max - min)) - 1
    return (y - min) / (max - min) - 0.5


def current_trigon_wf(label, a, fm, x, c, lfo=0):
    if label == 'Triangle':
        return Triangle.trigonometric(a, fm, x, c, lfo)
    elif label == 'Sawtooth':
        return Sawtooth.trigonometric(a, fm, x, c, lfo)
    elif label == 'Square Wave':
        return SquareWave.trigonometric(a, fm, x, c, lfo)
    elif label == 'Sine':
        return Sine.trigonometric(a, fm, x, c, lfo)


def amp_modulation(amp, y):
    return amp * y


def current_equation(label, title):
    if label == 'Sine':
        return Sine.equation_trigon()
    elif label == 'Triangle':
        return Triangle.equation_trigon()
    elif label == 'Sawtooth':
        return Sawtooth.equation_trigon()
    elif label == 'Square Wave':
        return SquareWave.equation_trigon()


def hex_to_rgb_array(hex_code):
    start = 0
    end = 2
    if '#' in hex_code:
        start = 1
    end_r = start + end
    r = int(hex_code[start:end_r], 16)/255
    end_g = end_r + end
    g = int(hex_code[end_r:end_g], 16)/255
    b = int(hex_code[end_g:], 16)/255
    return [r, g, b, 1]


class AudioPlayer:
    def __init__(self, channels=1, rate=22050, buffer_size=1024, waveforms=[]):
        super().__init__()
        self.rate = rate
        self.chunk_size = buffer_size
        self.stream = get_output(channels=channels, rate=rate, buffersize=buffer_size)
        self.sample = AudioSample()
        #self.stream.add_sample(self.sample)
        self.chunk = None
        self.pos = 0
        self.playing = False
        self.waveforms = waveforms
        self.chunks = []

    def set_chunk(self, y):
        self.chunk = y

    @staticmethod
    def get_bytes(chunk):
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 32767).astype('int16').tobytes()

    def render_audio(self, pos):

        start = pos
        end = pos + self.chunk_size

        x_audio = np.arange(start, end) / self.rate
        wf_mod = 0
        for wf in self.waveforms:
            wf_c = wf.render_wf_audio(x_audio, wf_mod)
            if isinstance(wf, ModulationWave) and wf.int_active:
                wf_mod = wf_c * wf.mod_index
            else:
                wf_mod = 0

        return wf_c

    def run(self):
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        self.sample.play()
        self.playing = True

        while self.playing:
            chunk = self.render_audio(self.pos)
            self.chunks = np.append(self.chunks, chunk)
            chunk = self.get_bytes(chunk)
            self.sample.write(chunk)
            self.pos += self.chunk_size
            if not self.playing:
                self.sample.stop()

    def stop(self):
        self.playing = False
        self.sample.stop()


class CarrierWave(EventDispatcher):

    equation = StringProperty('')
    # color = StringProperty('')

    def __init__(self, color, chunk_size, waveform='Sine', frequency=1):
        self.chunk_size = chunk_size
        self.waveform = waveform
        self.frequency = frequency
        self.mod_wave = 0

        self.plot = []
        self.color = color
        self.init_plot(hex_to_rgb_array(color))
        self.graph_active = False
        self.equation = ''

        self.x = np.linspace(0, 1, chunk_size)
        self.y = 0
        self.render_wf()
        self.render_equation()

    def init_plot(self, color):
        max_width = 3
        end = 5
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
        self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0, self.mod_wave)

    def render_wf_audio(self, x, m):
        x_audio = x
        if len(x) == (self.chunk_size + 1):
            x_audio = x[1:]
        return current_trigon_wf(self.waveform, 0.5, self.frequency, x_audio, 0, m)

    def render_equation(self):
        self.equation = LatexNodes2Text().latex_to_text(current_equation(self.waveform, 'Trigonometric function'))


class MaxMinima:

    def __init__(self, rate, chunk_size, waveform='Sine'):
        self._global_max = 0
        self._global_min = 0
        self.label = waveform
        # min frequency to get a full period in one chunk
        self.frequency = int(rate/chunk_size+1)
        self.x_samples = np.arange(0, chunk_size)/rate
        self.calc_max_min()

    def calc_max_min(self):
        result = current_trigon_wf(self.label, 0.5, 1, self.x_samples, 0, 0)
        integral = running_sum(result, 0)
        self._global_min = min(integral)
        self._global_max = max(integral)

    def global_max(self, f=1):
        return self._global_max/f

    def global_min(self, f=1):
        return self._global_min/f


class ModulationWave(CarrierWave):

    def __init__(self, color, chunk_size, max_minima, waveform='Triangle', frequency=1):
        self.int_active = False
        super().__init__(color, chunk_size, waveform, frequency)
        self.mod_index = 0.1
        self.graph_active = True
        self.max_minima = max_minima
        # for discrete integration
        self.first_entry = 0

    def calculate_integral(self, value):
        self.int_active = value
        self.render_wf()

    @staticmethod
    def discrete_integration(chunk, first_entry=0):
        result = running_sum(chunk, first_entry)
        return normalize(result)

    def render_wf(self):
        if self.int_active:
            #self.symbol = 'F(x)'
            # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0, self.mod_wave)
            self.y = self.discrete_integration(self.y)
        else:
            #self.symbol = 'f(x)'
            # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0, self.mod_wave)

    def render_wf_audio(self, x, m):
        if self.int_active:
            result = current_trigon_wf(self.waveform, 0.5, self.frequency, x, 0, m)
            result = running_sum(result, self.first_entry)
            self.first_entry = result[-1]
            global_min = self.max_minima[self.waveform].global_min(self.frequency)
            global_max = self.max_minima[self.waveform].global_max(self.frequency)
            result = normalize_fixed(result, global_max, global_min)
            return result
        else:
            return 0

    def change_mod_index(self, mi):
        self.mod_index = mi / self.frequency
        self.render_wf()

    def render_equation(self):
        prefix = ''
        if self.int_active:
            prefix = r'$\int$ '
        result = LatexNodes2Text().latex_to_text(prefix + current_equation(self.waveform, 'Trigonometric function'))
        self.equation = result
