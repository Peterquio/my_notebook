from ui.widgets.base_screen import BaseScreen


class CalendarHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Calendário",
            subtitle="Visualize eventos, datas importantes e sua agenda.",
        )