from kivy.app import App
from kivy.uix.button import Button
from functools import partial

class FirstKivy(App):
    def disable(self, instance, *args):
        instance.disabled = abs
    def updatetext(self, instance, *ars):
        instance.text = "Button Disabled!"
    def build(self):
        mybtn = Button(text="Click to disable.")
        mybtn.bind(on_press=partial(self.disable, mybtn))
        mybtn.bind(on_press=partial(self.updatetext, mybtn))
        return mybtn

FirstKivy().run()