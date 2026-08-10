from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class PixTransactionDialog(QDialog):
    def __init__(
            self,
            accounts: list[dict],
            categories: list[dict],
            transaction_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = accounts
        self.categories = categories
        self.transaction_data = transaction_data

        self.setWindowTitle(
            "Editar PIX"
            if transaction_data
            else "Novo PIX"
        )

        self.setMinimumWidth(460)

        self._montar_interface()

        if self.transaction_data:
            self._carregar_dados()

    def _montar_interface(
            self,
    ) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            22,
            24,
            20,
        )

        layout.setSpacing(12)

        titulo = QLabel(
            "Editar PIX"
            if self.transaction_data
            else "Novo PIX"
        )

        titulo.setStyleSheet(
            "font-size: 20px; "
            "font-weight: bold; "
            "color: #0f172a;"
        )

        layout.addWidget(
            titulo
        )

        # -------------------------------------------------
        # TIPO
        # -------------------------------------------------

        self.type_combo = QComboBox()

        self.type_combo.addItem(
            "PIX enviado",
            "sent",
        )

        self.type_combo.addItem(
            "PIX recebido",
            "received",
        )

        # -------------------------------------------------
        # CONTA
        # -------------------------------------------------

        self.account_combo = QComboBox()

        self.account_combo.addItem(
            "Selecione uma conta",
            None,
        )

        for account in self.accounts:
            account_name = (
                account.get("name")
                or "Conta"
            )

            institution_name = (
                account.get(
                    "institution_name"
                )
            )

            if institution_name:
                texto = (
                    f"{account_name} "
                    f"— {institution_name}"
                )
            else:
                texto = account_name

            self.account_combo.addItem(
                texto,
                account["id"],
            )

        # -------------------------------------------------
        # VALOR
        # -------------------------------------------------

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "0,00"
        )

        self.amount_input.textChanged.connect(
            self._formatar_valor_digitado
        )

        # -------------------------------------------------
        # DATA
        # -------------------------------------------------

        self.date_input = QDateEdit()

        self.date_input.setCalendarPopup(
            True
        )

        self.date_input.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.date_input.setDate(
            QDate.currentDate()
        )

        # -------------------------------------------------
        # CONTATO
        # -------------------------------------------------

        self.contact_name_input = QLineEdit()

        self.contact_name_input.setPlaceholderText(
            "Opcional"
        )

        # -------------------------------------------------
        # CATEGORIA
        # -------------------------------------------------

        self.category_combo = QComboBox()

        for category in self.categories:
            self.category_combo.addItem(
                category["name"],
                category["id"],
            )

        # -------------------------------------------------
        # DESCRIÇÃO
        # -------------------------------------------------

        self.description_input = QLineEdit()

        self.description_input.setPlaceholderText(
            "Ex.: Almoço, aluguel, reembolso..."
        )

        # -------------------------------------------------
        # OBSERVAÇÕES
        # -------------------------------------------------

        self.notes_input = QTextEdit()

        self.notes_input.setPlaceholderText(
            "Observações..."
        )

        self.notes_input.setFixedHeight(
            78
        )

        # -------------------------------------------------
        # LAYOUT
        # -------------------------------------------------

        layout.addWidget(
            QLabel("Tipo")
        )
        layout.addWidget(
            self.type_combo
        )

        layout.addWidget(
            QLabel("Conta")
        )
        layout.addWidget(
            self.account_combo
        )

        layout.addWidget(
            QLabel("Valor")
        )
        layout.addWidget(
            self.amount_input
        )

        layout.addWidget(
            QLabel("Data")
        )
        layout.addWidget(
            self.date_input
        )

        layout.addWidget(
            QLabel("Contato / Nome")
        )
        layout.addWidget(
            self.contact_name_input
        )

        layout.addWidget(
            QLabel("Categoria")
        )
        layout.addWidget(
            self.category_combo
        )

        layout.addWidget(
            QLabel("Descrição")
        )
        layout.addWidget(
            self.description_input
        )

        layout.addWidget(
            QLabel("Observações")
        )
        layout.addWidget(
            self.notes_input
        )

        botoes = QHBoxLayout()

        botoes.addStretch()

        cancelar = QPushButton(
            "Cancelar"
        )

        cancelar.clicked.connect(
            self.reject
        )

        salvar = QPushButton(
            "Salvar"
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

    def _carregar_dados(
            self,
    ) -> None:

        type_index = (
            self.type_combo.findData(
                self.transaction_data.get(
                    "transaction_type"
                )
            )
        )

        if type_index >= 0:
            self.type_combo.setCurrentIndex(
                type_index
            )

        account_index = (
            self.account_combo.findData(
                self.transaction_data.get(
                    "account_id"
                )
            )
        )

        if account_index >= 0:
            self.account_combo.setCurrentIndex(
                account_index
            )

        self.amount_input.setText(
            self._formatar_centavos_para_texto(
                self.transaction_data.get(
                    "amount_cents",
                    0,
                )
            )
        )

        transaction_date = (
            self.transaction_data.get(
                "transaction_date"
            )
        )

        if transaction_date:
            self.date_input.setDate(
                QDate.fromString(
                    transaction_date,
                    "yyyy-MM-dd",
                )
            )

        self.contact_name_input.setText(
            self.transaction_data.get(
                "contact_name"
            )
            or ""
        )

        category_index = (
            self.category_combo.findData(
                self.transaction_data.get(
                    "category_id"
                )
            )
        )

        if category_index >= 0:
            self.category_combo.setCurrentIndex(
                category_index
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

    def _formatar_valor_digitado(
            self,
    ) -> None:

        texto = self.amount_input.text()

        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return

        texto_formatado = (
            self._formatar_centavos_para_texto(
                int(apenas_digitos)
            )
        )

        if texto == texto_formatado:
            return

        self.amount_input.blockSignals(
            True
        )

        self.amount_input.setText(
            texto_formatado
        )

        self.amount_input.setCursorPosition(
            len(texto_formatado)
        )

        self.amount_input.blockSignals(
            False
        )

    def _formatar_centavos_para_texto(
            self,
            valor_cents: int,
    ) -> str:

        valor = (
            valor_cents
            / 100
        )

        texto = f"{valor:,.2f}"

        return (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _converter_texto_para_centavos(
            self,
            texto: str,
    ) -> int:

        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return 0

        return int(
            apenas_digitos
        )

    def _salvar(
            self,
    ) -> None:

        account_id = (
            self.account_combo
            .currentData()
        )

        if account_id is None:
            QMessageBox.warning(
                self,
                "Conta obrigatória",
                "Selecione a conta do PIX.",
            )
            return

        valor_cents = (
            self._converter_texto_para_centavos(
                self.amount_input.text()
            )
        )

        if valor_cents <= 0:
            QMessageBox.warning(
                self,
                "Valor inválido",
                "Informe um valor maior que zero.",
            )
            return

        self.accept()

    def obter_dados(
            self,
    ) -> dict:

        return {
            "account_id": (
                self.account_combo
                .currentData()
            ),

            "transaction_type": (
                self.type_combo
                .currentData()
            ),

            "amount_cents": (
                self._converter_texto_para_centavos(
                    self.amount_input.text()
                )
            ),

            "transaction_date": (
                self.date_input
                .date()
                .toString(
                    "yyyy-MM-dd"
                )
            ),

            "contact_id": None,

            "contact_name": (
                self.contact_name_input
                .text()
                .strip()
                or None
            ),

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
        }