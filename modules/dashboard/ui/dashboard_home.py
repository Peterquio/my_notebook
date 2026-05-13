from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt
from ui.widgets.dashboard_grid import DashboardGrid
from ui.widgets.base_screen import BaseScreen
from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot
from ui.widgets.dashboard_toolbar import DashboardToolbar


class DashboardHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Dashboard",
            subtitle="Visão geral do seu sistema pessoal.",
        )

        self.card_slots = []
        self._criar_widgets()

    def _criar_widgets(self) -> None:
        toolbar = DashboardToolbar()

        toolbar.edit_mode_changed.connect(
            self._toggle_edit_mode
        )

        self.header_actions.addWidget(toolbar)
        dashboard_grid = DashboardGrid(
            spacing=20,
        )

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(dashboard_grid)
        content_layout.setAlignment(Qt.AlignTop)

        cards = [
            ("Tarefas", "12", "5 vencem hoje", "📌", "3x1"),
            ("Financeiro", "R$ 2.500", "saldo previsto", "💰", "1x2"),
            ("Planner", "4", "metas ativas", "🗓️", "1x1"),
            ("Diário", "18", "registros salvos", "📖", "1x1"),
            ("Planejamento Hopi Hari", "5", "Orçamento", "🎡", "3x3")
        ]

        for index, (title, value, subtitle, icon, size) in enumerate(cards):
            card = AppCard(
                title=title,
                value=value,
                subtitle=subtitle,
                icon=icon,
            )

            slot = CardSlot(card)

            self.card_slots.append(slot)

            dashboard_grid.add_card(
                slot,
                size=size,
            )

    def _toggle_edit_mode(
            self,
            enabled: bool,
    ) -> None:

        self.set_edit_mode(enabled)

        for slot in self.card_slots:
            slot.set_edit_mode(enabled)