from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt

from ui.widgets.base_screen import BaseScreen
from ui.widgets.editable_dashboard_area import EditableDashboardArea
from ui.widgets.card_catalog_dialog import CardCatalogDialog

from modules.finance.services.finance_service import FinanceService
from modules.finance.ui.finance_card_generator import gerar_card_financeiro


class FinanceHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Financeiro",
            subtitle="Controle suas receitas, despesas, cartões e categorias.",
        )

        self.finance_service = FinanceService()
        self._criar_widgets()

    def _criar_widgets(self) -> None:
        self.dashboard_area = EditableDashboardArea(
            spacing=20,
        )

        self.dashboard_area.edit_mode_changed.connect(
            self.set_edit_mode
        )

        self.dashboard_area.add_card_requested.connect(
            self._abrir_seletor_cards
        )

        self.header_actions.addWidget(
            self.dashboard_area.toolbar
        )

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.dashboard_area)
        content_layout.setAlignment(Qt.AlignTop)

    def _abrir_seletor_cards(self) -> None:
        dialog = CardCatalogDialog(
            self.finance_service.listar_cards_disponiveis(),
            parent=self,
        )

        dialog.card_selected.connect(
            self._adicionar_card_financeiro
        )

        dialog.exec()

    def _adicionar_card_financeiro(
            self,
            card_data: dict,
    ) -> None:
        slot = gerar_card_financeiro(
            card_data
        )

        self.dashboard_area.add_card(
            slot,
            size=card_data.get("size", "1x1"),
        )

        slot.set_edit_mode(
            self.dashboard_area.dashboard_grid.edit_mode
        )