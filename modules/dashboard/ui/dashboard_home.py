from ui.widgets.base_screen import BaseScreen
from ui.widgets.app_card import AppCard
from ui.widgets.editable_card_grid import EditableCardGrid
from ui.widgets.add_card_button import AddCardButton
from ui.widgets.dashboard_toolbar import DashboardToolbar

class DashboardHome(BaseScreen):
    def __init__(self, master):
        super().__init__(
            master,
            title="Dashboard",
            subtitle="Visão geral do seu sistema pessoal.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        toolbar = DashboardToolbar(
            self.header_actions,
            on_toggle_edit=self._toggle_edit_mode,
        )

        toolbar.pack()

        self.card_grid = EditableCardGrid(
            self.content_area,
            columns=4,
        )

        self.card_grid.grid(
            row=0,
            column=0,
            sticky="nw",
        )

        cards = [
            ("Tarefas", "12", "5 vencem hoje", "📌", "1x1"),
            ("Financeiro", "R$ 2.500", "saldo previsto", "💰", "2x1"),
            ("Planner", "4", "metas ativas", "🗓️", "1x2"),
            ("Diário", "18", "registros", "📖", "2x1"),
            ("Calendário", "13/05", "15 dias sem fumar", "🚭", "1x1"),
        ]

        for title, value, subtitle, icon, size in cards:
            card = AppCard(
                self.card_grid,
                title=title,
                value=value,
                subtitle=subtitle,
                icon=icon,
                variant="random",
                clickable=True,
            )

            self.card_grid.add_card(
                card,
                size=size,
            )

        add_card = AddCardButton(
            self.card_grid,
            command=lambda: print("Adicionar novo card"),
        )

        self.card_grid.add_card(
            add_card,
            size="1x1",
        )

    def _toggle_edit_mode(self, enabled: bool) -> None:
        self.set_edit_mode(enabled)
        self.card_grid.set_edit_mode(enabled)