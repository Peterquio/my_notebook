from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame


class BankAccountWidget(QFrame):
    PRESETS = {
        "nubank": ("#6d28d9", "#f5f3ff", "#ffffff"),
        "inter": ("#f97316", "#fff7ed", "#ffffff"),
        "itau": ("#ea580c", "#fff7ed", "#ffffff"),
        "bradesco": ("#be123c", "#fff1f2", "#ffffff"),
        "santander": ("#dc2626", "#fef2f2", "#ffffff"),
        "bb": ("#facc15", "#172554", "#111827"),
        "caixa": ("#2563eb", "#eff6ff", "#ffffff"),
        "btg": ("#0f172a", "#f8fafc", "#ffffff"),
        "xp": ("#111827", "#fef3c7", "#ffffff"),
        "picpay": ("#16a34a", "#f0fdf4", "#ffffff"),
        "mercado_pago": ("#38bdf8", "#ecfeff", "#082f49"),
        "pagbank": ("#facc15", "#fefce8", "#111827"),
        "other": ("#334155", "#f8fafc", "#ffffff"),
    }

    ACCOUNT_KIND_LABELS = {
        "checking": "Conta corrente",
        "savings": "Conta poupança",
        "payment": "Conta pagamento",
        "other": "Conta bancária",
    }

    def __init__(self, card_data: dict) -> None:
        super().__init__()

        self.card_data = card_data
        self.setObjectName("BankAccountWidget")
        self.setMinimumSize(280, 164)

        self._resolver_visual()

    def _resolver_visual(self) -> None:
        config = self.card_data.get("config", {})

        self.name = config.get("name") or "Conta Bancária"
        self.institution_name = config.get("institution_name") or "Banco"
        self.bank_preset_key = config.get("bank_preset_key") or "other"
        self.account_kind = config.get("account_kind") or "other"
        self.agency = config.get("agency")
        self.account_number = config.get("account_number")

        self.current_balance = config.get("current_balance_cents", 0) / 100
        self.projected_balance = config.get("projected_balance_cents", 0) / 100
        self.projected_date = config.get("projected_date") or ""

        self.pix_scheduled_count = config.get("pix_scheduled_count", 0)

        self.background_color, self.soft_color, self.text_color = self.PRESETS.get(
            self.bank_preset_key,
            self.PRESETS["other"],
        )

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0, 0, -1, -1)

        painter.setBrush(QColor(self.background_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 22, 22)

        painter.setBrush(QColor(255, 255, 255, 28))
        painter.drawEllipse(
            QRectF(self.width() - 92, -36, 140, 140)
        )

        painter.setBrush(QColor(255, 255, 255, 18))
        painter.drawEllipse(
            QRectF(self.width() - 144, self.height() - 46, 170, 170)
        )

        self._draw_texts(painter)

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

        painter.setFont(title_font)
        painter.drawText(
            QRectF(18, 14, self.width() - 72, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.institution_name.upper(),
        )

        painter.setFont(title_font)
        painter.drawText(
            QRectF(self.width() - 54, 14, 36, 22),
            Qt.AlignRight | Qt.AlignVCenter,
            "🏦",
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(18, 36, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            self.ACCOUNT_KIND_LABELS.get(self.account_kind, "Conta bancária"),
        )

        painter.setFont(balance_font)
        painter.drawText(
            QRectF(18, 68, self.width() - 36, 32),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._formatar_moeda(self.current_balance),
        )

        painter.setFont(small_font)
        painter.drawText(
            QRectF(20, 98, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            "saldo atual",
        )

        footer = f"Previsto {self._formatar_data(self.projected_date)} → {self._formatar_moeda(self.projected_balance)}"

        painter.setFont(footer_font)
        painter.drawText(
            QRectF(18, self.height() - 48, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            footer,
        )

        detalhe = self._montar_detalhe_conta()

        painter.drawText(
            QRectF(18, self.height() - 28, self.width() - 36, 18),
            Qt.AlignLeft | Qt.AlignVCenter,
            detalhe,
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

    def _formatar_moeda(self, valor: float) -> str:
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data(self, data_iso: str) -> str:
        if not data_iso:
            return ""

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