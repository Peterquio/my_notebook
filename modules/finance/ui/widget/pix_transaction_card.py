from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from ui.widgets.card_shadow_frame import CardShadowFrame

class PixTransactionCard(CardShadowFrame):
    clicked = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(
            self,
            transaction_data: dict,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.transaction_data = transaction_data

        self.setFixedSize(
            170,
            150,
        )

        self.setCursor(
            Qt.PointingHandCursor
        )

        self._montar_interface()
        self._aplicar_estilo()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )
        layout.setSpacing(5)

        header = QHBoxLayout()

        date_label = QLabel(
            self._formatar_data()
        )

        date_label.setObjectName(
            "PixTransactionDate"
        )

        delete_button = QPushButton("×")
        delete_button.setObjectName(
            "PixTransactionDelete"
        )
        delete_button.setFixedSize(
            24,
            24,
        )
        delete_button.setCursor(
            Qt.PointingHandCursor
        )

        delete_button.clicked.connect(
            lambda: self.delete_requested.emit(
                self.transaction_data
            )
        )

        header.addWidget(
            date_label
        )
        header.addStretch()
        header.addWidget(
            delete_button
        )

        amount_label = QLabel(
            self._formatar_valor(
                self.transaction_data.get(
                    "amount_cents",
                    0,
                )
            )
        )

        amount_label.setObjectName(
            "PixTransactionAmount"
        )

        contact_name = (
            self.transaction_data.get(
                "contact_name"
            )
            or self.transaction_data.get(
                "description"
            )
            or "PIX"
        )

        contact_label = QLabel(
            contact_name
        )

        contact_label.setObjectName(
            "PixTransactionContact"
        )

        contact_label.setWordWrap(
            True
        )

        category_name = (
            self.transaction_data.get(
                "category_name"
            )
            or "Sem categoria"
        )

        category_label = QLabel(
            category_name
        )

        category_label.setObjectName(
            "PixTransactionCategory"
        )

        layout.addLayout(
            header
        )

        layout.addStretch()

        layout.addWidget(
            amount_label
        )

        layout.addWidget(
            contact_label
        )

        layout.addWidget(
            category_label
        )

    def _formatar_data(self) -> str:
        data_iso = (
            self.transaction_data.get(
                "transaction_date"
            )
        )

        if not data_iso:
            return ""

        try:
            data = datetime.strptime(
                data_iso,
                "%Y-%m-%d",
            )

            return data.strftime(
                "%d/%m"
            )

        except ValueError:
            return data_iso

    def _formatar_valor(
            self,
            amount_cents: int,
    ) -> str:
        valor = amount_cents / 100

        texto = f"{valor:,.2f}"

        texto = (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {texto}"

    def _aplicar_estilo(self) -> None:
        transaction_type = (
            self.transaction_data.get(
                "transaction_type"
            )
        )

        if transaction_type == "received":
            background = "#dcfce7"
            border = "#86efac"
            amount_color = "#166534"
        else:
            background = "#fee2e2"
            border = "#fca5a5"
            amount_color = "#991b1b"

        self.setStyleSheet(
            f"""
            PixTransactionCard {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: 14px;
            }}

            QLabel {{
                background: transparent;
                border: none;
            }}

            QLabel#PixTransactionDate {{
                color: #64748b;
                font-size: 11px;
                font-weight: 600;
            }}

            QLabel#PixTransactionAmount {{
                color: {amount_color};
                font-size: 18px;
                font-weight: 700;
            }}

            QLabel#PixTransactionContact {{
                color: #334155;
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel#PixTransactionCategory {{
                color: #64748b;
                font-size: 11px;
            }}

            QPushButton#PixTransactionDelete {{
                background: transparent;
                border: none;
                color: #64748b;
                font-size: 17px;
                font-weight: 700;
            }}

            QPushButton#PixTransactionDelete:hover {{
                background-color: rgba(15, 23, 42, 20);
                border-radius: 12px;
                color: #0f172a;
            }}
            """
        )

    def mousePressEvent(
            self,
            event,
    ) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(
                self.transaction_data
            )

        super().mousePressEvent(
            event
        )