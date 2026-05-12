from ui.widgets.base_screen import BaseScreen
from ui.widgets.app_card import AppCard


class DashboardHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Dashboard",
            subtitle="Visão geral do seu sistema pessoal.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        card = AppCard(
            self.content_area,
            title="Tarefas Pendentes",
            value="12",
            variant="random",
        )

        card.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nw",
        )