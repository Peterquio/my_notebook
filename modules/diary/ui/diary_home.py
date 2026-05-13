from ui.widgets.base_screen import BaseScreen


class DiaryHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Diário",
            subtitle="Registre pensamentos, ideias e acontecimentos.",
        )