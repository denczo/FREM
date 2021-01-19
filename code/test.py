from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt
from kivy.config import Config

plt.plot([1, 23, 2, 4])
plt.ylabel('some numbers')



class MyApp(App):

    def build(self):
        box = BoxLayout(orientation='vertical', size=(640,320))
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        return box


MyApp().run()
