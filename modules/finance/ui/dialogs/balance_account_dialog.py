from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QPushButton,
    QVBoxLayout,
)


class BalanceAccountDialog(QDialog):
    BANK_OPTIONS = [
        ("Nubank", "nubank"),
        ("Banco Inter", "inter"),
        ("Itaú", "itau"),
        ("Bradesco", "bradesco"),
        ("Santander", "santander"),
        ("Banco do Brasil", "bb"),
        ("Caixa", "caixa"),
        ("BTG Pactual", "btg"),
        ("XP", "xp"),
        ("PicPay", "picpay"),
        ("Mercado Pago", "mercado_pago"),
        ("PagBank", "pagbank"),
        ("Outro...", "other"),
    ]

    def __init__(self, account_data: dict | None = None, parent=None) -> None:
        super().__init__(parent)

        self.account_data = account_data

        self.setWindowTitle("Editar conta" if account_data else "Nova conta")
        self.setMinimumWidth(480)

        self._montar_interface()

        if self.account_data:
            self._carregar_dados()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        titulo = QLabel(
            "Editar conta financeira" if self.account_data else "Nova conta financeira"
        )
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        layout.addWidget(titulo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex.: Nubank Principal")

        self.bank_combo = QComboBox()
        for label, key in self.BANK_OPTIONS:
            self.bank_combo.addItem(label, key)

        self.custom_bank_input = QLineEdit()
        self.custom_bank_input.setPlaceholderText("Nome do banco/instituição")
        self.custom_bank_input.setVisible(False)

        self.bank_combo.currentIndexChanged.connect(
            self._atualizar_campo_banco_customizado
        )

        self.type_combo = QComboBox()
        self.type_combo.addItem("Banco", "bank")
        self.type_combo.addItem("Carteira", "wallet")
        self.type_combo.addItem("Dinheiro", "cash")

        self.account_kind_combo = QComboBox()
        self.account_kind_combo.addItem("Conta corrente", "checking")
        self.account_kind_combo.addItem("Conta poupança", "savings")
        self.account_kind_combo.addItem("Conta pagamento", "payment")
        self.account_kind_combo.addItem("Outro", "other")

        self.agency_input = QLineEdit()
        self.agency_input.setPlaceholderText("Ex.: 0001")

        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("Ex.: 123456-7")

        self.opening_balance_input = QLineEdit()
        self.opening_balance_input.setPlaceholderText("0,00")
        self.opening_balance_input.textChanged.connect(
            self._formatar_valor_digitado
        )

        self.global_checkbox = QCheckBox("Participa do saldo global")
        self.global_checkbox.setChecked(True)

        self.investment_checkbox = QCheckBox("Conta de investimento")

        layout.addWidget(QLabel("Nome da conta"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Banco / Instituição"))
        layout.addWidget(self.bank_combo)
        layout.addWidget(self.custom_bank_input)

        layout.addWidget(QLabel("Tipo da conta no sistema"))
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Tipo bancário"))
        layout.addWidget(self.account_kind_combo)

        layout.addWidget(QLabel("Agência"))
        layout.addWidget(self.agency_input)

        layout.addWidget(QLabel("Número da conta"))
        layout.addWidget(self.account_number_input)

        layout.addWidget(QLabel("Saldo inicial"))
        layout.addWidget(self.opening_balance_input)

        layout.addWidget(self.global_checkbox)
        layout.addWidget(self.investment_checkbox)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self._salvar)

        botoes.addWidget(cancelar)
        botoes.addWidget(salvar)

        layout.addLayout(botoes)

    def _atualizar_campo_banco_customizado(self) -> None:
        self.custom_bank_input.setVisible(
            self.bank_combo.currentData() == "other"
        )

    def _carregar_dados(self) -> None:
        self.name_input.setText(self.account_data["name"])

        bank_key = self.account_data.get("bank_preset_key")

        index = self.bank_combo.findData(bank_key)

        if index >= 0:
            self.bank_combo.setCurrentIndex(index)
        else:
            self.bank_combo.setCurrentIndex(
                self.bank_combo.findData("other")
            )
            self.custom_bank_input.setText(
                self.account_data.get("institution_name") or ""
            )

        self._atualizar_campo_banco_customizado()

        type_index = self.type_combo.findData(
            self.account_data["account_type"]
        )

        if type_index >= 0:
            self.type_combo.setCurrentIndex(type_index)

        kind_index = self.account_kind_combo.findData(
            self.account_data.get("account_kind")
        )

        if kind_index >= 0:
            self.account_kind_combo.setCurrentIndex(kind_index)

        self.agency_input.setText(
            self.account_data.get("agency") or ""
        )

        self.account_number_input.setText(
            self.account_data.get("account_number") or ""
        )

        self.opening_balance_input.setText("0,00")

        self.global_checkbox.setChecked(
            bool(self.account_data["include_in_global_balance"])
        )

        self.investment_checkbox.setChecked(
            bool(self.account_data["is_investment"])
        )

    def _formatar_valor_digitado(self) -> None:
        texto = self.opening_balance_input.text()

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

        self.opening_balance_input.blockSignals(True)
        self.opening_balance_input.setText(texto_formatado)
        self.opening_balance_input.setCursorPosition(len(texto_formatado))
        self.opening_balance_input.blockSignals(False)

    def _formatar_centavos_para_texto(self, valor_cents: int) -> str:
        valor = valor_cents / 100
        texto = f"{valor:,.2f}"

        return (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _converter_texto_para_centavos(self, texto: str) -> int:
        apenas_digitos = "".join(
            caractere
            for caractere in texto
            if caractere.isdigit()
        )

        if not apenas_digitos:
            return 0

        return int(apenas_digitos)

    def _salvar(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Nome obrigatório",
                "Informe o nome da conta.",
            )
            return

        if self.bank_combo.currentData() == "other":
            if not self.custom_bank_input.text().strip():
                QMessageBox.warning(
                    self,
                    "Banco obrigatório",
                    "Informe o nome do banco/instituição.",
                )
                return

        self.accept()

    def obter_dados(self) -> dict:
        bank_preset_key = self.bank_combo.currentData()

        if bank_preset_key == "other":
            institution_name = self.custom_bank_input.text().strip()
        else:
            institution_name = self.bank_combo.currentText()

        return {
            "name": self.name_input.text().strip(),
            "account_type": self.type_combo.currentData(),
            "institution_name": institution_name,
            "bank_preset_key": bank_preset_key,
            "agency": self.agency_input.text().strip() or None,
            "account_number": self.account_number_input.text().strip() or None,
            "account_kind": self.account_kind_combo.currentData(),
            "opening_balance_cents": self._converter_texto_para_centavos(
                self.opening_balance_input.text()
            ),
            "include_in_global_balance": self.global_checkbox.isChecked(),
            "is_investment": self.investment_checkbox.isChecked(),
        }