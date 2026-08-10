from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

from ui.widgets.card_shadow_frame import CardShadowFrame
from modules.finance.services.credit_card_asset_resolver import CreditCardAssetResolver


class CreditCardWidget(CardShadowFrame):
    def __init__(
            self,
            card_data: dict,
    ) -> None:
        super().__init__()

        self.card_data = card_data
        self.asset_resolver = CreditCardAssetResolver()

        self.setObjectName("CreditCardWidget")
        self.setMinimumSize(260, 164)

        self._resolver_visual()

    def _resolver_visual(self) -> None:
        config = self.card_data.get("config", {})

        preset_key = config.get(
            "preset_key",
            "generic_black",
        )

        self.resolved_assets = self.asset_resolver.resolver_preset(
            preset_key
        )

        self.name = config.get("name", "Meu Cartão")
        self.last_four_digits = config.get("last_four_digits") or "0000"
        self.closing_day = config.get("closing_day", 5)
        self.due_day = config.get("due_day", 15)

        current_invoice_amount_cents = config.get(
            "current_invoice_amount_cents",
            0,
        )

        self.current_invoice_amount = current_invoice_amount_cents / 100

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)

        painter.setBrush(QColor(self.resolved_assets.background_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 22, 22)

        self._draw_pixmap_cover(
            painter=painter,
            path=self.resolved_assets.background_path,
            rect=rect,
        )

        self._draw_pixmap_cover(
            painter=painter,
            path=self.resolved_assets.overlay_path,
            rect=rect,
        )

        self._draw_pixmap_fit_by_height(
            painter=painter,
            path=self.resolved_assets.issuer_path,
            x=18,
            y=16,
            height=24,
        )

        self._draw_pixmap_fit(
            painter=painter,
            path=self.resolved_assets.chip_path,
            x=20,
            y=58,
            width=42,
            height=30,
        )

        self._draw_texts(painter)

        self._draw_pixmap_fit(
            painter=painter,
            path=self.resolved_assets.brand_path,
            x=self.width() - 81,
            y=self.height() - 66,
            width=70,
            height=40,
        )

    def _draw_texts(self, painter: QPainter) -> None:
        text_color = QColor(self.resolved_assets.text_color)
        painter.setPen(text_color)

        name_font = QFont()
        name_font.setPointSize(10)
        name_font.setBold(True)

        invoice_font = QFont()
        invoice_font.setPointSize(13)
        invoice_font.setBold(True)

        small_font = QFont()
        small_font.setPointSize(8)

        digits_font = QFont()
        digits_font.setPointSize(10)
        digits_font.setBold(True)

        invoice_text = (
            f"R$ {self.current_invoice_amount:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        painter.setFont(name_font)
        painter.drawText(
            QRectF(18, self.height() - 74, self.width() - 36, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.name,
        )

        painter.setFont(invoice_font)
        painter.drawText(
            QRectF(18, self.height() - 56, self.width() - 36, 26),
            Qt.AlignLeft | Qt.AlignVCenter,
            invoice_text,
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(18, self.height() - 30, self.width() - 88, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"Fecha {self.closing_day:02d} • Vence {self.due_day:02d}",
        )

        painter.setFont(digits_font)
        painter.drawText(
            QRectF(self.width() - 84, self.height() - 30, 52, 18),
            Qt.AlignRight | Qt.AlignVCenter,
            self.last_four_digits,
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

        painter.drawPixmap(
            int(draw_x),
            int(draw_y),
            scaled,
        )

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

        painter.drawPixmap(
            x,
            y,
            scaled,
        )

    def _draw_pixmap_fit_by_height(
            self,
            painter: QPainter,
            path,
            x: int,
            y: int,
            height: int,
    ) -> None:
        if path is None:
            return

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            return

        scaled = pixmap.scaledToHeight(
            height,
            Qt.SmoothTransformation,
        )

        painter.drawPixmap(
            x,
            y,
            scaled,
        )