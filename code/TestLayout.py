from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class AdaptWidget(BoxLayout):

    def __init__(self, **kw):
        super(AdaptWidget, self).__init__(**kw)
        # but1 = Button(id='but1', text='button1')
        # but1 = ObjectProperty(None)
        # self.but1 = ObjectProperty(None)
        self.add_widget(Button(text='button1'))
        self.add_widget(Button(text='button2'))
        self.add_widget(Button(text='button3'))


    def on_size(self, *args):
        if self.width > self.height:
            self.orientation = 'horizontal'
            # self.child.but1.size_hint = (0.7, 1)
            # but1.size_hint = (0.7, 1)
            # self.ids.but1.size_hint = (0.7, 1)
            self.children[2].size_hint = (0.7, 1)
            self.children[1].size_hint = (0.5, 1)
            self.children[0].size_hint = (0.5, 1)
        else:
            self.orientation = 'vertical'
            self.children[2].size_hint = (1, 0.7)
            self.children[1].size_hint = (1, 0.5)
            self.children[0].size_hint = (1, 0.5)
        print(self.width, self.height)


class TestLayoutApp(App):
    def build(self):
        return AdaptWidget()


if __name__ == '__main__':
    TestLayoutApp().run()
