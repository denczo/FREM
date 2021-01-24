import numpy as np


# discrete integration where s is your signal as array and l is your first entry
from waveform import Triangle, Sawtooth, SquareWave, Sine


def running_sum(s, l):
    y = np.zeros(len(s))
    y[0] = s[0] + l
    for n in range(1, len(s)):
        y[n] = s[n] + y[n - 1]
    return y


def normalize(y):
    return (y - y.min(axis=0)) / (y.max(axis=0) - y.min(axis=0))


def current_fourier_wf(label, i, fm, x):
    if label == 'Triangle':
        return Triangle.fourier_series(int(i), fm, x)
    elif label == 'Sawtooth':
        return Sawtooth.fourier_series(int(i), fm, x)
    elif label == 'Square Wave':
        return SquareWave.fourier_series(int(i), fm, x)


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


def equation_type(wf, title):
    if title == 'Fourier series':
        return wf.equation_fourier()
    elif title == 'Trigonometric function':
        return wf.equation_trigon()


def current_equation(label, title):

    if label == 'Sine':
        return equation_type(Sine, title)
    elif label == 'Triangle':
        return equation_type(Triangle, title)
    elif label == 'Sawtooth':
        return equation_type(Sawtooth, title)
    elif label == 'Square Wave':
        return equation_type(SquareWave, title)

