from datetime import datetime

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from ui.widgets.card_shadow_frame import CardShadowFrame



class PixWidget(CardShadowFrame):
    def __init__(
            self,
            card_data: dict,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.card_data = card_data
        self.config = card_data.get("config", {})

        self.setObjectName("PixWidget")

        self._montar_interface()
        self._aplicar_estilo()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )
        layout.setSpacing(8)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = QLabel("PIX")
        self.title_label.setObjectName("PixTitle")

        self.period_label = QLabel(
            self._formatar_periodo()
        )
        self.period_label.setObjectName("PixPeriod")

        header_layout.addWidget(
            self.title_label
        )

        header_layout.addWidget(
            self.period_label
        )

        header_layout.addStretch()

        layout.addLayout(
            header_layout
        )

        layout.addStretch()

        # -------------------------------------------------
        # VALORES
        # -------------------------------------------------

        values_layout = QHBoxLayout()
        values_layout.setContentsMargins(0, 0, 0, 0)
        values_layout.setSpacing(30)

        sent_container = self._criar_bloco_valor(
            titulo="Enviados",
            valor=self.config.get(
                "sent_cents",
                0,
            ),
            object_name="PixSentValue",
        )

        received_container = self._criar_bloco_valor(
            titulo="Recebidos",
            valor=self.config.get(
                "received_cents",
                0,
            ),
            object_name="PixReceivedValue",
        )

        values_layout.addWidget(
            sent_container,
            1,
        )

        values_layout.addWidget(
            received_container,
            1,
        )

        layout.addLayout(
            values_layout
        )

    def _criar_bloco_valor(
            self,
            titulo: str,
            valor: int,
            object_name: str,
    ) -> QFrame:

        container = QFrame()
        container.setObjectName(
            "PixValueContainer"
        )

        layout = QVBoxLayout(
            container
        )
        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        layout.setSpacing(2)

        title_label = QLabel(
            titulo
        )
        title_label.setObjectName(
            "PixValueTitle"
        )

        value_label = QLabel(
            self._formatar_valor(
                valor
            )
        )
        value_label.setObjectName(
            object_name
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        return container

    def _formatar_periodo(self) -> str:
        start_date = self.config.get(
            "start_date"
        )

        end_date = self.config.get(
            "end_date"
        )

        if not start_date or not end_date:
            return ""

        try:
            inicio = datetime.strptime(
                start_date,
                "%Y-%m-%d",
            )

            fim = datetime.strptime(
                end_date,
                "%Y-%m-%d",
            )

        except ValueError:
            return ""

        meses = {
            1: "janeiro",
            2: "fevereiro",
            3: "março",
            4: "abril",
            5: "maio",
            6: "junho",
            7: "julho",
            8: "agosto",
            9: "setembro",
            10: "outubro",
            11: "novembro",
            12: "dezembro",
        }

        return (
            f"{inicio.day:02d} de {meses[inicio.month]}"
            f" à "
            f"{fim.day:02d} de {meses[fim.month]}"
        )

    def _formatar_valor(
            self,
            valor_cents: int,
    ) -> str:

        valor = (
            int(valor_cents or 0)
            / 100
        )

        texto = f"{valor:,.2f}"

        texto = (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {texto}"

    def _aplicar_estilo(self) -> None:
        self.setStyleSheet(
            """
            QFrame#PixWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 16px;
            }

            QLabel {
                background: transparent;
                border: none;
            }

            QLabel#PixTitle {
                color: #0f172a;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#PixPeriod {
                color: #64748b;
                font-size: 12px;
                font-weight: 500;
            }

            QFrame#PixValueContainer {
                background: transparent;
                border: none;
            }

            QLabel#PixValueTitle {
                color: #64748b;
                font-size: 12px;
                font-weight: 500;
            }

            QLabel#PixSentValue {
                color: #dc2626;
                font-size: 19px;
                font-weight: 700;
            }

            QLabel#PixReceivedValue {
                color: #16a34a;
                font-size: 19px;
                font-weight: 700;
            }
            """
        )