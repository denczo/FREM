from math import sin
from kivy.garden.graph import Graph, Plot, MeshLinePlot, SmoothLinePlot, MeshStemPlot, LinePlot
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import numpy as np
from pylatexenc.latex2text import LatexNodes2Text


class Color:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a


class TestApp(App):

    def build(self):
        # Clock.schedule_interval(lambda dt: print("FPS: ", Clock.get_fps()), 1)
        return MainGrid()


class MainGrid(BoxLayout):

    def __init__(self):
        super(MainGrid, self).__init__()
        self.graph = Graph(padding=10,
                           x_grid=True, y_grid=True, xmin=-0.2, xmax=0.2, ymin=-1, ymax=1, draw_border=False)
        # self.plot = SmoothLinePlot(color=[1, 1, 1, 1])

        # self.graph.add_plot(self.plot)
        self.plot_x = np.linspace(0, 1, 1024)
        f = 200
        self.plot_y = 0.5 * np.sin(2 * np.pi * f * self.plot_x)
        self.draw_plot(self.plot_x, self.plot_y)

        # self.plot.points = [(self.plot_x[i], self.plot_y[i]) for i in range(1024)]
        # self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]
        self.add_widget(self.graph)

    def lerp(self, c1, c2, t):
        r = c1.r + (c2.r - c1.r) * t
        g = c1.g + (c2.g - c1.g) * t
        b = c1.b + (c2.b - c1.b) * t
        a = c1.a + (c2.a - c1.a) * t
        return Color(r, g, b, a)

    def draw_plot(self, x, y):
        end = 4
        cyan = Color(0, 1, 1, 1)
        blue = Color(0, 0, 1, 0.8)

        for i in range(1, end):
            color = self.lerp(blue, cyan, i/end)
            color_values = [color.r, color.g, color.b, color.a]
            print(color_values)
            width = 4/i
            plot = LinePlot(line_width=width, color=color_values)
            plot.points = [(x[i], y[i]) for i in range(1024)]
            # plots.append(plot)
            self.graph.add_plot(plot)


#TestApp().run()

print(LatexNodes2Text().latex_to_text(r'$\frac{1}{2}a + \frac{1}{\pi} \ \[\sum_{n=0}^i\]   \frac{\sin(2\pi\/f\/n\/x)}{n}$'))