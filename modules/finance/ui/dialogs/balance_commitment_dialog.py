from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
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


class BalanceCommitmentDialog(QDialog):
    def __init__(
            self,
            accounts: list[dict],
            commitment_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = accounts
        self.commitment_data = commitment_data

        self.setWindowTitle(
            "Editar compromisso" if commitment_data else "Novo compromisso"
        )
        self.setMinimumWidth(460)

        self._montar_interface()

        if self.commitment_data:
            self._carregar_dados()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        titulo = QLabel(
            "Editar compromisso" if self.commitment_data else "Novo compromisso"
        )
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Ex.: Aluguel, Internet, Luz")

        self.account_combo = QComboBox()
        self.account_combo.addItem("Selecione uma conta", None)

        for account in self.accounts:
            self.account_combo.addItem(
                account["name"],
                account["id"],
            )

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0,00")
        self.amount_input.textChanged.connect(
            self._formatar_valor_digitado
        )

        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDisplayFormat("dd/MM/yyyy")
        self.due_date_input.setDate(QDate.currentDate())

        self.recurring_checkbox = QCheckBox("Compromisso recorrente")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Observações...")
        self.notes_input.setFixedHeight(78)

        layout.addWidget(titulo)

        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("Conta de pagamento"))
        layout.addWidget(self.account_combo)

        layout.addWidget(QLabel("Valor previsto"))
        layout.addWidget(self.amount_input)

        layout.addWidget(QLabel("Data de vencimento"))
        layout.addWidget(self.due_date_input)

        layout.addWidget(self.recurring_checkbox)

        layout.addWidget(QLabel("Observações"))
        layout.addWidget(self.notes_input)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self._salvar)

        botoes.addWidget(cancelar)
        botoes.addWidget(salvar)

        layout.addLayout(botoes)

    def _carregar_dados(self) -> None:
        self.description_input.setText(
            self.commitment_data["description"]
        )

        account_index = self.account_combo.findData(
            self.commitment_data["account_id"]
        )

        if account_index >= 0:
            self.account_combo.setCurrentIndex(account_index)

        self.amount_input.setText(
            self._formatar_centavos_para_texto(
                self.commitment_data["expected_amount_cents"]
            )
        )

        self.due_date_input.setDate(
            QDate.fromString(
                self.commitment_data["due_date"],
                "yyyy-MM-dd",
            )
        )

        self.recurring_checkbox.setChecked(
            bool(self.commitment_data["is_recurring"])
        )

        self.notes_input.setPlainText(
            self.commitment_data["notes"] or ""
        )

    def _formatar_valor_digitado(self) -> None:
        texto = self.amount_input.text()

        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return

        texto_formatado = self._formatar_centavos_para_texto(
            int(apenas_digitos)
        )

        if texto == texto_formatado:
            return

        self.amount_input.blockSignals(True)
        self.amount_input.setText(texto_formatado)
        self.amount_input.setCursorPosition(len(texto_formatado))
        self.amount_input.blockSignals(False)

    def _formatar_centavos_para_texto(
            self,
            valor_cents: int,
    ) -> str:
        valor = valor_cents / 100
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

        return int(apenas_digitos)

    def _salvar(self) -> None:
        if not self.description_input.text().strip():
            QMessageBox.warning(
                self,
                "Descrição obrigatória",
                "Informe a descrição do compromisso.",
            )
            return

        if self.account_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Conta obrigatória",
                "Selecione a conta de pagamento.",
            )
            return

        if self._converter_texto_para_centavos(
                self.amount_input.text()
        ) <= 0:
            QMessageBox.warning(
                self,
                "Valor inválido",
                "Informe um valor maior que zero.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        return {
            "description": self.description_input.text().strip(),
            "expected_amount_cents": self._converter_texto_para_centavos(
                self.amount_input.text()
            ),
            "due_date": self.due_date_input.date().toString("yyyy-MM-dd"),
            "payment_type": "bank_account",
            "account_id": self.account_combo.currentData(),
            "credit_card_id": None,
            "is_recurring": self.recurring_checkbox.isChecked(),
            "notes": self.notes_input.toPlainText().strip() or None,
        }