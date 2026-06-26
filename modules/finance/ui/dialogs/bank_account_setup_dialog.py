from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from modules.finance.services.bank_account_asset_resolver import (
    BankAccountAssetResolver,
)

from modules.finance.ui.widget.bank_account_widget import (
    BankAccountWidget,
)


class BankAccountPreviewWidget(BankAccountWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(
            card_data={
                "config": {
                    "name": "Conta Principal",
                    "institution_name": "Banco",
                    "bank_preset_key": "generic_bank",
                    "account_kind": "checking",
                    "current_balance_cents": 0,
                    "projected_balance_cents": 0,
                    "projected_date": "",
                    "pix_scheduled_count": 0,
                }
            },
            parent=parent,
        )

        self.setMinimumSize(340, 215)

    def set_preview_data(self, config: dict) -> None:
        self.update_card_data(
            {
                "config": config,
            }
        )


class BankAccountSetupDialog(QDialog):
    def __init__(
            self,
            account_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.account_data = account_data
        self.asset_resolver = BankAccountAssetResolver()

        self.setWindowTitle(
            "Editar conta bancária"
            if account_data
            else "Configurar conta bancária"
        )
        self.setModal(True)
        self.setMinimumSize(760, 520)
        self.setObjectName("BankAccountSetupDialog")

        self._criar_layout()

        if self.account_data:
            self._carregar_dados()

        self._atualizar_preview()

    def _criar_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 26, 28, 24)
        main_layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        title = QLabel(
            "Editar conta bancária"
            if self.account_data
            else "Configurar conta bancária"
        )
        title.setObjectName("CardCatalogDialogTitle")

        subtitle = QLabel(
            "Defina as informações iniciais da conta."
        )
        subtitle.setObjectName("CardCatalogDialogSubtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        preview_title = QLabel("Prévia da conta")
        preview_title.setObjectName("CardCatalogDialogSubtitle")

        self.preview_account = BankAccountPreviewWidget()

        left_layout.addWidget(preview_title)
        left_layout.addWidget(self.preview_account)
        left_layout.addStretch()

        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Nubank Principal")
        self.name_input.textChanged.connect(self._atualizar_preview)

        self.bank_combo = QComboBox()

        for preset in self.asset_resolver.listar_presets():
            self.bank_combo.addItem(
                preset.label,
                preset.key,
            )

        self.bank_combo.currentIndexChanged.connect(
            self._bank_alterado
        )

        self.custom_bank_input = QLineEdit()
        self.custom_bank_input.setPlaceholderText(
            "Nome do banco/instituição"
        )
        self.custom_bank_input.setVisible(False)
        self.custom_bank_input.textChanged.connect(
            self._atualizar_preview
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
        self.account_kind_combo.currentIndexChanged.connect(
            self._atualizar_preview
        )

        self.agency_input = QLineEdit()
        self.agency_input.setPlaceholderText("Ex: 0001")
        self.agency_input.textChanged.connect(self._atualizar_preview)

        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("Ex: 123456-7")
        self.account_number_input.textChanged.connect(
            self._atualizar_preview
        )

        self.opening_balance_input = QLineEdit()
        self.opening_balance_input.setPlaceholderText("0,00")
        self.opening_balance_input.textChanged.connect(
            self._formatar_valor_digitado
        )
        self.opening_balance_input.textChanged.connect(
            self._atualizar_preview
        )

        self.global_checkbox = QCheckBox(
            "Participa do saldo global"
        )
        self.global_checkbox.setChecked(True)

        self.investment_checkbox = QCheckBox(
            "Conta de investimento"
        )

        form_layout.addWidget(QLabel("Nome da conta"))
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("Banco / asset"))
        form_layout.addWidget(self.bank_combo)
        form_layout.addWidget(self.custom_bank_input)

        form_layout.addWidget(QLabel("Tipo da conta no sistema"))
        form_layout.addWidget(self.type_combo)

        form_layout.addWidget(QLabel("Tipo bancário"))
        form_layout.addWidget(self.account_kind_combo)

        account_numbers_layout = QHBoxLayout()
        account_numbers_layout.setSpacing(14)

        agency_layout = QVBoxLayout()
        agency_layout.setSpacing(6)
        agency_layout.addWidget(QLabel("Agência"))
        agency_layout.addWidget(self.agency_input)

        number_layout = QVBoxLayout()
        number_layout.setSpacing(6)
        number_layout.addWidget(QLabel("Número da conta"))
        number_layout.addWidget(self.account_number_input)

        account_numbers_layout.addLayout(agency_layout)
        account_numbers_layout.addLayout(number_layout)

        form_layout.addLayout(account_numbers_layout)

        form_layout.addWidget(QLabel("Saldo inicial"))
        form_layout.addWidget(self.opening_balance_input)

        form_layout.addWidget(self.global_checkbox)
        form_layout.addWidget(self.investment_checkbox)

        form_layout.addStretch()

        content_layout.addLayout(left_layout, stretch=1)
        content_layout.addLayout(form_layout, stretch=1)

        main_layout.addLayout(content_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumHeight(38)
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Salvar conta")
        save_button.setObjectName("PrimarySoftButton")
        save_button.setMinimumHeight(38)
        save_button.clicked.connect(self._salvar)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

    def _bank_alterado(self) -> None:
        self.custom_bank_input.setVisible(
            self.bank_combo.currentData() == "generic_bank"
        )
        self._atualizar_preview()

    def _carregar_dados(self) -> None:
        self.name_input.setText(
            self.account_data.get("name") or ""
        )

        bank_key = (
            self.account_data.get("bank_preset_key")
            or "generic_bank"
        )

        index = self.bank_combo.findData(bank_key)

        if index >= 0:
            self.bank_combo.setCurrentIndex(index)
        else:
            self.bank_combo.setCurrentIndex(
                self.bank_combo.findData("generic_bank")
            )
            self.custom_bank_input.setText(
                self.account_data.get("institution_name") or ""
            )

        self._bank_alterado()

        type_index = self.type_combo.findData(
            self.account_data.get("account_type")
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

        self.opening_balance_input.setText(
            self._formatar_centavos_para_texto(
                self.account_data.get("opening_balance_cents", 0)
            )
        )

        self.global_checkbox.setChecked(
            bool(
                self.account_data.get(
                    "include_in_global_balance",
                    True,
                )
            )
        )

        self.investment_checkbox.setChecked(
            bool(
                self.account_data.get(
                    "is_investment",
                    False,
                )
            )
        )

    def _atualizar_preview(self) -> None:
        bank_preset_key = self.bank_combo.currentData()

        institution_name = self._obter_nome_instituicao()

        opening_balance_cents = self._converter_texto_para_centavos(
            self.opening_balance_input.text()
        )

        self.preview_account.set_preview_data(
            {
                "name": self.name_input.text().strip() or "Conta Principal",
                "institution_name": institution_name,
                "bank_preset_key": bank_preset_key,
                "account_kind": self.account_kind_combo.currentData(),
                "agency": self.agency_input.text().strip() or None,
                "account_number": (
                    self.account_number_input.text().strip()
                    or None
                ),
                "current_balance_cents": opening_balance_cents,
                "projected_balance_cents": opening_balance_cents,
                "projected_date": "",
                "pix_scheduled_count": 0,
            }
        )

    def _obter_nome_instituicao(self) -> str:
        if self.bank_combo.currentData() == "generic_bank":
            return (
                self.custom_bank_input.text().strip()
                or "Banco"
            )

        preset = self.asset_resolver.obter_preset(
            self.bank_combo.currentData()
        )

        if preset is None:
            return self.bank_combo.currentText()

        return preset.institution

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
        self.opening_balance_input.setCursorPosition(
            len(texto_formatado)
        )
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

        if self.bank_combo.currentData() == "generic_bank":
            if not self.custom_bank_input.text().strip():
                QMessageBox.warning(
                    self,
                    "Banco obrigatório",
                    "Informe o nome do banco/instituição.",
                )
                return

        self.accept()

    def obter_dados(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "account_type": self.type_combo.currentData(),
            "institution_name": self._obter_nome_instituicao(),
            "bank_preset_key": self.bank_combo.currentData(),
            "agency": self.agency_input.text().strip() or None,
            "account_number": (
                self.account_number_input.text().strip()
                or None
            ),
            "account_kind": self.account_kind_combo.currentData(),
            "opening_balance_cents": self._converter_texto_para_centavos(
                self.opening_balance_input.text()
            ),
            "include_in_global_balance": self.global_checkbox.isChecked(),
            "is_investment": self.investment_checkbox.isChecked(),
        }