from PySide6.QtCore import (
    QDate,
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.date_line_edit import (
    DateLineEdit,
)

from modules.finance.ui.widget.category_combo_box import (
    CategoryComboBox,
)


class CreditCardExpenseDialog(QDialog):
    delete_requested = Signal()

    MODE_SIMPLE = "simple"
    MODE_MONTHLY_BILL = "monthly_bill"
    MODE_SUBSCRIPTION = "subscription"

    def __init__(
            self,
            categories: list[dict],
            subscriptions: list[dict],
            monthly_bills: list[dict],
            invoice_year: int,
            invoice_month: int,
            row_data: dict | None = None,
            recurring_payment: dict | None = None,
            mode: str = "edit",
            parent=None,
    ) -> None:

        super().__init__(parent)

        self.categories = categories or []
        self.subscriptions = subscriptions or []
        self.monthly_bills = monthly_bills or []

        self.invoice_year = invoice_year
        self.invoice_month = invoice_month

        self.row_data = row_data
        self.recurring_payment = recurring_payment

        self.mode = mode

        self.setWindowTitle(
            (
                "Novo lançamento"
                if mode == "create"
                else "Editar lançamento"
            )
        )

        self.setMinimumWidth(
            520
        )

        self._montar_interface()
        self._atualizar_estado_parcelamento()
        self._atualizar_modo_recorrente()
        self._preencher_dados()
        self._aplicar_estilo()

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

        form = QFormLayout()

        form.setSpacing(
            10
        )

        # =====================================================
        # DESCRIÇÃO
        # =====================================================

        self.descricao_input = QLineEdit()

        # =====================================================
        # DATA
        # =====================================================

        self.data_input = DateLineEdit()

        # =====================================================
        # VALOR
        # =====================================================

        self.valor_input = QDoubleSpinBox()

        self.valor_input.setMaximum(
            999999.99
        )

        self.valor_input.setDecimals(
            2
        )

        self.valor_input.setPrefix(
            "R$ "
        )

        # =====================================================
        # CATEGORIA
        # =====================================================

        self.categoria_input = (
            CategoryComboBox(
                categories=self.categories,
                height=38,
                placeholder="Escolha uma categoria",
            )
        )

        # =====================================================
        # SUBCATEGORIA
        # =====================================================

        self.subcategoria_input = QLineEdit()

        self.subcategoria_input.setPlaceholderText(
            "Ex.: Mercado, farmácia, transporte..."
        )

        # =====================================================
        # PARCELAMENTO
        # =====================================================

        self.parcelado_checkbox = QCheckBox(
            "Item parcelado"
        )

        self.parcela_atual_input = QSpinBox()

        self.parcela_atual_input.setRange(
            1,
            999,
        )

        self.parcelas_totais_input = QSpinBox()

        self.parcelas_totais_input.setRange(
            1,
            999,
        )

        self.parcelado_checkbox.stateChanged.connect(
            self._atualizar_estado_parcelamento
        )

        self.parcela_atual_input.valueChanged.connect(
            self._corrigir_limites_parcelas
        )

        self.parcelas_totais_input.valueChanged.connect(
            self._corrigir_limites_parcelas
        )

        # =====================================================
        # OBSERVAÇÕES
        # =====================================================

        self.observacoes_input = QTextEdit()

        self.observacoes_input.setFixedHeight(
            72
        )

        # =====================================================
        # FORM
        # =====================================================

        form.addRow(
            "Descrição:",
            self.descricao_input,
        )

        form.addRow(
            "Data da parcela atual:",
            self.data_input,
        )

        form.addRow(
            "Valor da parcela:",
            self.valor_input,
        )

        form.addRow(
            "Categoria:",
            self.categoria_input,
        )

        form.addRow(
            "Subcategoria:",
            self.subcategoria_input,
        )

        form.addRow(
            "",
            self.parcelado_checkbox,
        )

        form.addRow(
            "Parcela atual:",
            self.parcela_atual_input,
        )

        form.addRow(
            "Parcelas totais:",
            self.parcelas_totais_input,
        )

        layout.addLayout(
            form
        )

        # =====================================================
        # SEPARADOR
        # =====================================================

        separador = QLabel(
            "Vincular este lançamento"
        )

        separador.setObjectName(
            "RecurringTitle"
        )

        layout.addWidget(
            separador
        )

        # =====================================================
        # TIPO
        # =====================================================

        type_row = QHBoxLayout()

        type_row.setSpacing(
            6
        )

        self.recurring_group = (
            QButtonGroup(self)
        )

        self.recurring_group.setExclusive(
            True
        )

        self.recurring_buttons = {}

        opcoes = [
            (
                "Simples",
                self.MODE_SIMPLE,
            ),
            (
                "Conta do Mês",
                self.MODE_MONTHLY_BILL,
            ),
            (
                "Assinatura",
                self.MODE_SUBSCRIPTION,
            ),
        ]

        for texto, value in opcoes:

            button = QPushButton(
                texto
            )

            button.setCheckable(
                True
            )

            button.setProperty(
                "recurringButton",
                True,
            )

            self.recurring_group.addButton(
                button
            )

            self.recurring_buttons[
                value
            ] = button

            button.clicked.connect(
                self._atualizar_modo_recorrente
            )

            type_row.addWidget(
                button,
                1,
            )

        self.recurring_buttons[
            self.MODE_SIMPLE
        ].setChecked(
            True
        )

        layout.addLayout(
            type_row
        )

        # =====================================================
        # ÁREA DINÂMICA
        # =====================================================

        self.recurring_container = QWidget()

        self.recurring_layout = QHBoxLayout(
            self.recurring_container
        )

        self.recurring_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.recurring_layout.setSpacing(
            8
        )

        self.recurring_container.setFixedHeight(
            40
        )

        layout.addWidget(
            self.recurring_container
        )

        # =====================================================
        # OBSERVAÇÕES
        # =====================================================

        observacoes_form = QFormLayout()

        observacoes_form.addRow(
            "Observações:",
            self.observacoes_input,
        )

        layout.addLayout(
            observacoes_form
        )

        # =====================================================
        # AJUDA
        # =====================================================

        ajuda = QLabel(
            "Vincular uma assinatura ou conta do mês não altera "
            "descrição, valor, categoria, data ou qualquer outro "
            "dado deste lançamento."
        )

        ajuda.setWordWrap(
            True
        )

        ajuda.setStyleSheet(
            """
            color: #64748b;
            font-size: 11px;
            """
        )

        layout.addWidget(
            ajuda
        )

        # =====================================================
        # BOTÕES
        # =====================================================

        botoes = QHBoxLayout()

        if self.mode == "edit":

            excluir = QPushButton(
                "Excluir"
            )

            excluir.setObjectName(
                "DangerButton"
            )

            excluir.clicked.connect(
                self._solicitar_exclusao
            )

            botoes.addWidget(
                excluir
            )

        botoes.addStretch()

        cancelar = QPushButton(
            "Cancelar"
        )

        salvar = QPushButton(
            (
                "Adicionar"
                if self.mode == "create"
                else "Salvar"
            )
        )

        salvar.setDefault(
            True
        )

        cancelar.clicked.connect(
            self.reject
        )

        salvar.clicked.connect(
            self._salvar
        )

        botoes.addWidget(
            cancelar
        )

        botoes.addWidget(
            salvar
        )

        layout.addLayout(
            botoes
        )

    # =========================================================
    # RECORRÊNCIA
    # =========================================================

    def _modo_recorrente(
            self,
    ) -> str:

        for value, button in (
            self.recurring_buttons.items()
        ):

            if button.isChecked():
                return value

        return self.MODE_SIMPLE

    def _atualizar_modo_recorrente(
            self,
    ) -> None:

        self._limpar_recurring_layout()

        mode = self._modo_recorrente()

        if mode == self.MODE_SIMPLE:
            return

        self.reference_combo = QComboBox()

        if mode == self.MODE_SUBSCRIPTION:

            self.reference_combo.addItem(
                "Escolha uma assinatura",
                None,
            )

            for item in self.subscriptions:

                self.reference_combo.addItem(
                    item["name"],
                    item["id"],
                )

        else:

            self.reference_combo.addItem(
                "Escolha uma conta do mês",
                None,
            )

            for item in self.monthly_bills:

                self.reference_combo.addItem(
                    item["name"],
                    item["id"],
                )

        # =====================================================
        # MÊS
        # =====================================================

        self.reference_month_combo = (
            QComboBox()
        )

        for month in range(
            1,
            13,
        ):

            self.reference_month_combo.addItem(
                f"{month:02d}",
                month,
            )

        self.reference_month_combo.setFixedWidth(
            65
        )

        # =====================================================
        # ANO
        # =====================================================

        self.reference_year_combo = (
            QComboBox()
        )

        for year in range(
            self.invoice_year - 2,
            self.invoice_year + 4,
        ):

            self.reference_year_combo.addItem(
                f"{year % 100:02d}",
                year,
            )

        self.reference_year_combo.setFixedWidth(
            65
        )

        # =====================================================
        # PADRÃO = FATURA SELECIONADA
        # =====================================================

        month_index = (
            self.reference_month_combo
            .findData(
                self.invoice_month
            )
        )

        if month_index >= 0:

            self.reference_month_combo.setCurrentIndex(
                month_index
            )

        year_index = (
            self.reference_year_combo
            .findData(
                self.invoice_year
            )
        )

        if year_index >= 0:

            self.reference_year_combo.setCurrentIndex(
                year_index
            )

        self.recurring_layout.addWidget(
            self.reference_combo,
            1,
        )

        self.recurring_layout.addWidget(
            self.reference_month_combo
        )

        self.recurring_layout.addWidget(
            self.reference_year_combo
        )

    # =========================================================
    # PREENCHE DADOS
    # =========================================================

    def _preencher_dados(
            self,
    ) -> None:

        # =====================================================
        # NOVO LANÇAMENTO
        # =====================================================

        if (
            self.mode == "create"
            or self.row_data is None
        ):

            self.data_input.set_date(
                QDate.currentDate()
            )

            return

        # =====================================================
        # DADOS NORMAIS
        # =====================================================

        self.descricao_input.setText(
            self.row_data[
                "description"
            ]
        )

        dia, mes = (
            self.row_data[
                "date"
            ].split("/")
        )

        self.data_input.set_date(
            QDate(
                int(
                    self.invoice_year
                ),
                int(mes),
                int(dia),
            )
        )

        valor_texto = (
            self.row_data[
                "amount"
            ]
            .replace("R$ ", "")
            .replace(".", "")
            .replace(",", ".")
        )

        self.valor_input.setValue(
            float(valor_texto)
        )

        self.categoria_input.select_category(
            self.row_data.get(
                "category_id"
            )
        )

        self.subcategoria_input.setText(
            self.row_data.get(
                "subcategory"
            )
            or ""
        )

        installment_number = int(
            self.row_data.get(
                "installment_number",
                1,
            )
            or 1
        )

        installment_total = int(
            self.row_data.get(
                "installment_total",
                1,
            )
            or 1
        )

        if installment_total > 1:

            self.parcelado_checkbox.setChecked(
                True
            )

            self.parcela_atual_input.setValue(
                installment_number
            )

            self.parcelas_totais_input.setValue(
                installment_total
            )

        else:

            self.parcelado_checkbox.setChecked(
                False
            )

        self.observacoes_input.setPlainText(
            self.row_data.get(
                "notes"
            )
            or ""
        )

        # =====================================================
        # VÍNCULO EXISTENTE
        # =====================================================

        if not self.recurring_payment:
            return

        if (
            self.recurring_payment.get(
                "subscription_id"
            )
            is not None
        ):

            mode = self.MODE_SUBSCRIPTION

            reference_id = (
                self.recurring_payment[
                    "subscription_id"
                ]
            )

        elif (
            self.recurring_payment.get(
                "monthly_bill_id"
            )
            is not None
        ):

            mode = self.MODE_MONTHLY_BILL

            reference_id = (
                self.recurring_payment[
                    "monthly_bill_id"
                ]
            )

        else:

            return

        self.recurring_buttons[
            mode
        ].setChecked(
            True
        )

        self._atualizar_modo_recorrente()

        index = (
            self.reference_combo
            .findData(
                reference_id
            )
        )

        if index >= 0:

            self.reference_combo.setCurrentIndex(
                index
            )

        month_index = (
            self.reference_month_combo
            .findData(
                self.recurring_payment[
                    "reference_month"
                ]
            )
        )

        if month_index >= 0:

            self.reference_month_combo.setCurrentIndex(
                month_index
            )

        year_index = (
            self.reference_year_combo
            .findData(
                self.recurring_payment[
                    "reference_year"
                ]
            )
        )

        if year_index >= 0:

            self.reference_year_combo.setCurrentIndex(
                year_index
            )

    # =========================================================
    # PARCELAMENTO
    # =========================================================

    def _atualizar_estado_parcelamento(
            self,
    ) -> None:

        parcelado = (
            self.parcelado_checkbox
            .isChecked()
        )

        self.parcela_atual_input.setEnabled(
            parcelado
        )

        self.parcelas_totais_input.setEnabled(
            parcelado
        )

        if not parcelado:

            self.parcela_atual_input.setValue(
                1
            )

            self.parcelas_totais_input.setValue(
                1
            )

    def _corrigir_limites_parcelas(
            self,
    ) -> None:

        parcela_atual = (
            self.parcela_atual_input
            .value()
        )

        parcelas_totais = (
            self.parcelas_totais_input
            .value()
        )

        if (
            parcela_atual
            > parcelas_totais
        ):

            self.parcelas_totais_input.setValue(
                parcela_atual
            )

    # =========================================================
    # SALVAR
    # =========================================================

    def _salvar(
            self,
    ) -> None:

        if not (
            self.descricao_input
            .text()
            .strip()
        ):

            QMessageBox.warning(
                self,
                "Descrição obrigatória",
                "Informe a descrição do lançamento.",
            )

            return

        if (
            self.valor_input.value()
            <= 0
        ):

            QMessageBox.warning(
                self,
                "Valor obrigatório",
                "Informe um valor maior que zero.",
            )

            return

        if (
            self.categoria_input
            .category_id()
            is None
        ):

            QMessageBox.warning(
                self,
                "Categoria obrigatória",
                "Escolha uma categoria.",
            )

            return

        mode = self._modo_recorrente()

        if (
            mode != self.MODE_SIMPLE
        ):

            if (
                not hasattr(
                    self,
                    "reference_combo",
                )
                or
                self.reference_combo.currentData()
                is None
            ):

                QMessageBox.warning(
                    self,
                    "Vínculo obrigatório",
                    (
                        "Escolha a assinatura "
                        "ou conta do mês."
                    ),
                )

                return

        self.accept()

    # =========================================================
    # RETORNO
    # =========================================================

    def obter_dados(
            self,
    ) -> dict:

        parcelado = (
            self.parcelado_checkbox
            .isChecked()
        )

        expense = {
            "category_id": (
                self.categoria_input
                .category_id()
            ),

            "subcategory": (
                self.subcategoria_input
                .text()
                .strip()
                or None
            ),

            "effective_description": (
                self.descricao_input
                .text()
                .strip()
            ),

            "effective_purchase_date": (
                self.data_input
                .to_iso_date(
                    self.invoice_year
                )
            ),

            "effective_amount_cents": int(
                round(
                    self.valor_input
                    .value()
                    * 100
                )
            ),

            "notes": (
                self.observacoes_input
                .toPlainText()
                .strip()
                or None
            ),

            "installment_number": (
                self.parcela_atual_input
                .value()
                if parcelado
                else 1
            ),

            "installment_total": (
                self.parcelas_totais_input
                .value()
                if parcelado
                else 1
            ),
        }

        mode = self._modo_recorrente()

        recurring = {
            "mode": mode,
            "reference_id": None,
            "reference_month": None,
            "reference_year": None,
        }

        if (
            mode != self.MODE_SIMPLE
        ):

            recurring[
                "reference_id"
            ] = (
                self.reference_combo
                .currentData()
            )

            recurring[
                "reference_month"
            ] = (
                self.reference_month_combo
                .currentData()
            )

            recurring[
                "reference_year"
            ] = (
                self.reference_year_combo
                .currentData()
            )

        return {
            "expense": expense,
            "recurring": recurring,
        }

    # =========================================================
    # HELPERS
    # =========================================================

    def _limpar_recurring_layout(
            self,
    ) -> None:

        for attribute in (
            "reference_combo",
            "reference_month_combo",
            "reference_year_combo",
        ):

            if hasattr(
                    self,
                    attribute,
            ):

                delattr(
                    self,
                    attribute,
                )

        while (
            self.recurring_layout.count()
        ):

            item = (
                self.recurring_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

    # =========================================================
    # TECLADO / EXCLUSÃO
    # =========================================================

    def keyPressEvent(
            self,
            event,
    ) -> None:

        if event.key() in (
            Qt.Key_Return,
            Qt.Key_Enter,
        ):

            self._salvar()
            return

        super().keyPressEvent(
            event
        )

    def _solicitar_exclusao(
            self,
    ) -> None:

        self.delete_requested.emit()
        self.reject()

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

            QLabel {
                color: #334155;
                font-size: 13px;
            }

            QLabel#RecurringTitle {
                color: #0f172a;
                font-size: 13px;
                font-weight: 700;
                margin-top: 4px;
            }

            QLineEdit,
            QComboBox,
            QDoubleSpinBox,
            QSpinBox,
            QTextEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 11px;
                padding: 7px 10px;
                font-size: 13px;
                color: #0f172a;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDoubleSpinBox:focus,
            QSpinBox:focus,
            QTextEdit:focus {
                border: 1px solid #2563eb;
            }

            QCheckBox {
                color: #0f172a;
                font-size: 13px;
                spacing: 8px;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 9px 18px;
                font-size: 13px;
                font-weight: 600;
                background-color: #e2e8f0;
                color: #0f172a;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }

            QPushButton:default {
                background-color: #2563eb;
                color: white;
            }

            QPushButton:default:hover {
                background-color: #1d4ed8;
            }

            QPushButton[recurringButton="true"] {
                background-color: white;
                color: #64748b;
                border: 1px solid #e2e8f0;
            }

            QPushButton[recurringButton="true"]:checked {
                background-color: #eff6ff;
                color: #1d4ed8;
                border: 1px solid #60a5fa;
            }

            QPushButton#DangerButton {
                background-color: #fee2e2;
                color: #b91c1c;
            }

            QPushButton#DangerButton:hover {
                background-color: #fecaca;
            }
            """
        )