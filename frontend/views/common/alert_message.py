import flet as ft
import asyncio

class AlertMessage(ft.Container):
    def __init__(self, message, alert_type='info'):
        super().__init__()

        self.message = message
        self.type = alert_type
        self.alert = ft.Text(self.message, color=ft.colors.WHITE)

        self.stack = ft.Stack(
            controls=[
                ft.Container(
                    content=self.alert,
                    alignment=ft.alignment.center,
                    padding=10,
                    bgcolor=self.get_alert_color(),
                    border_radius=10,
                    width=300, 
                    height=50,
                    bottom=20,
                    left=50,
                )
            ]
        )
        self.content = self.stack

    def get_alert_color(self):
        if self.type == 'error':
            return ft.colors.RED
        elif self.type == 'success':
            return ft.colors.GREEN
        elif self.type == 'warning':
            return ft.colors.ORANGE
        else:
            return ft.colors.BLACK

    async def show_alert(self):
        self.page.controls.append(self.stack)
        self.page.update()
        await asyncio.sleep(2)
        self.page.controls.remove(self.stack)
        self.page.update()
