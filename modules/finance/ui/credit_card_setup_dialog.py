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
        self.setMinimumSize(520, 520)
        self.setObjectName("CreditCardSetupDialog")

        self.selected_asset_id = (
            assets[0]["id"]
            if assets
            else "generico_1"
        )

        self._criar_layout()
        self._atualizar_preview()

    def _criar_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        title = QLabel("Configurar cartão de crédito")
        title.setObjectName("CardCatalogDialogTitle")

        subtitle = QLabel("Defina as informações iniciais do cartão.")
        subtitle.setObjectName("CardCatalogDialogSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.preview_card = QFrame()
        self.preview_card.setFixedHeight(140)
        self.preview_card.setObjectName("CreditCardPreview")

        preview_layout = QVBoxLayout(self.preview_card)
        preview_layout.setContentsMargins(18, 16, 18, 16)
        preview_layout.setSpacing(8)

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

        layout.addWidget(self.preview_card)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do cartão")
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
        self.limit_input.setPlaceholderText("Limite do cartão. Ex: 5000,00")

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

        layout.addWidget(QLabel("Nome"))
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Fundo / asset"))
        layout.addWidget(self.asset_combo)

        layout.addWidget(QLabel("Limite"))
        layout.addWidget(self.limit_input)

        days_layout = QHBoxLayout()

        closing_layout = QVBoxLayout()
        closing_layout.addWidget(QLabel("Fechamento"))
        closing_layout.addWidget(self.closing_day_input)

        due_layout = QVBoxLayout()
        due_layout.addWidget(QLabel("Vencimento"))
        due_layout.addWidget(self.due_day_input)

        days_layout.addLayout(closing_layout)
        days_layout.addLayout(due_layout)

        layout.addLayout(days_layout)

        layout.addWidget(QLabel("Número mascarado"))
        layout.addWidget(self.last_digits_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Salvar cartão")
        save_button.setObjectName("PrimarySoftButton")
        save_button.clicked.connect(self.accept)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        layout.addStretch()
        layout.addLayout(buttons_layout)

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