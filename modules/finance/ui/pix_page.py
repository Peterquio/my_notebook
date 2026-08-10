from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.shared.dashboard.dashboard_grid import (
    DashboardGrid,
)

from ui.widgets.card_slot import (
    CardSlot,
)

from modules.finance.repositories.finance_category_repository import (
    FinanceCategoryRepository,
)

from modules.finance.services.balance_account_service import (
    BalanceAccountService,
)

from modules.finance.services.pix_service import (
    PixService,
)

from modules.finance.ui.dialogs.pix_transaction_dialog import (
    PixTransactionDialog,
)

from modules.finance.ui.widget.pix_transaction_card import (
    PixTransactionCard,
)


class PixPage(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username

        self.pix_service = PixService(
            username
        )

        self.account_service = BalanceAccountService(
            username
        )

        self.category_repository = (
            FinanceCategoryRepository(
                username
            )
        )

        self.setObjectName(
            "PixPage"
        )

        self._aplicar_estilo()
        self._montar_interface()
        self._carregar_transacoes()

    # =========================================================
    # INTERFACE
    # =========================================================

    def _montar_interface(
            self,
    ) -> None:

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        main_layout.setSpacing(
            20
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        back_button = QPushButton(
            "←"
        )

        back_button.setObjectName(
            "PixBackButton"
        )

        back_button.setFixedSize(
            40,
            40,
        )

        back_button.clicked.connect(
            self.back_requested.emit
        )

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel(
            "PIX"
        )

        title.setObjectName(
            "PixPageTitle"
        )

        subtitle = QLabel(
            "Acompanhe seus PIX enviados e recebidos."
        )

        subtitle.setObjectName(
            "PixPageSubtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        new_button = QPushButton(
            "+ Novo PIX"
        )

        new_button.setObjectName(
            "PixPrimaryButton"
        )

        new_button.setMinimumHeight(
            40
        )

        new_button.clicked.connect(
            self._novo_pix
        )

        header_layout.addWidget(
            back_button
        )

        header_layout.addLayout(
            title_layout
        )

        header_layout.addStretch()

        header_layout.addWidget(
            new_button
        )

        main_layout.addLayout(
            header_layout
        )

        # -----------------------------------------------------
        # RESUMO
        # -----------------------------------------------------

        self.summary_frame = QFrame()

        self.summary_frame.setObjectName(
            "PixSummaryFrame"
        )

        summary_layout = QHBoxLayout(
            self.summary_frame
        )

        summary_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        summary_layout.setSpacing(
            24
        )

        # Período

        period_container = QWidget()

        period_layout = QVBoxLayout(
            period_container
        )

        period_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        period_layout.setSpacing(
            4
        )

        period_title = QLabel(
            "PERÍODO FINANCEIRO"
        )

        period_title.setObjectName(
            "PixSummaryCaption"
        )

        self.period_value = QLabel(
            "--"
        )

        self.period_value.setObjectName(
            "PixSummaryPeriod"
        )

        period_layout.addWidget(
            period_title
        )

        period_layout.addWidget(
            self.period_value
        )

        # Enviados

        sent_container = QWidget()

        sent_layout = QVBoxLayout(
            sent_container
        )

        sent_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        sent_layout.setSpacing(
            4
        )

        sent_title = QLabel(
            "ENVIADOS"
        )

        sent_title.setObjectName(
            "PixSummaryCaption"
        )

        self.sent_value = QLabel(
            "R$ 0,00"
        )

        self.sent_value.setObjectName(
            "PixSummarySent"
        )

        sent_layout.addWidget(
            sent_title
        )

        sent_layout.addWidget(
            self.sent_value
        )

        # Recebidos

        received_container = QWidget()

        received_layout = QVBoxLayout(
            received_container
        )

        received_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        received_layout.setSpacing(
            4
        )

        received_title = QLabel(
            "RECEBIDOS"
        )

        received_title.setObjectName(
            "PixSummaryCaption"
        )

        self.received_value = QLabel(
            "R$ 0,00"
        )

        self.received_value.setObjectName(
            "PixSummaryReceived"
        )

        received_layout.addWidget(
            received_title
        )

        received_layout.addWidget(
            self.received_value
        )

        summary_layout.addWidget(
            period_container,
            2,
        )

        summary_layout.addWidget(
            sent_container,
            1,
        )

        summary_layout.addWidget(
            received_container,
            1,
        )

        main_layout.addWidget(
            self.summary_frame
        )

        # -----------------------------------------------------
        # SCROLL
        # -----------------------------------------------------

        self.scroll_area = QScrollArea()

        self.scroll_area.setObjectName(
            "PixScrollArea"
        )

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_content = QWidget()

        self.scroll_content.setObjectName(
            "PixScrollContent"
        )

        self.transactions_layout = QVBoxLayout(
            self.scroll_content
        )

        self.transactions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.transactions_layout.setSpacing(
            28
        )

        self.transactions_layout.setAlignment(
            Qt.AlignTop
        )

        self.scroll_area.setWidget(
            self.scroll_content
        )

        main_layout.addWidget(
            self.scroll_area,
            1,
        )

    # =========================================================
    # CARREGAMENTO
    # =========================================================

    def _carregar_transacoes(
            self,
    ) -> None:

        self._limpar_transacoes()

        self._atualizar_resumo()

        grupos = (
            self.pix_service
            .listar_transacoes_agrupadas_por_mes()
        )

        if not grupos:
            self._mostrar_estado_vazio()
            return

        for grupo in grupos:
            self._adicionar_grupo_mes(
                grupo
            )

        self.transactions_layout.addStretch()

    def _atualizar_resumo(
            self,
    ) -> None:

        resumo = (
            self.pix_service
            .obter_resumo_periodo_atual()
        )

        self.period_value.setText(
            self._formatar_periodo(
                resumo["start_date"],
                resumo["end_date"],
            )
        )

        self.sent_value.setText(
            self._formatar_moeda(
                resumo["sent_cents"]
            )
        )

        self.received_value.setText(
            self._formatar_moeda(
                resumo["received_cents"]
            )
        )

    # =========================================================
    # GRUPO MENSAL
    # =========================================================

    def _adicionar_grupo_mes(
            self,
            grupo: dict,
    ) -> None:

        section = QWidget()

        section.setObjectName(
            "PixMonthSection"
        )

        section_layout = QVBoxLayout(
            section
        )

        section_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        section_layout.setSpacing(
            12
        )

        # -----------------------------------------------------
        # HEADER DO MÊS
        # -----------------------------------------------------

        month_header = QHBoxLayout()

        month_header.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        month_header.setSpacing(
            12
        )

        month_label = QLabel(
            f'{grupo["month_name"]} '
            f'{grupo["year"]}'
        )

        month_label.setObjectName(
            "PixMonthTitle"
        )

        quantidade = len(
            grupo["transactions"]
        )

        if quantidade == 1:
            quantidade_texto = (
                "1 movimentação"
            )
        else:
            quantidade_texto = (
                f"{quantidade} movimentações"
            )

        count_label = QLabel(
            quantidade_texto
        )

        count_label.setObjectName(
            "PixMonthCount"
        )

        month_header.addWidget(
            month_label
        )

        month_header.addStretch()

        month_header.addWidget(
            count_label
        )

        section_layout.addLayout(
            month_header
        )

        # -----------------------------------------------------
        # BOARD DO MÊS
        # -----------------------------------------------------

        grid = DashboardGrid(
            min_cell_width=170,
            max_cell_width=190,
            cell_ratio=0.78,
            spacing=12,
            strategy="sequential",
            min_columns=1,
            max_columns=6,
        )

        grid.setObjectName(
            "PixMonthGrid"
        )

        for transaction in grupo[
            "transactions"
        ]:

            card = PixTransactionCard(
                transaction_data=transaction,
            )

            slot = CardSlot(
                card,
                size="1x1",
                card_id=str(
                    transaction["id"]
                ),
            )

            slot.card_type = (
                "pix_transaction"
            )

            slot.card_config = (
                transaction
            )

            slot.clicked.connect(
                lambda current_transaction=transaction:
                self._editar_pix(
                    current_transaction
                )
            )

            slot.delete_requested.connect(
                lambda _card_id,
                       _config,
                       current_transaction=transaction:
                self._excluir_pix(
                    current_transaction
                )
            )

            grid.add_card(
                slot,
                size="1x1",
            )

        section_layout.addWidget(
            grid
        )

        self.transactions_layout.addWidget(
            section
        )

    # =========================================================
    # ESTADO VAZIO
    # =========================================================

    def _mostrar_estado_vazio(
            self,
    ) -> None:

        empty_container = QFrame()

        empty_container.setObjectName(
            "PixEmptyState"
        )

        empty_layout = QVBoxLayout(
            empty_container
        )

        empty_layout.setContentsMargins(
            30,
            36,
            30,
            36,
        )

        empty_layout.setSpacing(
            8
        )

        empty_layout.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            "Nenhum PIX lançado"
        )

        title.setObjectName(
            "PixEmptyTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        description = QLabel(
            "Seus PIX enviados e recebidos "
            "aparecerão aqui."
        )

        description.setObjectName(
            "PixEmptyDescription"
        )

        description.setAlignment(
            Qt.AlignCenter
        )

        button = QPushButton(
            "+ Adicionar primeiro PIX"
        )

        button.setObjectName(
            "PixPrimaryButton"
        )

        button.clicked.connect(
            self._novo_pix
        )

        empty_layout.addWidget(
            title
        )

        empty_layout.addWidget(
            description
        )

        empty_layout.addSpacing(
            8
        )

        empty_layout.addWidget(
            button,
            alignment=Qt.AlignCenter,
        )

        self.transactions_layout.addWidget(
            empty_container
        )

    # =========================================================
    # DIÁLOGOS
    # =========================================================

    def _obter_dados_dialogo(
            self,
    ) -> tuple[list[dict], list[dict]]:

        accounts = (
            self.account_service
            .listar_contas()
        )

        categories = (
            self.category_repository
            .listar_ativas()
        )

        return (
            accounts,
            categories,
        )

    def _novo_pix(
            self,
    ) -> None:

        accounts, categories = (
            self._obter_dados_dialogo()
        )

        if not accounts:
            QMessageBox.warning(
                self,
                "Nenhuma conta cadastrada",
                (
                    "Cadastre uma conta financeira "
                    "antes de lançar um PIX."
                ),
            )
            return

        dialog = PixTransactionDialog(
            accounts=accounts,
            categories=categories,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.Accepted
        ):
            return

        dados = (
            dialog.obter_dados()
        )

        try:
            self.pix_service.criar_transacao(
                **dados
            )

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "Não foi possível salvar",
                str(erro),
            )
            return

        self._carregar_transacoes()

        self.data_changed.emit()

    def _editar_pix(
            self,
            transaction_data: dict,
    ) -> None:

        accounts, categories = (
            self._obter_dados_dialogo()
        )

        dialog = PixTransactionDialog(
            accounts=accounts,
            categories=categories,
            transaction_data=transaction_data,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.Accepted
        ):
            return

        dados = (
            dialog.obter_dados()
        )

        try:
            self.pix_service.atualizar_transacao(
                transaction_id=(
                    transaction_data["id"]
                ),
                **dados,
            )

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "Não foi possível atualizar",
                str(erro),
            )
            return

        self._carregar_transacoes()

        self.data_changed.emit()

    def _excluir_pix(
            self,
            transaction_data: dict,
    ) -> None:

        nome = (
            transaction_data.get(
                "contact_name"
            )
            or transaction_data.get(
                "description"
            )
            or "este PIX"
        )

        resposta = QMessageBox.question(
            self,
            "Excluir PIX",
            (
                f'Deseja realmente excluir '
                f'"{nome}"?'
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.pix_service.excluir_transacao(
                transaction_data["id"]
            )

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "Não foi possível excluir",
                str(erro),
            )
            return

        self._carregar_transacoes()

        self.data_changed.emit()

    # =========================================================
    # LIMPEZA
    # =========================================================

    def _limpar_transacoes(
            self,
    ) -> None:

        while self.transactions_layout.count():
            item = (
                self.transactions_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    # =========================================================
    # FORMATAÇÃO
    # =========================================================

    def _formatar_moeda(
            self,
            valor_cents: int,
    ) -> str:

        valor = (
            int(valor_cents or 0)
            / 100
        )

        texto = (
            f"{valor:,.2f}"
        )

        texto = (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"R$ {texto}"
        )

    def _formatar_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> str:

        meses = {
            1: "jan",
            2: "fev",
            3: "mar",
            4: "abr",
            5: "mai",
            6: "jun",
            7: "jul",
            8: "ago",
            9: "set",
            10: "out",
            11: "nov",
            12: "dez",
        }

        inicio = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        )

        fim = datetime.strptime(
            end_date,
            "%Y-%m-%d",
        )

        return (
            f"{inicio.day:02d} "
            f"{meses[inicio.month]} "
            f"— "
            f"{fim.day:02d} "
            f"{meses[fim.month]}"
        )

    # =========================================================
    # ESTILO
    # =========================================================

    def _aplicar_estilo(
            self,
    ) -> None:

        self.setStyleSheet(
            """
            QWidget#PixPage {
                background-color: #f8fafc;
                color: #0f172a;
            }

            QWidget#PixScrollContent {
                background-color: transparent;
            }

            QScrollArea#PixScrollArea {
                background-color: transparent;
                border: none;
            }

            QLabel#PixPageTitle {
                color: #0f172a;
                font-size: 26px;
                font-weight: 700;
            }

            QLabel#PixPageSubtitle {
                color: #64748b;
                font-size: 13px;
            }

            QPushButton#PixBackButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                color: #475569;
                font-size: 18px;
            }

            QPushButton#PixBackButton:hover {
                background-color: #f1f5f9;
                border-color: #cbd5e1;
            }

            QPushButton#PixPrimaryButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 9px 16px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#PixPrimaryButton:hover {
                background-color: #1d4ed8;
            }

            QFrame#PixSummaryFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }

            QLabel#PixSummaryCaption {
                color: #94a3b8;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#PixSummaryPeriod {
                color: #334155;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#PixSummarySent {
                color: #dc2626;
                font-size: 20px;
                font-weight: 700;
            }

            QLabel#PixSummaryReceived {
                color: #16a34a;
                font-size: 20px;
                font-weight: 700;
            }

            QLabel#PixMonthTitle {
                color: #334155;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#PixMonthCount {
                color: #94a3b8;
                font-size: 12px;
            }

            QFrame#PixEmptyState {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }

            QLabel#PixEmptyTitle {
                color: #334155;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#PixEmptyDescription {
                color: #64748b;
                font-size: 13px;
            }
            """
        )