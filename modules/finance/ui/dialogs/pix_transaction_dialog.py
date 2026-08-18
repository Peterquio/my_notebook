from datetime import date
from PySide6.QtCore import (QEasingCurve, Property, QDate, QRectF,
                            Qt, QVariantAnimation, Signal)
from PySide6.QtGui import (QColor, QPainter, QPen)
from PySide6.QtWidgets import (QButtonGroup,
    QComboBox, QDateEdit, QDialog, QFrame,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout, QWidget)

from modules.finance.ui.widget.category_combo_box import CategoryComboBox


# =============================================================
# SWITCH ENTRADA / SAÍDA
# =============================================================


class PixTypeSwitch(QWidget):
    type_changed = Signal(str)

    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self._progress = 0.0
        self._transaction_type = "received"

        self.setCursor(
            Qt.PointingHandCursor
        )

        self.animation = QVariantAnimation(
            self
        )

        self.animation.setDuration(
            240
        )

        self.animation.setEasingCurve(
            QEasingCurve.InOutCubic
        )

        self.animation.valueChanged.connect(
            self._on_animation_value
        )

    # =========================================================
    # ANIMAÇÃO
    # =========================================================

    def _get_progress(
            self,
    ) -> float:
        return self._progress

    def _set_progress(
            self,
            value: float,
    ) -> None:
        self._progress = value
        self.update()

    progress = Property(
        float,
        _get_progress,
        _set_progress,
    )

    def _on_animation_value(
            self,
            value,
    ) -> None:
        self.progress = float(
            value
        )

    # =========================================================
    # VALOR
    # =========================================================

    def transaction_type(
            self,
    ) -> str:
        return self._transaction_type

    def set_transaction_type(
            self,
            transaction_type: str,
            animate: bool = False,
    ) -> None:

        if transaction_type not in {
            "received",
            "sent",
        }:
            transaction_type = "received"

        destino = (
            0.0
            if transaction_type == "received"
            else 1.0
        )

        mudou = (
            transaction_type
            != self._transaction_type
        )

        self._transaction_type = (
            transaction_type
        )

        if animate:

            self.animation.stop()

            self.animation.setStartValue(
                self._progress
            )

            self.animation.setEndValue(
                destino
            )

            self.animation.start()

        else:

            self.animation.stop()
            self.progress = destino

        if mudou:
            self.type_changed.emit(
                transaction_type
            )

    # =========================================================
    # CLIQUE
    # =========================================================

    def mousePressEvent(
            self,
            event,
    ) -> None:

        if event.button() != Qt.LeftButton:
            return

        novo_tipo = (
            "sent"
            if self._transaction_type == "received"
            else "received"
        )

        self.set_transaction_type(
            novo_tipo,
            animate=True,
        )

        event.accept()

    # =========================================================
    # DESENHO
    # =========================================================

    def paintEvent(
            self,
            event,
    ) -> None:

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        largura = self.width()
        altura = self.height()

        rect = QRectF(
            1,
            1,
            largura - 2,
            altura - 2,
        )

        # -----------------------------------------------------
        # COR: VERDE -> VERMELHO
        # -----------------------------------------------------

        verde = QColor(
            "#22c55e"
        )

        vermelho = QColor(
            "#ef4444"
        )

        r = int(
            verde.red()
            + (
                vermelho.red()
                - verde.red()
            )
            * self._progress
        )

        g = int(
            verde.green()
            + (
                vermelho.green()
                - verde.green()
            )
            * self._progress
        )

        b = int(
            verde.blue()
            + (
                vermelho.blue()
                - verde.blue()
            )
            * self._progress
        )

        cor_fundo = QColor(
            r,
            g,
            b,
        )

        # -----------------------------------------------------
        # TRILHO
        # -----------------------------------------------------

        painter.setPen(
            QPen(
                QColor("#94a3b8"),
                1,
            )
        )

        painter.setBrush(
            cor_fundo
        )

        painter.drawRoundedRect(
            rect,
            altura / 2,
            altura / 2,
        )

        # -----------------------------------------------------
        # BOLINHA
        # -----------------------------------------------------

        margem = 4
        diametro = altura - margem * 2

        inicio_x = margem
        fim_x = largura - margem - diametro

        x = (
            inicio_x
            + (
                fim_x
                - inicio_x
            )
            * self._progress
        )

        knob_rect = QRectF(
            x,
            margem,
            diametro,
            diametro,
        )

        painter.setPen(
            QPen(
                QColor("#cbd5e1"),
                1,
            )
        )

        painter.setBrush(
            QColor("#ffffff")
        )

        painter.drawEllipse(
            knob_rect
        )

        # -----------------------------------------------------
        # TEXTO
        # -----------------------------------------------------

        fonte = painter.font()
        fonte.setBold(True)
        fonte.setPointSize(10)

        painter.setFont(
            fonte
        )

        painter.setPen(
            QColor("#ffffff")
        )

        if self._transaction_type == "received":

            texto_rect = QRectF(
                diametro + 10,
                0,
                largura - diametro - 18,
                altura,
            )

            painter.drawText(
                texto_rect,
                Qt.AlignCenter,
                "ENTRADA",
            )

        else:

            texto_rect = QRectF(
                8,
                0,
                largura - diametro - 18,
                altura,
            )

            painter.drawText(
                texto_rect,
                Qt.AlignCenter,
                "SAÍDA",
            )


