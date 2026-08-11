from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout
from core.dashboard.services.dashboard_card_catalog_controller import DashboardCardCatalogController
from modules.finance.dashboard.finance_dashboard_card_registry import FinanceDashboardCardRegistry
from modules.finance.services.credit_card_service import CreditCardService
from modules.finance.ui.credit_card_detail_window import CreditCardDetailWindow
from modules.finance.ui.balance_detail_window import BalanceDetailWindow
from modules.finance.ui.account_detail_window import AccountDetailWindow
from modules.finance.services.balance_service import BalanceService
from modules.finance.ui.dialogs.finance_welcome_dialog import FinanceWelcomeDialog
from modules.finance.ui.dialogs.balance_initial_cycle_dialog import BalanceInitialCycleDialog
from modules.finance.services.finance_balance_opening_service import FinanceBalanceOpeningService
from modules.finance.services.balance_account_service import BalanceAccountService
from modules.finance.repositories.finance_settings_repository import FinanceSettingsRepository
from modules.finance.ui.subscriptions_page import SubscriptionsPage
from modules.finance.ui.calculator_window import CalculatorWindow
from modules.finance.ui.pix_window import PixWindow
from core.shared.dashboard.dashboard_home_base import DashboardHomeBase
from core.dashboard.services.dashboard_layout_service import DashboardLayoutService
from core.dashboard.services.dashboard_card_service import DashboardCardService
from core.database.database_manager import DatabaseManager

from modules.finance.services.finance_service import FinanceService
from modules.finance.ui.finance_card_generator import gerar_card_financeiro
from modules.finance.cards.finance_card_catalog import FINANCE_CARD_CATALOG

class FinanceHome(DashboardHomeBase):
    def __init__(self):
        super().__init__(
            title="Financeiro",
            subtitle="Controle suas receitas, despesas, cartões e categorias.",
            spacing=20,
            grid_strategy="free",
        )

        self.finance_service = FinanceService()
        self.username = "default"

        self.credit_card_service = CreditCardService(
            self.username
        )

        self.dashboard_card_registry = FinanceDashboardCardRegistry(
            card_generator=gerar_card_financeiro,
            credit_card_service=self.credit_card_service,
            username=self.username,
        )

        DatabaseManager(
            self.username
        ).inicializar_banco_usuario()

        self.balance_service = BalanceService(
            self.username
        )

        self.balance_account_service = BalanceAccountService(
            self.username
        )

        self.finance_balance_opening_service = (
            FinanceBalanceOpeningService(
                self.username
            )
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
        settings_repository = FinanceSettingsRepository(
            self.username
        )

        reference_day = (
            settings_repository
            .obter_reference_day()
        )

        if reference_day is not None:
            return

        welcome_dialog = FinanceWelcomeDialog(
            parent=self,
        )

        if (
                welcome_dialog.exec()
                != FinanceWelcomeDialog.Accepted
        ):
            return

        cycle_dialog = BalanceInitialCycleDialog(
            parent=self,
        )

        if (
                cycle_dialog.exec()
                != BalanceInitialCycleDialog.Accepted
        ):
            return

        dados = cycle_dialog.obter_dados()

        settings_repository.salvar_reference_day(
            dados["reference_day"]
        )

    def _criar_widgets(self) -> None:
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

            if item["card_type"] == "account_balance":
                self._conectar_abertura_card_conta(
                    slot
                )

            if item["card_type"] == "subscriptions":
                self._conectar_abertura_card_assinaturas(
                    slot
                )

            if item["card_type"] == "calculator":
                self._conectar_abertura_card_calculadora(
                    slot
                )

            if item["card_type"] == "pix_sheet":
                self._conectar_abertura_card_pix(
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

        self.finance_balance_opening_service.preparar_abertura_saldo()

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

    def _abrir_detalhes_conta(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        conta = self.balance_account_service.buscar_por_dashboard_card_id(
            slot.card_id
        )

        if conta is None:
            return

        self.account_detail_page = AccountDetailWindow(
            account=conta,
            username=self.username,
            parent=self.window(),
        )

        self.account_detail_page.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.account_detail_page.data_changed.connect(
            self._recarregar_dashboard
        )

        self.window().entrar_modo_foco(
            self.account_detail_page
        )

    def _conectar_abertura_card_conta(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot: self._abrir_detalhes_conta(
                current_slot
            )
        )

    def _abrir_detalhes_assinaturas(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        self.subscriptions_page = SubscriptionsPage(
            username=self.username,
            parent=self.window(),
        )

        self.subscriptions_page.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.subscriptions_page.data_changed.connect(
            self._recarregar_dashboard
        )

        self.window().entrar_modo_foco(
            self.subscriptions_page
        )

    def _conectar_abertura_card_assinaturas(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot:
            self._abrir_detalhes_assinaturas(
                current_slot
            )
        )

    def _abrir_pix(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        self.pix_window = PixWindow(
            username=self.username,
            parent=self.window(),
        )

        self.pix_window.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.pix_window.data_changed.connect(
            self._recarregar_dashboard
        )

        self.window().entrar_modo_foco(
            self.pix_window
        )

    def _conectar_abertura_card_pix(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot:
            self._abrir_pix(
                current_slot
            )
        )

    def _abrir_calculadora(
            self,
            slot,
    ) -> None:

        if self.edit_mode:
            return

        self.calculator_window = CalculatorWindow(
            username=self.username,
            parent=self.window(),
        )

        self.calculator_window.back_requested.connect(
            self._voltar_para_dashboard_financeiro
        )

        self.window().entrar_modo_foco(
            self.calculator_window
        )

    def _conectar_abertura_card_calculadora(
            self,
            slot,
    ) -> None:

        try:
            slot.clicked.disconnect()
        except RuntimeError:
            pass

        slot.clicked.connect(
            lambda current_slot=slot: self._abrir_calculadora(
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

        if card_type == "account_balance":
            self._conectar_abertura_card_conta(
                slot
            )
            return

        if card_type == "subscriptions":
            self._conectar_abertura_card_assinaturas(
                slot
            )
            return

        if card_type == "calculator":
            self._conectar_abertura_card_calculadora(
                slot
            )
            return

        if card_type == "pix_sheet":
            self._conectar_abertura_card_pix(
                slot
            )
            return

    def _voltar_para_dashboard_financeiro(self) -> None:
        self.window().sair_modo_foco()

        self.credit_card_detail_page = None

        if hasattr(self, "balance_detail_page"):
            self.balance_detail_page = None

        if hasattr(self, "account_detail_page"):
            self.account_detail_page = None

        self._recarregar_dashboard()