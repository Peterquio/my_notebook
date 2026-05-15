from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class CreditCardWidget(QFrame):
    def __init__(
            self,
            card_data: dict,
    ) -> None:
        super().__init__()

        self.card_data = card_data

        self.setObjectName("CreditCardWidget")

        self._criar_layout()

    def _criar_layout(self) -> None:
        config = self.card_data.get("config", {})

        background = config.get(
            "background_value",
            "#2563EB",
        )

        text_color = config.get(
            "text_color",
            "#FFFFFF",
        )

        self.setStyleSheet(f"""
            QFrame#CreditCardWidget {{
                background-color: {background};
                border-radius: 22px;
            }}

            QLabel {{
                color: {text_color};
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        name = QLabel(
            config.get("name", "Meu Cartão")
        )

        name.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
        """)

        invoice = QLabel(
            "Fatura atual: R$ 0,00"
        )

        invoice.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
        """)

        dates = QLabel(
            (
                f'Fecha dia '
                f'{config.get("closing_day", 5):02d} • '
                f'Vence dia '
                f'{config.get("due_day", 15):02d}'
            )
        )

        digits = QLabel(
            f'•••• {config.get("last_four_digits", "0000")}'
        )

        digits.setAlignment(Qt.AlignRight)

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(invoice)
        layout.addWidget(dates)
        layout.addWidget(digits)

    def set_hovered(
            self,
            hovered: bool,
    ) -> None:
        pass

    def set_pressed(
            self,
            pressed: bool,
    ) -> None:
        pass

    def set_dragging(
            self,
            dragging: bool,
    ) -> None:
        pass