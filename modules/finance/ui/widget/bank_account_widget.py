from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QFrame

from modules.finance.services.bank_account_asset_resolver import (
    BankAccountAssetResolver,
)


class BankAccountWidget(QFrame):
    ACCOUNT_KIND_LABELS = {
        "checking": "Conta corrente",
        "savings": "Conta poupança",
        "payment": "Conta pagamento",
        "other": "Conta bancária",
    }

    def __init__(self, card_data: dict, parent=None) -> None:
        super().__init__(parent)

        self.card_data = card_data
        self.asset_resolver = BankAccountAssetResolver()

        self.setObjectName("BankAccountWidget")
        self.setMinimumSize(280, 164)

        self._resolver_visual()

    def _resolver_visual(self) -> None:
        config = self.card_data.get("config", {})

        self.name = config.get("name") or "Conta Bancária"
        self.institution_name = config.get("institution_name") or "Banco"
        self.bank_preset_key = config.get("bank_preset_key") or "generic_bank"
        self.account_kind = config.get("account_kind") or "other"
        self.agency = config.get("agency")
        self.account_number = config.get("account_number")

        self.current_balance = config.get("current_balance_cents", 0) / 100
        self.projected_balance = config.get("projected_balance_cents", 0) / 100
        self.projected_date = config.get("projected_date") or ""

        self.pix_scheduled_count = config.get("pix_scheduled_count", 0)

        resolved_assets = self.asset_resolver.resolver_preset(
            self.bank_preset_key
        )

        self.background_color = resolved_assets.background_color
        self.text_color = resolved_assets.text_color
        self.logo_path = resolved_assets.logo_path
        self.background_path = resolved_assets.background_path
        self.overlay_path = resolved_assets.overlay_path

    def update_card_data(self, card_data: dict) -> None:
        self.card_data = card_data
        self._resolver_visual()
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)

        painter.setBrush(QColor(self.background_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 22, 22)

        self._draw_pixmap_cover(painter, self.background_path, rect)

        if self.background_path is None:
            self._draw_default_decoration(painter)

        self._draw_pixmap_cover(painter, self.overlay_path, rect)

        self._draw_logo_or_icon(painter)
        self._draw_texts(painter)

    def _draw_default_decoration(self, painter: QPainter) -> None:
        painter.setBrush(QColor(255, 255, 255, 28))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            QRectF(self.width() - 92, -36, 140, 140)
        )

        painter.setBrush(QColor(255, 255, 255, 18))
        painter.drawEllipse(
            QRectF(self.width() - 144, self.height() - 46, 170, 170)
        )

    def _draw_logo_or_icon(self, painter: QPainter) -> None:
        if self.logo_path is not None:
            self._draw_pixmap_fit_by_height(
                painter=painter,
                path=self.logo_path,
                x=18,
                y=14,
                height=24,
            )
            return

        painter.setPen(QColor(self.text_color))

        icon_font = QFont()
        icon_font.setPointSize(14)
        icon_font.setBold(True)

        painter.setFont(icon_font)
        painter.drawText(
            QRectF(self.width() - 54, 14, 36, 22),
            Qt.AlignRight | Qt.AlignVCenter,
            "🏦",
        )

    def _draw_texts(self, painter: QPainter) -> None:
        painter.setPen(QColor(self.text_color))

        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)

        small_font = QFont()
        small_font.setPointSize(8)

        balance_font = QFont()
        balance_font.setPointSize(17)
        balance_font.setBold(True)

        footer_font = QFont()
        footer_font.setPointSize(8)

        title_x = 18
        title_width = self.width() - 72

        if self.logo_path is not None:
            title_x = 18
            title_y = 42
        else:
            title_y = 14

        painter.setFont(title_font)
        painter.drawText(
            QRectF(title_x, title_y, title_width, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.institution_name.upper(),
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(18, title_y + 22, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.ACCOUNT_KIND_LABELS.get(
                self.account_kind,
                "Conta bancária",
            ),
        )

        painter.setFont(balance_font)
        painter.drawText(
            QRectF(18, 76, self.width() - 36, 32),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._formatar_moeda(self.current_balance),
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(20, 106, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            "saldo atual",
        )

        footer = (
            f"Previsto {self._formatar_data(self.projected_date)} → "
            f"{self._formatar_moeda(self.projected_balance)}"
        )

        painter.setFont(footer_font)
        painter.drawText(
            QRectF(18, self.height() - 48, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            footer,
        )

        painter.drawText(
            QRectF(18, self.height() - 28, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._montar_detalhe_conta(),
        )

    def _montar_detalhe_conta(self) -> str:
        partes = []

        if self.agency:
            partes.append(f"Ag. {self.agency}")

        if self.account_number:
            partes.append(f"Conta {self.account_number}")

        if self.pix_scheduled_count:
            partes.append(f"Pix agendados: {self.pix_scheduled_count}")

        return " • ".join(partes) if partes else self.name

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

        ratio = pixmap.width() / pixmap.height()
        width = int(height * ratio)

        scaled = pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        painter.drawPixmap(x, y, scaled)

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

    def _formatar_moeda(self, valor: float) -> str:
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data(self, data_iso: str) -> str:
        if not data_iso:
            return "--/--"

        partes = data_iso.split("-")

        if len(partes) != 3:
            return data_iso

        return f"{partes[2]}/{partes[1]}"

    def set_hovered(self, hovered: bool) -> None:
        pass

    def set_pressed(self, pressed: bool) -> None:
        pass

    def set_dragging(self, dragging: bool) -> None:
        pass