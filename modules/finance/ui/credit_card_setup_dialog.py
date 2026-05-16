from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QComboBox,
    QFrame,
)


class CreditCardSetupDialog(QDialog):
    def __init__(
            self,
            assets: list[dict],
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.assets = assets

        self.setWindowTitle("Configurar cartão")
        self.setModal(True)
        self.setMinimumSize(760, 520)
        self.setObjectName("CreditCardSetupDialog")

        self.selected_asset_id = (
            assets[0]["id"]
            if assets
            else "generico_1"
        )

        self._criar_layout()
        self._atualizar_preview()

    def _criar_layout(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 26, 28, 24)
        main_layout.setSpacing(20)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        title = QLabel("Configurar cartão de crédito")
        title.setObjectName("CardCatalogDialogTitle")

        subtitle = QLabel("Defina as informações iniciais do cartão.")
        subtitle.setObjectName("CardCatalogDialogSubtitle")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        preview_title = QLabel("Prévia do cartão")
        preview_title.setObjectName("CardCatalogDialogSubtitle")

        self.preview_card = QFrame()
        self.preview_card.setMinimumSize(300, 190)
        self.preview_card.setObjectName("CreditCardPreview")

        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(22, 20, 22, 20)
        preview_layout.setSpacing(10)

        self.preview_name = QLabel("Meu Cartão")
        self.preview_name.setObjectName("CreditCardPreviewName")

        self.preview_invoice = QLabel("Fatura atual: R$ 0,00")
        self.preview_invoice.setObjectName("CreditCardPreviewInvoice")

        self.preview_dates = QLabel("Fecha dia 05 • Vence dia 15")
        self.preview_dates.setObjectName("CreditCardPreviewDates")

        self.preview_digits = QLabel("•••• 0000")
        self.preview_digits.setAlignment(Qt.AlignRight)
        self.preview_digits.setObjectName("CreditCardPreviewDigits")

        preview_layout.addWidget(self.preview_name)
        preview_layout.addStretch()
        preview_layout.addWidget(self.preview_invoice)
        preview_layout.addWidget(self.preview_dates)
        preview_layout.addWidget(self.preview_digits)

        left_layout.addWidget(preview_title)
        left_layout.addWidget(self.preview_card)
        left_layout.addStretch()

        form_layout = QVBoxLayout()
        form_layout.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Nubank, BB Visa, Cartão Inter")
        self.name_input.textChanged.connect(self._atualizar_preview)

        self.asset_combo = QComboBox()

        for asset in self.assets:
            self.asset_combo.addItem(
                f'{asset["bank_name"]} — {asset["asset_name"]}',
                asset["id"],
            )

        self.asset_combo.currentIndexChanged.connect(
            self._asset_alterado
        )

        self.limit_input = QLineEdit()
        self.limit_input.setPlaceholderText("Ex: 5000,00")

        self.closing_day_input = QSpinBox()
        self.closing_day_input.setRange(1, 31)
        self.closing_day_input.setValue(5)
        self.closing_day_input.valueChanged.connect(self._atualizar_preview)

        self.due_day_input = QSpinBox()
        self.due_day_input.setRange(1, 31)
        self.due_day_input.setValue(15)
        self.due_day_input.valueChanged.connect(self._atualizar_preview)

        self.last_digits_input = QLineEdit()
        self.last_digits_input.setPlaceholderText("Últimos 4 dígitos")
        self.last_digits_input.setMaxLength(4)
        self.last_digits_input.textChanged.connect(self._atualizar_preview)

        form_layout.addWidget(QLabel("Nome do cartão"))
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("Fundo / asset"))
        form_layout.addWidget(self.asset_combo)

        form_layout.addWidget(QLabel("Limite"))
        form_layout.addWidget(self.limit_input)

        days_layout = QHBoxLayout()
        days_layout.setSpacing(14)

        closing_layout = QVBoxLayout()
        closing_layout.setSpacing(6)
        closing_layout.addWidget(QLabel("Fechamento"))
        closing_layout.addWidget(self.closing_day_input)

        due_layout = QVBoxLayout()
        due_layout.setSpacing(6)
        due_layout.addWidget(QLabel("Vencimento"))
        due_layout.addWidget(self.due_day_input)

        days_layout.addLayout(closing_layout)
        days_layout.addLayout(due_layout)

        form_layout.addLayout(days_layout)

        form_layout.addWidget(QLabel("Número mascarado"))
        form_layout.addWidget(self.last_digits_input)

        form_layout.addStretch()

        content_layout.addLayout(left_layout, stretch=1)
        content_layout.addLayout(form_layout, stretch=1)

        main_layout.addLayout(content_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumHeight(38)
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Salvar cartão")
        save_button.setObjectName("PrimarySoftButton")
        save_button.setMinimumHeight(38)
        save_button.clicked.connect(self.accept)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

    def _asset_alterado(self) -> None:
        self.selected_asset_id = self.asset_combo.currentData()
        self._atualizar_preview()

    def _get_selected_asset(self) -> dict:
        for asset in self.assets:
            if asset["id"] == self.selected_asset_id:
                return asset

        return {
            "background_value": "#2563EB",
            "text_color": "#FFFFFF",
        }

    def _atualizar_preview(self) -> None:
        asset = self._get_selected_asset()

        background = asset.get("background_value", "#2563EB")
        text_color = asset.get("text_color", "#FFFFFF")

        self.preview_card.setStyleSheet(f"""
            QFrame#CreditCardPreview {{
                background-color: {background};
                border-radius: 22px;
            }}

            QLabel {{
                color: {text_color};
            }}
        """)

        name = self.name_input.text().strip() or "Meu Cartão"
        digits = self.last_digits_input.text().strip() or "0000"

        self.preview_name.setText(name)
        self.preview_dates.setText(
            f"Fecha dia {self.closing_day_input.value():02d} • "
            f"Vence dia {self.due_day_input.value():02d}"
        )
        self.preview_digits.setText(f"•••• {digits}")

    def _parse_money_to_cents(
            self,
            text: str,
    ) -> int:
        cleaned = (
            text.strip()
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
        )

        if not cleaned:
            return 0

        value = float(cleaned)

        return int(round(value * 100))

    def get_data(self) -> dict:
        asset = self._get_selected_asset()

        return {
            "name": self.name_input.text().strip() or "Meu Cartão",
            "asset_id": self.selected_asset_id,

            "bank_name": asset.get("bank_name"),
            "asset_name": asset.get("asset_name"),
            "background_type": asset.get("background_type", "color"),
            "background_value": asset.get("background_value", "#2563EB"),
            "text_color": asset.get("text_color", "#FFFFFF"),

            "limit_amount_cents": self._parse_money_to_cents(
                self.limit_input.text()
            ),
            "closing_day": self.closing_day_input.value(),
            "due_day": self.due_day_input.value(),
            "last_four_digits": self.last_digits_input.text().strip() or None,
        }