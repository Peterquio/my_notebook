from PySide6.QtGui import QPainter, QPixmap, QColor, QFont
from PySide6.QtCore import Qt, QRectF
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

from modules.finance.services.credit_card_asset_resolver import CreditCardAssetResolver


class CreditCardPreviewWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setMinimumSize(340, 215)
        self.setObjectName("CreditCardPreview")

        self.background_color = "#2563EB"
        self.name = "Meu Cartão"
        self.digits = "0000"
        self.dates = "Fecha dia 05 • Vence dia 15"

        self.background_path = None
        self.overlay_path = None
        self.issuer_path = None
        self.brand_path = None
        self.chip_path = None

    def set_card_data(
            self,
            background_color: str,
            name: str,
            digits: str,
            dates: str,
            background_path=None,
            overlay_path=None,
            issuer_path=None,
            brand_path=None,
            chip_path=None,
    ) -> None:
        self.background_color = background_color
        self.name = name
        self.digits = digits
        self.dates = dates
        self.background_path = background_path
        self.overlay_path = overlay_path
        self.issuer_path = issuer_path
        self.brand_path = brand_path
        self.chip_path = chip_path

        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)

        painter.setBrush(QColor(self.background_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 24, 24)

        self._draw_pixmap_cover(painter, self.background_path, rect)
        self._draw_pixmap_cover(painter, self.overlay_path, rect)

        self._draw_pixmap_fit(
            painter=painter,
            path=self.issuer_path,
            x=24,
            y=22,
            width=92,
            height=38,
        )

        self._draw_pixmap_fit(
            painter=painter,
            path=self.chip_path,
            x=26,
            y=82,
            width=54,
            height=40,
        )

        self._draw_texts(painter)

        self._draw_pixmap_fit(
            painter=painter,
            path=self.brand_path,
            x=self.width() - 94,
            y=self.height() - 58,
            width=68,
            height=38,
        )

    def _draw_texts(self, painter: QPainter) -> None:
        painter.setPen(QColor("#FFFFFF"))

        name_font = QFont()
        name_font.setPointSize(13)
        name_font.setBold(True)

        small_font = QFont()
        small_font.setPointSize(9)

        digits_font = QFont()
        digits_font.setPointSize(13)
        digits_font.setBold(True)

        painter.setFont(name_font)
        painter.drawText(
            QRectF(24, self.height() - 92, self.width() - 48, 24),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.name,
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(24, self.height() - 66, self.width() - 48, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.dates,
        )

        painter.setFont(digits_font)
        painter.drawText(
            QRectF(24, self.height() - 38, self.width() - 128, 24),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"•••• {self.digits}",
        )

    def _draw_pixmap_fit(
            self,
            painter: QPainter,
            path,
            x: int,
            y: int,
            width: int,
            height: int,
    ) -> None:
        if path is None:
            return

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            return

        scaled = pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        draw_x = x + (width - scaled.width()) / 2
        draw_y = y + (height - scaled.height()) / 2

        painter.drawPixmap(int(draw_x), int(draw_y), scaled)

    def _draw_pixmap_cover(
            self,
            painter: QPainter,
            path,
            rect: QRectF,
    ) -> None:
        if path is None:
            return

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            return

        scaled = pixmap.scaled(
            rect.size().toSize(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )

        x = int((self.width() - scaled.width()) / 2)
        y = int((self.height() - scaled.height()) / 2)

        painter.drawPixmap(x, y, scaled)


class CreditCardSetupDialog(QDialog):
    def __init__(
            self,
            assets: list[dict],
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.assets = assets
        self.asset_resolver = CreditCardAssetResolver()

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

        self.preview_card = CreditCardPreviewWidget()

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
            "id": None,
            "bank_name": None,
            "asset_name": None,
            "preset_key": "generic_black",
        }

    def _atualizar_preview(self) -> None:
        asset = self._get_selected_asset()

        name = self.name_input.text().strip() or "Meu Cartão"
        digits = self.last_digits_input.text().strip() or "0000"

        dates = (
            f"Fecha dia {self.closing_day_input.value():02d} • "
            f"Vence dia {self.due_day_input.value():02d}"
        )

        try:
            preset_key = asset.get("preset_key", "generic_black")

            resolved_assets = self.asset_resolver.resolver_preset(
                preset_key
            )

            self.preview_card.set_card_data(
                background_color=resolved_assets.background_color,
                name=name,
                digits=digits,
                dates=dates,
                background_path=resolved_assets.background_path,
                overlay_path=resolved_assets.overlay_path,
                issuer_path=resolved_assets.issuer_path,
                brand_path=resolved_assets.brand_path,
                chip_path=resolved_assets.chip_path,
            )

        except Exception as erro:
            print(f"[CreditCardSetupDialog] Erro ao resolver preset: {erro}")
            self.preview_card.set_card_data(
                background_color=asset.get("background_value", "#2563EB"),
                name=name,
                digits=digits,
                dates=dates,
            )

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
            "preset_key": asset.get("preset_key", "generic_black"),

            "limit_amount_cents": self._parse_money_to_cents(
                self.limit_input.text()
            ),
            "closing_day": self.closing_day_input.value(),
            "due_day": self.due_day_input.value(),
            "last_four_digits": self.last_digits_input.text().strip() or None,
        }