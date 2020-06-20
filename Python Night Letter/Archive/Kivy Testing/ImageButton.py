from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_file("mod file.kv")

class KivyButton(App, BoxLayout):
    def build(self):
        return self

KivyButton().run()