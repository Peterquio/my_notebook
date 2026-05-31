from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from core.dashboard.services.dashboard_card_catalog_controller import (
    DashboardCardCatalogController,
)

from modules.finance.dashboard.finance_dashboard_card_registry import (
    FinanceDashboardCardRegistry,
)

from modules.finance.services.credit_card_service import (
    CreditCardService,
)

from modules.finance.ui.credit_card_detail_window import (
    CreditCardDetailWindow,
)

from modules.finance.ui.balance_detail_window import (
    BalanceDetailWindow,
)

from modules.finance.services.balance_service import (
    BalanceService,
)

from modules.finance.ui.dialogs.finance_welcome_dialog import (
    FinanceWelcomeDialog,
)

from modules.finance.ui.dialogs.balance_initial_cycle_dialog import (
    BalanceInitialCycleDialog,
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

        self.dashboard_card_registry = FinanceDashboardCardRegistry(
            card_generator=gerar_card_financeiro,
            credit_card_service=self.credit_card_service,
        )

        DatabaseManager(
            self.username
        ).inicializar_banco_usuario()

        self.balance_service = BalanceService(
            self.username
        )

        self._garantir_onboarding_financeiro()

        self.dashboard_layout_service = DashboardLayoutService(
            self.username
        )

        self.dashboard_card_service = DashboardCardService(
            self.username
        )

        self.card_catalog_controller = None

        self._criar_widgets()

    def _garantir_onboarding_financeiro(self) -> None:
        ciclos = self.balance_service.listar_ciclos()

        if ciclos:
            return

        welcome_dialog = FinanceWelcomeDialog(
            parent=self,
        )

        if welcome_dialog.exec() != FinanceWelcomeDialog.Accepted:
            return

        cycle_dialog = BalanceInitialCycleDialog(
            parent=self,
        )

        if cycle_dialog.exec() != BalanceInitialCycleDialog.Accepted:
            return

        dados = cycle_dialog.obter_dados()

        self.balance_service.criar_ciclo(
            name=dados["name"],
            start_date=dados["start_date"],
            end_date=dados["end_date"],
        )

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
            card_generator=self.dashboard_card_registry.generate_slot,
            card_data_factory=self.dashboard_card_registry.create_new_card_data,
            dashboard_area=self.dashboard_area,
            dashboard_card_service=self.dashboard_card_service,
            on_slot_created=self._on_dashboard_slot_created,
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
        layout_salvo = self.dashboard_layout_service.carregar_layout(
            module_name="finance"
        )

        if not layout_salvo:
            return

        catalog_by_type = {
            card["id"]: card
            for card in FINANCE_CARD_CATALOG
        }

        for item in layout_salvo:
            template = catalog_by_type.get(
                item["card_type"],
                {}
            )

            card_data = self.dashboard_card_registry.hydrate_card_data(
                layout_item=item,
                template_data=template,
            )

            slot = self.dashboard_card_registry.generate_slot(
                card_data
            )

            if item["card_type"] == "credit_card":
                self._conectar_abertura_card_cartao(
                    slot
                )

            if item["card_type"] == "balance":
                self._conectar_abertura_card_saldo(
                    slot
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

    def _recarregar_dashboard(self) -> None:
        for slot in list(self.dashboard_area.card_slots):
            self.dashboard_area.dashboard_grid.remove_card(
                slot
            )

        self.dashboard_area.card_slots.clear()

        self._carregar_layout_dashboard()

    def _abrir_detalhes_cartao(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        credit_card = self.credit_card_service.buscar_por_dashboard_card_id(
            slot.card_id
        )

        if credit_card is None:
            return

        self.credit_card_detail_page = CreditCardDetailWindow(
            credit_card=credit_card,
            username=self.username,
            parent=self.window(),
        )

        self.credit_card_detail_page.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.credit_card_detail_page.data_changed.connect(
            self._recarregar_dashboard
        )

        self.window().entrar_modo_foco(
            self.credit_card_detail_page
        )

    def _conectar_abertura_card_cartao(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot: self._abrir_detalhes_cartao(
                current_slot
            )
        )

    def _abrir_detalhes_saldo(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        self.balance_detail_page = BalanceDetailWindow(
            username=self.username,
            parent=self.window(),
        )

        self.balance_detail_page.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.balance_detail_page.data_changed.connect(
            self._recarregar_dashboard
        )

        self.window().entrar_modo_foco(
            self.balance_detail_page
        )

    def _conectar_abertura_card_saldo(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot: self._abrir_detalhes_saldo(
                current_slot
            )
        )

    def _on_dashboard_slot_created(
            self,
            slot,
    ) -> None:

        card_type = getattr(
            slot,
            "card_type",
            None,
        )

        if card_type == "credit_card":
            self._conectar_abertura_card_cartao(
                slot
            )
            return

        if card_type == "balance":
            self._conectar_abertura_card_saldo(
                slot
            )
            return

    def _voltar_para_dashboard_financeiro(self) -> None:
        self.window().sair_modo_foco()

        self.credit_card_detail_page = None

        if hasattr(self, "balance_detail_page"):
            self.balance_detail_page = None

        self._recarregar_dashboard()