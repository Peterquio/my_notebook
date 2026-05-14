from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt

from ui.widgets.base_screen import BaseScreen
from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot
from ui.widgets.editable_dashboard_area import EditableDashboardArea


class DashboardHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Dashboard",
            subtitle="Visão geral do seu sistema pessoal.",
        )

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        self.dashboard_area = EditableDashboardArea(
            spacing=20,
        )

        self.dashboard_area.edit_mode_changed.connect(
            self.set_edit_mode
        )

        self.header_actions.addWidget(
            self.dashboard_area.toolbar
        )

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.dashboard_area)
        content_layout.setAlignment(Qt.AlignTop)

        cards = [
            ("Tarefas", "12", "5 vencem hoje", "📌", "1x1"),
            ("Financeiro", "R$ 2.500", "saldo previsto", "💰", "2x1"),
            ("Planner", "4", "metas ativas", "🗓️", "1x2"),
            ("Diário", "18", "registros salvos", "📖", "1x1"),
            ("Planejamento Hopi Hari", "5", "Orçamento", "🎡", "3x3"),
        ]

        for title, value, subtitle, icon, size in cards:
            card = AppCard(
                title=title,
                value=value,
                subtitle=subtitle,
                icon=icon,
            )

            slot = CardSlot(
                card,
                size=size,
                card_id=title.lower().replace(" ", "_"),
            )

            self.dashboard_area.add_card(
                slot,
                size=size,
            )