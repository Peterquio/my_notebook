from PySide6.QtWidgets import QGridLayout

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
        layout = QGridLayout(self.content_area)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        cards = [
            ("Tarefas", "12", "5 vencem hoje", "📌"),
            ("Financeiro", "R$ 2.500", "saldo previsto", "💰"),
            ("Planner", "4", "metas ativas", "🗓️"),
            ("Diário", "18", "registros salvos", "📖"),
        ]

        for index, (title, value, subtitle, icon) in enumerate(cards):
            card = AppCard(
                title=title,
                value=value,
                subtitle=subtitle,
                icon=icon,
            )

            row = index // 2
            column = index % 2

            slot = CardSlot(card)
            self.card_slots.append(slot)
            layout.addWidget(slot, row, column)

    def _toggle_edit_mode(
            self,
            enabled: bool,
    ) -> None:

        self.set_edit_mode(enabled)

        for slot in self.card_slots:
            slot.set_edit_mode(enabled)