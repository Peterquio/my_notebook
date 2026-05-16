from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)

from core.dashboard.services.dashboard_card_catalog_controller import (
    DashboardCardCatalogController,
)

from modules.finance.dashboard.finance_dashboard_card_registry import (
    FinanceDashboardCardRegistry,
)

from modules.finance.services.credit_card_expense_service import (
    CreditCardExpenseService,
)

from modules.finance.services.credit_card_service import (
    CreditCardService,
)

from modules.finance.ui.credit_card_detail_window import (
    CreditCardDetailWindow,
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

        self.credit_card_expense_service = CreditCardExpenseService(
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
            card_generator=self.dashboard_card_registry.generate_slot,
            card_data_factory=self.dashboard_card_registry.create_new_card_data,
            dashboard_area=self.dashboard_area,
            dashboard_card_service=self.dashboard_card_service,
        )

        self.dashboard_area.add_card_requested.connect(
            self.card_catalog_controller.abrir_seletor_cards
        )

        self.header_actions.addWidget(
            self.dashboard_area.toolbar
        )

        self.btn_teste_compra_cartao = QPushButton(
            "Teste compra cartão"
        )

        self.btn_teste_compra_cartao.clicked.connect(
            self._registrar_compra_teste_cartao
        )

        self.header_actions.addWidget(
            self.btn_teste_compra_cartao
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
                slot.mouseDoubleClickEvent = lambda event, current_slot=slot: (
                    self._abrir_detalhes_cartao(current_slot)
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

    def _registrar_compra_teste_cartao(self) -> None:
        cartoes = self.credit_card_service.listar_cartoes_ativos()

        if not cartoes:
            QMessageBox.warning(
                self,
                "Nenhum cartão encontrado",
                "Crie um cartão de crédito antes de registrar uma compra teste.",
            )
            return

        cartao = cartoes[0]

        lancamentos_criados = self.credit_card_expense_service.registrar_compra(
            credit_card_id=cartao["id"],
            description="Compra teste My Notebook",
            purchase_date=date.today(),
            amount_cents=12345,
            closing_day=cartao["closing_day"],
            due_day=cartao["due_day"],
            category_id=1,
            installment_total=3,
            notes="Lançamento temporário criado pelo botão de teste.",
        )

        QMessageBox.information(
            self,
            "Compra registrada",
            (
                "Compra teste registrada com sucesso!\n\n"
                f"Cartão: {cartao['name']}\n"
                f"Parcelas criadas: {len(lancamentos_criados)}\n"
                "Valor total: R$ 123,45"
            ),
        )

        self._recarregar_dashboard()

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
            QMessageBox.warning(
                self,
                "Cartão não configurado",
                (
                    "Este card ainda não possui um cartão de crédito configurado.\n\n"
                    "Remova este card e adicione um novo cartão pelo catálogo."
                ),
            )
            return

        janela = CreditCardDetailWindow(
            credit_card=credit_card,
            parent=self,
        )

        janela.exec()