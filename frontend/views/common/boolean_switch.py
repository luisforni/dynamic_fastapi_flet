import flet as ft

class BooleanSwitch(ft.Row):
    def __init__(self, label, value=False, on_change=None):
        super().__init__()
        self.switch = ft.Switch(value=value, on_change=on_change)
        self.controls = [ft.Text(label), self.switch]

    def get_value(self):
        return self.switch.value
