from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import numpy as np
from kivy.clock import Clock

from tools import *


class FremApp(App):

    def build(self):
        #Clock.schedule_interval(lambda dt: print("FPS: ", Clock.get_fps()), 1)
        return MainGrid()


colors = [
    '#08F7FE',  # teal/cyan
    '#FE53BB',  # pink
    '#F5D300',  # yellow
    '#00ff41',  # matrix green
]


class MainGrid(BoxLayout):

    def __init__(self):
        global mod_plot, carrier_plot, fig, ax
        super(MainGrid, self).__init__()
        fig, ax = plt.subplots(1)
        fig.set_facecolor('#212946')
        mod_plot = FigureCanvasKivyAgg(fig)
        carrier_plot = FigureCanvasKivyAgg(plt.gcf(), pos_hint={'bottom': 1})

        self.ids.modulation.add_widget(mod_plot)
        #self.ids.modulation.add_widget(carrier_plot)
        self.integral = False
        self.chunk_size = 1000
        self.plot_x = np.linspace(0, 1, self.chunk_size)
        self.plot_y = np.zeros(self.chunk_size)
        self.label = 'Triangle'
        self.formula = ''
        self.update_plot()

    def switch_wf(self, label):
        self.label = label
        self.update_plot()

    def calc_integral(self):
        self.integral = self.ids.checkbox.active
        self.update_plot()

    def update_plot(self):

        # label, a, fm, x, c, lfo=0
        temp = current_trigon_wf(self.label, 0.5, self.ids.freq.value, self.plot_x, 0)
        self.formula = current_equation(self.label, 'Trigonometric function')

        if self.integral:
            temp = running_sum(temp, 0)
            self.plot_y = normalize(temp)
        else:
            self.plot_y = temp

        plotColor = '#08F7FE'
        if self.integral:
            plotColor = '#F5D300'

        # FREM

        plt.setp(ax.spines.values(), linewidth=3, color='grey', alpha=0.2)
        ax.cla()
        ax.plot(self.plot_x, self.plot_y, linewidth=1.5, alpha=1, color=plotColor)
        # glow effect
        ax.plot(self.plot_x, self.plot_y, linewidth=6, alpha=0.1, color=plotColor)
        ax.tick_params(left=False, bottom=False, labelbottom=False, labelleft=False)
        #ax.spines['top'].set_visible(False)
        #ax.spines['right'].set_visible(False)
        #ax.spines['bottom'].set_visible(False)
        #ax.spines['left'].set_visible(False)
        ax.set_facecolor('#212946')
        ax.annotate(self.formula, xy=(0.5, -0.26), xycoords='axes fraction',
                      fontsize=9, color='#08F7FE', bbox=dict(boxstyle="round", fc='None', ec="white", alpha=0.5), ha='center',
                      va='center')

        plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.3)
        plt.grid(color='grey', alpha=0.2)
        mod_plot.draw()


FremApp().run()
