import numpy as np
from kivy.event import EventDispatcher
from kivy.properties import StringProperty
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
    # return 2*((y - min) / (max - min)) - 1
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


def current_equation(label, modulated):
    if label == 'Sine':
        return Sine.equation_trigon(modulated)
    elif label == 'Triangle':
        return Triangle.equation_trigon(modulated)
    elif label == 'Sawtooth':
        return Sawtooth.equation_trigon(modulated)
    elif label == 'Square Wave':
        return SquareWave.equation_trigon(modulated)


def hex_to_rgb_array(hex_code):
    start = 0
    end = 2
    if '#' in hex_code:
        start = 1
    end_r = start + end
    r = int(hex_code[start:end_r], 16) / 255
    end_g = end_r + end
    g = int(hex_code[end_r:end_g], 16) / 255
    b = int(hex_code[end_g:], 16) / 255
    return [r, g, b, 1]


class AudioPlayer:
    def __init__(self, channels=1, rate=22050, buffer_size=1024, fade_seq=256, waveforms=[]):
        super().__init__()
        self.rate = rate
        self.chunk_size = buffer_size
        self.fade_seq = fade_seq
        self.stream = get_output(channels=channels, rate=rate, buffersize=buffer_size, encoding=16)
        self.sample = AudioSample()
        print("AudioPlayer Chunksize ", self.chunk_size)
        print("Sampling Rate ", self.rate)
        # self.stream.add_sample(self.sample)
        self.chunk = None
        self.pos = 0
        self.playing = False
        self.waveforms = waveforms
        self.chunks = []
        self.smoother = Smoother(self.fade_seq)

    def set_chunk(self, y):
        self.chunk = y

    def end(self):
        self.stop()
        del self.stream
        del self.sample

    @staticmethod
    def get_bytes(chunk):
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 32767).astype('int16').tobytes()
        # return (chunk * 32767).astype('int8').tobytes()

    def render_audio(self, pos):

        start = pos
        end = pos + (self.chunk_size + self.fade_seq)

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
        print("still running")

        while self.playing:
            # smoothing
            chunk = self.smoother.smooth_transition(self.render_audio(self.pos))
            self.smoother.buffer = chunk[-self.fade_seq:]
            self.chunks = np.append(self.chunks, chunk)
            chunk = self.get_bytes(chunk[:self.chunk_size])
            self.sample.write(chunk)
            self.pos += self.chunk_size
            # print("still running")
            if not self.playing:
                self.sample.stop()

    def stop(self):
        self.playing = False
        self.sample.stop()


class Setting:

    def __init__(self, chunk_size, sampling_rate, fade_seq, realtime_rendering, button_states):
        self._chunk_size = chunk_size
        self._sampling_rate = sampling_rate
        self._fade_seq = fade_seq
        self._realtime_rendering = realtime_rendering
        self._button_states = button_states

    @property
    def chunk_size(self):
        return self._chunk_size

    @property
    def sampling_rate(self):
        return self._sampling_rate

    @property
    def fade_seq(self):
        return self._fade_seq

    @property
    def realtime_rendering(self):
        return self._realtime_rendering

    @property
    def button_states(self):
        return self._button_states


class Settings:
    best_performance = Setting(512, 11025, 256, False, ['down', 'normal', 'normal', 'normal'])
    balanced = Setting(512, 22050, 256, False, ['normal', 'down', 'normal', 'normal'])
    best_quality = Setting(2048, 44100, 256, True, ['normal', 'normal', 'down', 'normal'])
    extreme_quality = Setting(4096, 44100, 512, True, ['normal', 'normal', 'normal', 'down'])


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
        max_width = 2
        end = 2
        # max_width = 3
        # end = 5
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
        self.equation = LatexNodes2Text().latex_to_text(current_equation(self.waveform, False))


class MaxMinima:

    def __init__(self, rate, chunk_size, waveform='Sine'):
        self._global_max = 0
        self._global_min = 0
        self.label = waveform
        # min frequency to get a full period in one chunk
        self.frequency = int(rate / chunk_size + 1)
        self.x_samples = np.arange(0, chunk_size) / rate
        self.calc_max_min()

    def calc_max_min(self):
        result = current_trigon_wf(self.label, 0.5, 1, self.x_samples, 0, 0)
        integral = running_sum(result, 0)
        self._global_min = min(integral)
        self._global_max = max(integral)

    def global_max(self, f=1):
        return self._global_max / f

    def global_min(self, f=1):
        return self._global_min / f


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
            # label, a = amplitude, f = frequency, x = samples, c = constant, m = modulation wave
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0, self.mod_wave)
            self.y = self.discrete_integration(self.y)
        else:
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
        result = LatexNodes2Text().latex_to_text(prefix + current_equation(self.waveform, self.int_active))
        self.equation = result


class Smoother:
    def __init__(self, fade_seq):
        self.fade_seq = fade_seq
        self._buffer = np.zeros(fade_seq)
        self.coefficients = np.linspace(0, 1, fade_seq)
        self.coefficientsR = self.coefficients[::-1]

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        size_value = len(value)
        if size_value == self.fade_seq:
            self._buffer = value
        else:
            raise AttributeError("size of parameter {} doesn't fit size of buffer {}".format(size_value, self.fade_seq))

    # smooths transition between chunks to prevent discontinuities
    def smooth_transition(self, signal):
        buffer = [a * b for a, b in zip(self.coefficientsR, self.buffer)]
        # fade in
        signal[:self.fade_seq] = [a * b for a, b in zip(self.coefficients, signal[:self.fade_seq])]
        # add part from previous chunk
        signal[:self.fade_seq] += buffer
        return signal