# =============================================================
# DIALOG PIX
# =============================================================


class PixTransactionDialog(QDialog):
    MODE_SIMPLE = "simple"
    MODE_CONTACT = "contact"
    MODE_MONTHLY_BILL = "monthly_bill"
    MODE_SUBSCRIPTION = "subscription"

    LABEL_WIDTH = 105

    def __init__(
            self,
            accounts: list[dict],
            categories: list[dict],
            subscriptions: list[dict] | None = None,
            monthly_bills: list[dict] | None = None,
            contacts: list[dict] | None = None,
            transaction_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = accounts or []
        self.categories = categories or []
        self.subscriptions = subscriptions or []
        self.monthly_bills = monthly_bills or []
        self.contacts = contacts or []

        self.transaction_data = (
            transaction_data
        )

        self.setWindowTitle(
            "Editar PIX"
            if transaction_data
            else "Novo PIX"
        )

        self.setObjectName(
            "PixTransactionDialog"
        )

        self.setFixedSize(
            500,
            590,
        )

        self.setWindowFlag(
            Qt.WindowContextHelpButtonHint,
            False,
        )

        self._montar_interface()
        self._aplicar_estilo()

        if self.transaction_data:
            self._carregar_dados()

        self._atualizar_modo()

    def _criar_seletores_referencia(
            self,
            placeholder: str,
            items: list[dict],
            amount_key: str,
    ) -> None:

        # =========================================================
        # REFERÊNCIA
        # =========================================================

        self.reference_combo = QComboBox()

        self.reference_combo.addItem(
            placeholder,
            None,
        )

        for item in items:
            self.reference_combo.addItem(
                item["name"],
                item["id"],
            )

        self.reference_combo.currentIndexChanged.connect(
            self._referencia_alterada
        )

        # =========================================================
        # MÊS
        # =========================================================

        self.reference_month_combo = QComboBox()

        self.reference_month_combo.setObjectName(
            "ReferencePeriodCombo"
        )

        for month in range(1, 13):
            self.reference_month_combo.addItem(
                f"{month:02d}",
                month,
            )

        # =========================================================
        # ANO
        # =========================================================

        self.reference_year_combo = QComboBox()

        self.reference_year_combo.setObjectName(
            "ReferencePeriodCombo"
        )

        ano_atual = date.today().year

        for year in range(
                ano_atual - 2,
                ano_atual + 6,
        ):
            self.reference_year_combo.addItem(
                f"{year % 100:02d}",
                year,
            )

        # =========================================================
        # SELEÇÃO PADRÃO = MÊS / ANO ATUAL
        # =========================================================

        mes_atual = date.today().month

        month_index = (
            self.reference_month_combo
            .findData(
                mes_atual
            )
        )

        if month_index >= 0:
            self.reference_month_combo.setCurrentIndex(
                month_index
            )

        year_index = (
            self.reference_year_combo
            .findData(
                ano_atual
            )
        )

        if year_index >= 0:
            self.reference_year_combo.setCurrentIndex(
                year_index
            )

        # =========================================================
        # TAMANHOS
        # =========================================================

        self.reference_month_combo.setFixedWidth(
            68
        )

        self.reference_year_combo.setFixedWidth(
            68
        )

        # =========================================================
        # LINHA
        # =========================================================

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row.setSpacing(
            8
        )

        row.addWidget(
            self.reference_combo,
            1,
        )

        row.addWidget(
            self.reference_month_combo,
        )

        row.addWidget(
            self.reference_year_combo,
        )

        self.dynamic_layout.addLayout(
            row
        )

        # Guardamos para usar na sugestão de valor.

        self.reference_amount_key = (
            amount_key
        )

        self.reference_items = (
            items
        )

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
            24,
            18,
            24,
            20,
        )

        main_layout.setSpacing(
            12
        )

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = QHBoxLayout()

        titulo = QLabel(
            "Editar PIX"
            if self.transaction_data
            else "Novo PIX"
        )

        titulo.setObjectName(
            "PixDialogTitle"
        )

        fechar = QPushButton(
            "×"
        )

        fechar.setObjectName(
            "PixDialogClose"
        )

        fechar.setFixedSize(
            32,
            32,
        )

        fechar.clicked.connect(
            self.reject
        )

        header.addWidget(
            titulo
        )

        header.addStretch()

        header.addWidget(
            fechar
        )

        main_layout.addLayout(
            header
        )

        linha = QFrame()
        linha.setFrameShape(
            QFrame.HLine
        )

        linha.setObjectName(
            "PixSeparator"
        )

        main_layout.addWidget(
            linha
        )

        # -----------------------------------------------------
        # TIPO
        # -----------------------------------------------------

        self.type_switch = (
            PixTypeSwitch()
        )

        self.type_switch.type_changed.connect(
            self._tipo_alterado
        )

        # -----------------------------------------------------
        # CONTA
        # -----------------------------------------------------

        self.account_combo = (
            QComboBox()
        )

        self.account_combo.addItem(
            "Selecione uma conta",
            None,
        )

        for account in self.accounts:

            nome = (
                account.get("name")
                or "Conta"
            )

            institution = (
                account.get(
                    "institution_name"
                )
                or ""
            )

            if institution:
                texto = (
                    f"{nome} - {institution}"
                )
            else:
                texto = nome

            self.account_combo.addItem(
                texto,
                account["id"],
            )

        # -----------------------------------------------------
        # CONTA + ENTRADA / SAÍDA
        # -----------------------------------------------------

        first_row = QHBoxLayout()

        first_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        first_row.setSpacing(
            10
        )

        self.account_combo.setMinimumHeight(
            38
        )

        self.type_switch.setFixedSize(
            110,
            38,
        )

        first_row.addWidget(
            self.account_combo,
            1,
        )

        first_row.addWidget(
            self.type_switch,
            0,
        )

        main_layout.addLayout(
            first_row
        )

        # -----------------------------------------------------
        # VALOR
        # -----------------------------------------------------

        self.amount_input = (
            QLineEdit()
        )

        self.amount_input.setText(
            "R$ 0,00"
        )

        self.amount_input.setAlignment(
            Qt.AlignRight
        )

        self.amount_input.textEdited.connect(
            self._formatar_valor_digitado
        )

        main_layout.addLayout(
            self._linha_campo(
                "Valor:",
                self.amount_input,
            )
        )

        # -----------------------------------------------------
        # DATA
        # -----------------------------------------------------

        self.date_input = (
            QDateEdit()
        )

        self.date_input.setCalendarPopup(
            True
        )

        self.date_input.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.date_input.setDate(
            QDate.currentDate()
        )

        main_layout.addLayout(
            self._linha_campo(
                "Data:",
                self.date_input,
            )
        )

        # -----------------------------------------------------
        # CATEGORIA
        # -----------------------------------------------------

        self.category_combo = (
            CategoryComboBox(
                categories=self.categories,
                height=38,
                placeholder="Escolha uma categoria",
            )
        )

        main_layout.addLayout(
            self._linha_campo(
                "Categoria:",
                self.category_combo,
            )
        )

        # -----------------------------------------------------
        # CLASSIFICAÇÃO
        # -----------------------------------------------------

        classification_row = (
            QHBoxLayout()
        )

        classification_row.setSpacing(
            6
        )

        label = QLabel(
            "Classificação:"
        )

        label.setObjectName(
            "PixFieldLabel"
        )

        label.setFixedWidth(
            self.LABEL_WIDTH
        )

        classification_row.addWidget(
            label
        )

        self.mode_group = (
            QButtonGroup(self)
        )

        self.mode_group.setExclusive(
            True
        )

        self.mode_buttons = {}

        modos = [
            (
                "PIX Simples",
                self.MODE_SIMPLE,
            ),
            (
                "Contato",
                self.MODE_CONTACT,
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

        for texto, mode in modos:

            button = QPushButton(
                texto
            )

            button.setCheckable(
                True
            )

            button.setProperty(
                "classificationButton",
                True,
            )

            self.mode_group.addButton(
                button
            )

            self.mode_buttons[
                mode
            ] = button

            button.clicked.connect(
                self._atualizar_modo
            )

            classification_row.addWidget(
                button,
                1,
            )

        self.mode_buttons[
            self.MODE_SIMPLE
        ].setChecked(
            True
        )

        main_layout.addLayout(
            classification_row
        )

        # -----------------------------------------------------
        # ÁREA DINÂMICA
        # -----------------------------------------------------

        self.dynamic_frame = (
            QFrame()
        )

        self.dynamic_frame.setObjectName(
            "PixDynamicFrame"
        )

        self.dynamic_layout = (
            QVBoxLayout(
                self.dynamic_frame
            )
        )

        self.dynamic_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.dynamic_layout.setSpacing(
            8
        )

        self.dynamic_frame.setFixedHeight(
            46
        )

        main_layout.addWidget(
            self.dynamic_frame
        )

        # -----------------------------------------------------
        # DESCRIÇÃO
        # -----------------------------------------------------

        self.description_input = (
            QLineEdit()
        )

        self.description_input.setPlaceholderText(
            "Descrição do PIX"
        )

        main_layout.addLayout(
            self._linha_campo(
                "Descrição:",
                self.description_input,
            )
        )

        # -----------------------------------------------------
        # OBSERVAÇÕES
        # -----------------------------------------------------

        self.notes_input = (
            QTextEdit()
        )

        self.notes_input.setPlaceholderText(
            "Observações"
        )

        self.notes_input.setFixedHeight(
            68
        )

        main_layout.addLayout(
            self._linha_campo(
                "Observações:",
                self.notes_input,
                align_top=True,
            )
        )

        main_layout.addStretch()

        # -----------------------------------------------------
        # FOOTER
        # -----------------------------------------------------

        footer = QHBoxLayout()

        footer.addStretch()

        cancelar = QPushButton(
            "Cancelar"
        )

        cancelar.setObjectName(
            "PixCancelButton"
        )

        cancelar.clicked.connect(
            self.reject
        )

        salvar = QPushButton(
            "Salvar PIX"
        )

        salvar.setObjectName(
            "PixSaveButton"
        )

        salvar.clicked.connect(
            self._salvar
        )

        footer.addWidget(
            cancelar
        )

        footer.addWidget(
            salvar
        )

        main_layout.addLayout(
            footer
        )

    # =========================================================
    # LINHA LABEL + CAMPO
    # =========================================================

    def _linha_campo(
            self,
            texto: str,
            widget: QWidget,
            align_top: bool = False,
    ) -> QHBoxLayout:

        layout = QHBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            10
        )

        label = QLabel(
            texto
        )

        label.setObjectName(
            "PixFieldLabel"
        )

        label.setFixedWidth(
            self.LABEL_WIDTH
        )

        if align_top:

            layout.addWidget(
                label,
                alignment=Qt.AlignTop,
            )

        else:

            layout.addWidget(
                label,
                alignment=Qt.AlignVCenter,
            )

        layout.addWidget(
            widget,
            1,
        )

        return layout

    # =========================================================
    # TIPO
    # =========================================================

    def _tipo_alterado(
            self,
            transaction_type: str,
    ) -> None:

        mode = self._modo_atual()

        if (
            transaction_type == "received"
            and mode in {
                self.MODE_MONTHLY_BILL,
                self.MODE_SUBSCRIPTION,
            }
        ):
            self.mode_buttons[
                self.MODE_SIMPLE
            ].setChecked(
                True
            )

            self._atualizar_modo()

    # =========================================================
    # CLASSIFICAÇÃO
    # =========================================================

    def _modo_atual(
            self,
    ) -> str:

        for mode, button in (
            self.mode_buttons.items()
        ):

            if button.isChecked():
                return mode

        return self.MODE_SIMPLE

    def _atualizar_modo(
            self,
    ) -> None:

        self._limpar_dynamic()

        mode = self._modo_atual()

        if mode == self.MODE_SIMPLE:
            return

        if mode == self.MODE_CONTACT:
            self._montar_contato()
            return

        if mode == self.MODE_MONTHLY_BILL:

            if (
                self.type_switch
                .transaction_type()
                != "sent"
            ):
                self.type_switch \
                    .set_transaction_type(
                        "sent",
                        animate=True,
                    )

            self._montar_conta_mes()
            return

        if mode == self.MODE_SUBSCRIPTION:

            if (
                self.type_switch
                .transaction_type()
                != "sent"
            ):
                self.type_switch \
                    .set_transaction_type(
                        "sent",
                        animate=True,
                    )

            self._montar_assinatura()

    # =========================================================
    # CONTATO
    # =========================================================

    def _montar_contato(
            self,
    ) -> None:

        self.contact_combo = (
            QComboBox()
        )

        self.contact_combo.addItem(
            "Novo contato",
            None,
        )

        for contact in self.contacts:

            nome = (
                contact.get("name")
                or contact.get(
                    "contact_name"
                )
                or "Contato"
            )

            self.contact_combo.addItem(
                nome,
                contact.get("id"),
            )

        self.dynamic_layout.addLayout(
            self._linha_campo(
                "Contato:",
                self.contact_combo,
            )
        )

    # =========================================================
    # CONTA DO MÊS
    # =========================================================

    def _montar_conta_mes(
            self,
    ) -> None:

        self._criar_seletores_referencia(
            placeholder="Conta do Mês",
            items=self.monthly_bills,
            amount_key="estimated_amount_cents",
        )

    # =========================================================
    # ASSINATURA
    # =========================================================

    def _montar_assinatura(
            self,
    ) -> None:

        self._criar_seletores_referencia(
            placeholder="Assinatura",
            items=self.subscriptions,
            amount_key="amount_cents",
        )

    # =========================================================
    # REFERÊNCIA SELECIONADA
    # =========================================================

    def _referencia_alterada(
            self,
    ) -> None:

        if not hasattr(
                self,
                "reference_combo",
        ):
            return

        reference_id = (
            self.reference_combo
            .currentData()
        )

        if reference_id is None:
            return

        # Valor digitado manualmente ganha.
        if self._obter_amount_cents() != 0:
            return

        for item in self.reference_items:

            if (
                    item["id"]
                    == reference_id
            ):
                self._set_amount_cents(
                    item.get(
                        self.reference_amount_key,
                        0,
                    )
                )

                return

    # =========================================================
    # LIMPEZA DINÂMICA
    # =========================================================

    def _limpar_dynamic(
            self,
    ) -> None:

        for attribute in (
                "reference_combo",
                "reference_month_combo",
                "reference_year_combo",
                "reference_items",
                "reference_amount_key",
                "contact_combo",
        ):

            if hasattr(
                    self,
                    attribute,
            ):
                delattr(
                    self,
                    attribute,
                )

        while self.dynamic_layout.count():

            item = (
                self.dynamic_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout:
                self._limpar_layout(
                    child_layout
                )

    def _limpar_layout(
            self,
            layout,
    ) -> None:

        while layout.count():

            item = layout.takeAt(
                0
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

            child_layout = item.layout()

            if child_layout:
                self._limpar_layout(
                    child_layout
                )

    # =========================================================
    # VALOR
    # =========================================================

    def _formatar_valor_digitado(
            self,
            texto: str,
    ) -> None:

        numeros = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        cents = int(
            numeros or 0
        )

        self._set_amount_cents(
            cents
        )

    def _set_amount_cents(
            self,
            cents: int,
    ) -> None:

        cents = int(
            cents or 0
        )

        reais = cents / 100

        texto = (
            f"{reais:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        self.amount_input.blockSignals(
            True
        )

        self.amount_input.setText(
            f"R$ {texto}"
        )

        self.amount_input.blockSignals(
            False
        )

        self.amount_input.setCursorPosition(
            len(
                self.amount_input.text()
            )
        )

    def _obter_amount_cents(
            self,
    ) -> int:

        numeros = "".join(
            caractere
            for caractere
            in self.amount_input.text()
            if caractere.isdigit()
        )

        return int(
            numeros or 0
        )

    # =========================================================
    # EDIÇÃO
    # =========================================================

    def _carregar_dados(
            self,
    ) -> None:

        self.type_switch.set_transaction_type(
            self.transaction_data.get(
                "transaction_type",
                "received",
            ),
            animate=False,
        )

        self._selecionar_combo(
            self.account_combo,
            self.transaction_data.get(
                "account_id"
            ),
        )

        self._selecionar_combo(
            self.category_combo,
            self.transaction_data.get(
                "category_id"
            ),
        )

        self._set_amount_cents(
            self.transaction_data.get(
                "amount_cents",
                0,
            )
        )

        transaction_date = (
            self.transaction_data.get(
                "transaction_date"
            )
        )

        if transaction_date:

            data = QDate.fromString(
                transaction_date,
                "yyyy-MM-dd",
            )

            if data.isValid():

                self.date_input.setDate(
                    data
                )

        self.description_input.setText(
            self.transaction_data.get(
                "description"
            )
            or ""
        )

        self.notes_input.setPlainText(
            self.transaction_data.get(
                "notes"
            )
            or ""
        )

        if (
            self.transaction_data.get(
                "contact_name"
            )
        ):

            self.mode_buttons[
                self.MODE_CONTACT
            ].setChecked(
                True
            )

    # =========================================================
    # SALVAR
    # =========================================================

    def _salvar(
            self,
    ) -> None:

        if (
            self.account_combo
            .currentData()
            is None
        ):

            QMessageBox.warning(
                self,
                "Conta obrigatória",
                "Selecione a conta do PIX.",
            )

            return

        if (
            self._obter_amount_cents()
            <= 0
        ):

            QMessageBox.warning(
                self,
                "Valor obrigatório",
                "Informe um valor maior que zero.",
            )

            return

        if (
            self.category_combo
            .currentData()
            is None
        ):

            QMessageBox.warning(
                self,
                "Categoria obrigatória",
                "Selecione uma categoria.",
            )

            return

        mode = self._modo_atual()

        if mode in {
            self.MODE_MONTHLY_BILL,
            self.MODE_SUBSCRIPTION,
        }:

            if (
                not hasattr(
                    self,
                    "reference_combo",
                )
                or
                self.reference_combo
                .currentData()
                is None
            ):

                QMessageBox.warning(
                    self,
                    "Seleção obrigatória",
                    (
                        "Selecione a conta do mês "
                        "ou assinatura."
                    ),
                )

                return

        self.accept()

    # =========================================================
    # RESULTADO
    # =========================================================

    def obter_dados(
            self,
    ) -> dict:

        mode = self._modo_atual()

        contact_id = None
        contact_name = None

        reference_id = None
        reference_month = None
        reference_year = None

        # =========================================================
        # CONTATO
        # =========================================================

        if (
                mode == self.MODE_CONTACT
                and hasattr(
            self,
            "contact_combo",
        )
        ):

            contact_id = (
                self.contact_combo
                .currentData()
            )

            contact_name = (
                self.contact_combo
                .currentText()
                .strip()
            )

            if contact_id is None:
                contact_name = None

        # =========================================================
        # ASSINATURA / CONTA DO MÊS
        # =========================================================

        if (
                mode in {
            self.MODE_MONTHLY_BILL,
            self.MODE_SUBSCRIPTION,
        }
                and hasattr(
            self,
            "reference_combo",
        )
        ):
            reference_id = (
                self.reference_combo
                .currentData()
            )

            reference_month = (
                self.reference_month_combo
                .currentData()
            )

            reference_year = (
                self.reference_year_combo
                .currentData()
            )

        # =========================================================
        # RESULTADO
        # =========================================================

        return {
            "pix": {
                "account_id": (
                    self.account_combo
                    .currentData()
                ),

                "transaction_type": (
                    self.type_switch
                    .transaction_type()
                ),

                "amount_cents": (
                    self._obter_amount_cents()
                ),

                "transaction_date": (
                    self.date_input
                    .date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                ),

                "contact_id": contact_id,

                "contact_name": contact_name,

                "category_id": (
                    self.category_combo
                    .currentData()
                ),

                "description": (
                        self.description_input
                        .text()
                        .strip()
                        or None
                ),

                "notes": (
                        self.notes_input
                        .toPlainText()
                        .strip()
                        or None
                ),
            },

            "classification": {
                "mode": mode,
                "reference_id": reference_id,
                "reference_month": reference_month,
                "reference_year": reference_year,
            },
        }

    # =========================================================
    # HELPERS
    # =========================================================

    def _selecionar_combo(
            self,
            combo: QComboBox,
            value,
    ) -> None:

        index = combo.findData(
            value
        )

        if index >= 0:

            combo.setCurrentIndex(
                index
            )

    def _formatar_moeda(
            self,
            cents: int,
    ) -> str:

        valor = (
            int(cents or 0)
            / 100
        )

        texto = (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"R$ {texto}"
        )

    # =========================================================
    # ESTILO
    # =========================================================

    def _aplicar_estilo(
            self,
    ) -> None:

        self.setStyleSheet(
            """
            QDialog#PixTransactionDialog {
                background-color: #f8fafc;
                font-family: Segoe UI;
            }

            QLabel#PixDialogTitle {
                color: #0f172a;
                font-size: 21px;
                font-weight: 700;
            }

            QLabel#PixFieldLabel {
                color: #334155;
                font-size: 12px;
                font-weight: 600;
            }

            QFrame#PixSeparator {
                color: #e2e8f0;
                background-color: #e2e8f0;
                max-height: 1px;
            }

            QLineEdit,
            QComboBox,
            QDateEdit,
            QTextEdit {
                background-color: white;
                border: 1px solid #dbe3ed;
                border-radius: 14px;
                padding: 8px 12px;
                color: #0f172a;
                font-size: 12px;
            }

            QComboBox {
                padding-right: 28px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 26px;
            }
            
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }

            QLineEdit,
            QComboBox,
            QDateEdit {
                min-height: 20px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QDateEdit:focus,
            QTextEdit:focus {
                border: 1px solid #60a5fa;
            }

            QPushButton[classificationButton="true"] {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 5px;
                color: #64748b;
                font-size: 10px;
            }

            QPushButton[classificationButton="true"]:hover {
                background-color: #f1f5f9;
                color: #334155;
            }

            QPushButton[classificationButton="true"]:checked {
                background-color: #eff6ff;
                border: 1px solid #60a5fa;
                color: #2563eb;
                font-weight: 700;
            }

            QFrame#PixDynamicFrame {
                background-color: transparent;
                border: none;
            }

            QPushButton#PixDialogClose {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #64748b;
                font-size: 22px;
            }

            QPushButton#PixDialogClose:hover {
                background-color: #e2e8f0;
                color: #0f172a;
            }

            QPushButton#PixCancelButton {
                background-color: white;
                border: 1px solid #dbe3ed;
                border-radius: 9px;
                padding: 9px 18px;
                color: #475569;
                font-size: 12px;
            }

            QPushButton#PixCancelButton:hover {
                background-color: #f1f5f9;
            }

            QPushButton#PixSaveButton {
                background-color: #2563eb;
                border: none;
                border-radius: 9px;
                padding: 10px 20px;
                color: white;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton#PixSaveButton:hover {
                background-color: #1d4ed8;
            }
            
            QComboBox#ReferencePeriodCombo {
                padding-left: 10px;
                padding-right: 14px;
            }
            
            QComboBox#ReferencePeriodCombo::drop-down {
                width: 14px;
                border: none;
            }
            """
        )