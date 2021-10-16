import numpy as np


class Sawtooth:

    # a = amplitude, f = frequency, x = samples, c = constant
    @staticmethod
    def trigonometric(a, f, x, c=0, m=0):
        return -2 * a / np.pi * np.arctan(1 / np.tan(2 * np.pi * f/2 * x + m)) + c
    # a = amplitude, f = frequency, x = samples

    @staticmethod
    def equation_trigon():
        return r'$-2a/\pi + 1/\pi \ \arctan(1/(\tan(2\pi f/2 x))) + C$'


class SquareWave:

    # a = amplitude, f = frequency, x = samples, c = constant
    @staticmethod
    def trigonometric(a, f, x, c=0, m=0):
        return a * np.sign(np.sin(2*np.pi * f * x + m)) + c

    @staticmethod
    def equation_trigon():
        return r'$a sign(\sin(2\pi f x)) + C $'


class Triangle:

    # a = amplitude, f = frequency, x = samples, c = constant
    @staticmethod
    def trigonometric(a, f, x, c, m):
        return 2 * a / np.pi * np.arcsin(np.sin(2 * np.pi * f * x - np.pi/2 + m)) + c

    @staticmethod
    def equation_trigon():
        return r'$2a/\pi \ \arcsin(\sin(2\pi f x - \pi/2)) + C$'


class Sine:

    # a = amplitude, f = frequency, x = samples, c = constant
    @staticmethod
    def trigonometric(a, f, x, c, m):
        return a * np.sin(2 * np.pi * f * x - np.pi/2 + m) + c

    @staticmethod
    def equation_trigon():
        return r'$a \sin(2\pi f x - \pi/2) + C$'

