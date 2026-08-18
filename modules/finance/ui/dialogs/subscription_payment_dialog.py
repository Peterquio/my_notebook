from PySide6.QtCore import (
    Qt,
)

from PySide6.QtWidgets import (
    QComboBox,
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

from modules.finance.services.pix_service import (
    PixService,
)

from modules.finance.services.credit_card_service import (
    CreditCardService,
)

from modules.finance.services.credit_card_detail_service import (
    CreditCardDetailService,
)


class SubscriptionPaymentDialog(QDialog):
    SOURCE_PIX = "pix"
    SOURCE_CREDIT_CARD = "credit_card"

    def __init__(
            self,
            username: str,
            subscription: dict,
            reference_year: int,
            reference_month: int,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username
        self.subscription = subscription

        self.reference_year = reference_year
        self.reference_month = reference_month

        self.pix_service = PixService(
            username
        )

        self.credit_card_service = (
            CreditCardService(
                username
            )
        )

        self.credit_card_detail_service = (
            CreditCardDetailService(
                username
            )
        )

        self.credit_cards = []
        self.selected_source = self.SOURCE_PIX
        self.selected_payment_id = None

        self.setWindowTitle(
            "Vincular pagamento"
        )

        self.setFixedSize(
            580,
            560,
        )

        self._montar_interface()
        self._aplicar_estilo()

        self._selecionar_origem(
            self.SOURCE_PIX
        )

    # =========================================================
    # INTERFACE
    # =========================================================

    def _montar_interface(
            self,
    ) -> None:

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            22,
            20,
            22,
            20,
        )

        layout.setSpacing(
            12
        )

        titulo = QLabel(
            "Já pagou?"
        )

        titulo.setObjectName(
            "Title"
        )

        layout.addWidget(
            titulo
        )

        assinatura = QLabel(
            self.subscription["name"]
        )

        assinatura.setObjectName(
            "SubscriptionName"
        )

        layout.addWidget(
            assinatura
        )

        referencia = QLabel(
            (
                f"Referência: "
                f"{self.reference_month:02d}/"
                f"{self.reference_year}"
            )
        )

        referencia.setObjectName(
            "Reference"
        )

        layout.addWidget(
            referencia
        )

        # -----------------------------------------------------
        # PIX / CARTÃO
        # -----------------------------------------------------

        source_layout = QHBoxLayout()
        source_layout.setSpacing(8)

        self.pix_button = QPushButton(
            "PIX"
        )

        self.card_button = QPushButton(
            "Cartão de Crédito"
        )

        self.pix_button.setCheckable(
            True
        )

        self.card_button.setCheckable(
            True
        )

        self.pix_button.clicked.connect(
            lambda:
            self._selecionar_origem(
                self.SOURCE_PIX
            )
        )

        self.card_button.clicked.connect(
            lambda:
            self._selecionar_origem(
                self.SOURCE_CREDIT_CARD
            )
        )

        source_layout.addWidget(
            self.pix_button
        )

        source_layout.addWidget(
            self.card_button
        )

        layout.addLayout(
            source_layout
        )

        # -----------------------------------------------------
        # FILTROS
        # -----------------------------------------------------

        self.filters_container = QWidget()

        self.filters_layout = QHBoxLayout(
            self.filters_container
        )

        self.filters_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.filters_layout.setSpacing(
            8
        )

        layout.addWidget(
            self.filters_container
        )

        # -----------------------------------------------------
        # RESULTADOS
        # -----------------------------------------------------

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.results_container = QWidget()

        self.results_layout = QVBoxLayout(
            self.results_container
        )

        self.results_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.results_layout.setSpacing(
            7
        )

        self.results_layout.addStretch()

        self.scroll.setWidget(
            self.results_container
        )

        layout.addWidget(
            self.scroll,
            1,
        )

        # -----------------------------------------------------
        # FOOTER
        # -----------------------------------------------------

        footer = QHBoxLayout()

        footer.addStretch()

        cancelar = QPushButton(
            "Cancelar"
        )

        cancelar.clicked.connect(
            self.reject
        )

        self.confirm_button = QPushButton(
            "Vincular"
        )

        self.confirm_button.setObjectName(
            "ConfirmButton"
        )

        self.confirm_button.setEnabled(
            False
        )

        self.confirm_button.clicked.connect(
            self._confirmar
        )

        footer.addWidget(
            cancelar
        )

        footer.addWidget(
            self.confirm_button
        )

        layout.addLayout(
            footer
        )

    # =========================================================
    # ORIGEM
    # =========================================================

    def _selecionar_origem(
            self,
            source: str,
    ) -> None:

        self.selected_source = source
        self.selected_payment_id = None

        self.confirm_button.setEnabled(
            False
        )

        self.pix_button.setChecked(
            source == self.SOURCE_PIX
        )

        self.card_button.setChecked(
            source == self.SOURCE_CREDIT_CARD
        )

        self._limpar_filtros()
        self._limpar_resultados()

        if source == self.SOURCE_PIX:
            self._carregar_pix()
            return

        self._montar_filtros_cartao()

    # =========================================================
    # PIX
    # =========================================================

    def _carregar_pix(
            self,
    ) -> None:

        info = QLabel(
            "Selecione o PIX correspondente ao pagamento."
        )

        info.setObjectName(
            "Hint"
        )

        self.filters_layout.addWidget(
            info
        )

        transacoes = (
            self.pix_service
            .listar_transacoes()
        )

        transacoes_saida = [
            item
            for item in transacoes
            if item.get(
                "transaction_type"
            ) == "sent"
        ]

        valor_esperado = int(
            self.subscription.get(
                "amount_cents"
            )
            or 0
        )

        transacoes_saida.sort(
            key=lambda item: abs(
                int(
                    item.get("amount_cents")
                    or 0
                )
                - valor_esperado
            )
        )

        if not transacoes_saida:

            self._mostrar_mensagem(
                "Nenhum PIX de saída encontrado."
            )

            return

        for pix in transacoes_saida:

            nome = (
                pix.get("contact_name")
                or pix.get("description")
                or "PIX"
            )

            conta = (
                pix.get("account_name")
                or "Conta"
            )

            data = self._formatar_data(
                pix["transaction_date"]
            )

            valor = self._formatar_moeda(
                pix["amount_cents"]
            )

            self._adicionar_resultado(
                payment_id=pix["id"],
                titulo=nome,
                detalhe=(
                    f"{data} • {conta}"
                ),
                valor=valor,
            )

    # =========================================================
    # CARTÃO
    # =========================================================

    def _montar_filtros_cartao(
            self,
    ) -> None:

        self.credit_cards = (
            self.credit_card_service
            .listar_cartoes_ativos()
        )

        self.card_combo = QComboBox()

        self.card_combo.addItem(
            "Escolha o cartão",
            None,
        )

        for card in self.credit_cards:

            self.card_combo.addItem(
                card["name"],
                card["id"],
            )

        self.month_combo = QComboBox()

        for month in range(
            1,
            13,
        ):

            self.month_combo.addItem(
                f"{month:02d}",
                month,
            )

        self.year_combo = QComboBox()

        for year in range(
            self.reference_year - 2,
            self.reference_year + 3,
        ):

            self.year_combo.addItem(
                str(year),
                year,
            )

        month_index = (
            self.month_combo
            .findData(
                self.reference_month
            )
        )

        if month_index >= 0:
            self.month_combo.setCurrentIndex(
                month_index
            )

        year_index = (
            self.year_combo
            .findData(
                self.reference_year
            )
        )

        if year_index >= 0:
            self.year_combo.setCurrentIndex(
                year_index
            )

        self.card_combo.currentIndexChanged.connect(
            self._carregar_fatura
        )

        self.month_combo.currentIndexChanged.connect(
            self._carregar_fatura
        )

        self.year_combo.currentIndexChanged.connect(
            self._carregar_fatura
        )

        self.filters_layout.addWidget(
            self.card_combo,
            1,
        )

        self.filters_layout.addWidget(
            self.month_combo
        )

        self.filters_layout.addWidget(
            self.year_combo
        )

        if not self.credit_cards:

            self._mostrar_mensagem(
                "Nenhum cartão cadastrado."
            )

            return

        self._mostrar_mensagem(
            "Escolha um cartão."
        )

    def _carregar_fatura(
            self,
    ) -> None:

        self._limpar_resultados()

        credit_card_id = (
            self.card_combo
            .currentData()
        )

        if credit_card_id is None:

            self._mostrar_mensagem(
                "Escolha um cartão."
            )

            return

        credit_card = None

        for card in self.credit_cards:

            if (
                card["id"]
                == credit_card_id
            ):
                credit_card = card
                break

        if credit_card is None:

            self._mostrar_mensagem(
                "Cartão não encontrado."
            )

            return

        invoice_year = (
            self.year_combo
            .currentData()
        )

        invoice_month = (
            self.month_combo
            .currentData()
        )

        invoice_data = (
            self.credit_card_detail_service
            .carregar_fatura_por_mes(
                credit_card=credit_card,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                sort_mode="data",
            )
        )

        despesas = [
            row
            for row in invoice_data["rows"]
            if row.get("type") == "expense"
        ]

        valor_esperado = int(
            self.subscription.get(
                "amount_cents"
            )
            or 0
        )

        despesas.sort(
            key=lambda row: abs(
                int(
                    row.get("amount_cents")
                    or 0
                )
                - valor_esperado
            )
        )

        if not despesas:

            self._mostrar_mensagem(
                "Nenhum lançamento nesta fatura."
            )

            return

        for row in despesas:

            parcela = row.get(
                "installment"
            )

            detalhe = (
                f"{row['date']} • "
                f"{row['category']}"
            )

            if (
                parcela
                and parcela != "-"
            ):
                detalhe += (
                    f" • {parcela}"
                )

            self._adicionar_resultado(
                payment_id=row["expense_id"],
                titulo=row["description"],
                detalhe=detalhe,
                valor=row["amount"],
            )

    # =========================================================
    # RESULTADOS
    # =========================================================

    def _adicionar_resultado(
            self,
            payment_id: int,
            titulo: str,
            detalhe: str,
            valor: str,
    ) -> None:

        button = QPushButton()

        button.setCheckable(
            True
        )

        button.setObjectName(
            "PaymentItem"
        )

        button.setProperty(
            "payment_id",
            payment_id,
        )

        button.setText(
            (
                f"{titulo}\n"
                f"{detalhe}    •    {valor}"
            )
        )

        button.clicked.connect(
            lambda checked=False,
                   item=button:
            self._selecionar_resultado(
                item
            )
        )

        self.results_layout.insertWidget(
            self.results_layout.count() - 1,
            button,
        )

    def _selecionar_resultado(
            self,
            selected_button: QPushButton,
    ) -> None:

        for index in range(
            self.results_layout.count() - 1
        ):

            item = (
                self.results_layout
                .itemAt(index)
            )

            widget = item.widget()

            if isinstance(
                    widget,
                    QPushButton,
            ):

                widget.setChecked(
                    widget
                    is selected_button
                )

        self.selected_payment_id = (
            selected_button.property(
                "payment_id"
            )
        )

        self.confirm_button.setEnabled(
            True
        )

    # =========================================================
    # CONFIRMAR
    # =========================================================

    def _confirmar(
            self,
    ) -> None:

        if self.selected_payment_id is None:

            QMessageBox.warning(
                self,
                "Selecione um lançamento",
                "Escolha o pagamento correspondente.",
            )

            return

        self.accept()

    def obter_dados(
            self,
    ) -> dict:

        return {
            "payment_source": (
                self.selected_source
            ),

            "payment_id": (
                self.selected_payment_id
            ),
        }

    # =========================================================
    # LIMPEZA
    # =========================================================

    def _limpar_filtros(
            self,
    ) -> None:

        while self.filters_layout.count():

            item = (
                self.filters_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _limpar_resultados(
            self,
    ) -> None:

        while (
            self.results_layout.count()
            > 1
        ):

            item = (
                self.results_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _mostrar_mensagem(
            self,
            texto: str,
    ) -> None:

        label = QLabel(
            texto
        )

        label.setObjectName(
            "EmptyMessage"
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        self.results_layout.insertWidget(
            0,
            label,
        )

    # =========================================================
    # FORMATADORES
    # =========================================================

    def _formatar_moeda(
            self,
            cents: int,
    ) -> str:

        valor = int(
            cents or 0
        ) / 100

        texto = (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {texto}"

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:

        ano, mes, dia = (
            data_iso.split("-")
        )

        return (
            f"{dia}/{mes}/{ano}"
        )

    # =========================================================
    # ESTILO
    # =========================================================

    def _aplicar_estilo(
            self,
    ) -> None:

        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8fafc;
            }

            QLabel#Title {
                color: #0f172a;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#SubscriptionName {
                color: #0f172a;
                font-size: 17px;
                font-weight: 600;
            }

            QLabel#Reference,
            QLabel#Hint {
                color: #64748b;
                font-size: 12px;
            }

            QLabel#EmptyMessage {
                color: #94a3b8;
                padding: 35px;
            }

            QPushButton {
                background-color: white;
                color: #334155;
                border: 1px solid #dbe3ed;
                border-radius: 12px;
                padding: 9px 12px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }

            QPushButton:checked {
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #38bdf8;
                font-weight: 600;
            }

            QPushButton#PaymentItem {
                text-align: left;
                padding: 11px 14px;
            }

            QPushButton#ConfirmButton {
                background-color: #0284c7;
                color: white;
                border: none;
                font-weight: 600;
            }

            QPushButton#ConfirmButton:disabled {
                background-color: #cbd5e1;
            }

            QComboBox {
                background-color: white;
                color: #0f172a;
                border: 1px solid #dbe3ed;
                border-radius: 12px;
                padding: 8px 10px;
            }
            """
        )