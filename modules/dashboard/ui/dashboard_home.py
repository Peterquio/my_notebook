from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot

from core.shared.dashboard.dashboard_home_base import (
    DashboardHomeBase,
)


class DashboardHome(DashboardHomeBase):
    def __init__(self):
        super().__init__(
            title="Dashboard",
            subtitle="Visão geral do seu sistema pessoal.",
            spacing=20,
            grid_strategy="free",
        )

        self._carregar_cards_mockados()

    def _carregar_cards_mockados(self) -> None:
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