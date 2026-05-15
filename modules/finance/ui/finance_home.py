from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from core.dashboard.services.dashboard_card_catalog_controller import (
    DashboardCardCatalogController,
)
from modules.finance.services.credit_card_service import (
    CreditCardService,
)
from ui.widgets.base_screen import BaseScreen
from ui.widgets.editable_dashboard_area import EditableDashboardArea

from core.dashboard.services.dashboard_layout_service import DashboardLayoutService
from core.dashboard.services.dashboard_card_service import DashboardCardService
from core.database.database_manager import DatabaseManager

from modules.finance.services.finance_service import FinanceService
from modules.finance.ui.finance_card_generator import gerar_card_financeiro
from modules.finance.cards.finance_card_catalog import FINANCE_CARD_CATALOG


class FinanceHome(BaseScreen):
    def __init__(self):
        super().__init__(
            title="Financeiro",
            subtitle="Controle suas receitas, despesas, cartões e categorias.",
        )

        self.finance_service = FinanceService()
        self.username = "default"

        self.credit_card_service = CreditCardService(
            self.username
        )

        DatabaseManager(
            self.username
        ).inicializar_banco_usuario()

        self.dashboard_layout_service = DashboardLayoutService(
            self.username
        )

        self.dashboard_card_service = DashboardCardService(
            self.username
        )

        self.card_catalog_controller = None

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        self.dashboard_area = EditableDashboardArea(
            spacing=20,
            on_save_layout=self._salvar_layout_dashboard,
        )

        self.dashboard_area.edit_mode_changed.connect(
            self.set_edit_mode
        )

        self.card_catalog_controller = DashboardCardCatalogController(
            parent=self,
            module_name="finance",
            catalog_provider=self.finance_service.listar_cards_disponiveis,
            card_generator=gerar_card_financeiro,
            dashboard_area=self.dashboard_area,
            dashboard_card_service=self.dashboard_card_service,
        )

        self.dashboard_area.add_card_requested.connect(
            self.card_catalog_controller.abrir_seletor_cards
        )

        self.header_actions.addWidget(
            self.dashboard_area.toolbar
        )

        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.dashboard_area)
        content_layout.setAlignment(Qt.AlignTop)

        self._carregar_layout_dashboard()

    def _salvar_layout_dashboard(
            self,
            layout_items: list[dict],
    ) -> None:
        self.dashboard_layout_service.salvar_layout(
            module_name="finance",
            layout_items=layout_items,
        )

        print("[FINANCE] Layout salvo no SQLite.")

    def _carregar_layout_dashboard(self) -> None:
        layout_items = self.dashboard_layout_service.carregar_layout(
            module_name="finance",
        )

        catalog_by_type = {
            card["id"]: card
            for card in FINANCE_CARD_CATALOG
        }

        for item in layout_items:
            template = catalog_by_type.get(
                item["card_type"],
                {}
            )

            card_data = {
                "id": item["card_id"],
                "card_type": item["card_type"],
                "config": item.get("config", {}),

                "title": template.get("title", item["card_type"]),
                "subtitle": template.get("subtitle", ""),
                "icon": template.get("icon", ""),
                "size": template.get(
                    "size",
                    f'{item["width_units"]}x{item["height_units"]}',
                ),
            }

            slot = gerar_card_financeiro(
                card_data
            )

            slot.delete_requested.connect(
                self.dashboard_card_service.remover_ou_desativar_card
            )

            self.dashboard_area.add_card_at(
                slot,
                row=item["row"],
                column=item["column"],
                width_units=item["width_units"],
                height_units=item["height_units"],
            )