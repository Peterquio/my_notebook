from ui.widgets.base_screen import BaseScreen


class DiaryHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Diário",
            subtitle="Registre pensamentos, ideias e acontecimentos.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        pass