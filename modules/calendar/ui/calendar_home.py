from ui.widgets.base_screen import BaseScreen


class CalendarHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Calendário",
            subtitle="Visualize eventos, datas importantes e sua agenda.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        pass