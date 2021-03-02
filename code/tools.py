import numpy as np
from kivy_garden.graph import LinePlot

from waveform import Triangle, Sawtooth, SquareWave, Sine
from audiostream import get_output, AudioSample


# discrete integration where s is your signal as array and l is your first entry
def running_sum(s, l):
    y = np.zeros(len(s))
    y[0] = s[0] + l
    for n in range(1, len(s)):
        y[n] = s[n] + y[n - 1]
    return y


def normalize(y):
    return (y - y.min(axis=0)) / (y.max(axis=0) - y.min(axis=0))


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
    def __init__(self, channels=1, rate=44100, buffer_size=1024, waveforms=[]):
        super().__init__()
        self.rate = rate
        self.chunk_size = buffer_size
        self.stream = get_output(channels=channels, rate=rate, buffersize=buffer_size)
        self.sample = AudioSample()
        self.stream.add_sample(self.sample)
        self.chunk = None
        self.pos = 0
        self.playing = False
        self.waveforms = waveforms

    def set_chunk(self, y):
        self.chunk = y

    @staticmethod
    def get_bytes(chunk):
        # chunk is scaled and converted from float32 to int16 bytes
        return (chunk * 2**15).astype('int16').tobytes()

    def render_audio(self, pos):

        start = pos
        end = pos + self.chunk_size
        x_audio = np.arange(start, end) / self.rate

        old_wf = 0
        for wf in self.waveforms:
            new_wf = wf.render_wf_audio(x_audio, old_wf)
            old_wf = new_wf
            if isinstance(old_wf, ModulationWave) and wf.int_active:
                old_wf *= old_wf.mod_index

        return old_wf

    def run(self):
        self.sample.play()
        self.playing = True
        while self.playing:
            chunk = self.render_audio(self.pos)
            chunk = self.get_bytes(chunk)
            self.sample.write(chunk)
            self.pos += self.chunk_size
        self.sample.stop()

    def stop(self):
        self.playing = False
        self.sample.stop()


class CarrierWave:

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

    def render_wf_audio(self, x, m):
        return current_trigon_wf(self.waveform, 0.5, self.frequency, x, 0.5, m)

    def render_equation(self):
        self.equation = current_equation(self.waveform, 'Trigonometric function')


class ModulationWave(CarrierWave):

    def __init__(self, color, chunk_size, waveform='Triangle', frequency=1):
        self.int_active = False
        super().__init__(color, chunk_size, waveform, frequency)
        self.mod_index = 0.1
        self.graph_active = True

    def calculate_integral(self, value):
        self.int_active = value
        self.render_wf()

    @staticmethod
    def discrete_integration(chunk):
        result = running_sum(chunk, 0)
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
            self.y = current_trigon_wf(self.waveform, 0.5, self.frequency, self.x, 0.5, self.mod_wave)

    def render_wf_audio(self, x, m):
        if self.int_active:
            result = current_trigon_wf(self.waveform, 0.5, self.frequency, x, 0, m)
            return normalize(result)
        else:
            return 0

    def change_mod_index(self, mi):
        self.mod_index = mi / self.frequency
        self.render_wf()
