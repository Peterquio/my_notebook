from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
)


class CreditCardPreviousPaymentDialog(QDialog):
    def __init__(
            self,
            adjustments: list,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.adjustments = adjustments
        self.checkboxes = []

        self.setWindowTitle("Pagamentos da fatura anterior")
        self.setMinimumWidth(520)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        titulo = QLabel("Selecione os pagamentos que pertencem à fatura anterior:")
        titulo.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        descricao = QLabel(
            "Esses pagamentos serão ignorados no cálculo do valor a pagar desta fatura."
        )
        descricao.setWordWrap(True)
        descricao.setStyleSheet("color: #64748b; font-size: 12px;")

        layout.addWidget(titulo)
        layout.addWidget(descricao)

        for adjustment in self.adjustments:
            checkbox = QCheckBox(
                f"{adjustment.adjustment_date.strftime('%d/%m/%Y')}  |  "
                f"R$ {abs(adjustment.amount_cents) / 100:.2f}  |  "
                f"{adjustment.description}"
            )

            checkbox.setLayoutDirection(Qt.LeftToRight)

            self.checkboxes.append(
                {
                    "checkbox": checkbox,
                    "adjustment": adjustment,
                }
            )

            layout.addWidget(checkbox)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        confirmar = QPushButton("Confirmar")

        cancelar.clicked.connect(self.reject)
        confirmar.clicked.connect(self.accept)

        botoes.addWidget(cancelar)
        botoes.addWidget(confirmar)

        layout.addLayout(botoes)

    def obter_pagamentos_fatura_anterior(self) -> set[tuple]:
        selecionados = set()

        for item in self.checkboxes:
            if not item["checkbox"].isChecked():
                continue

            adjustment = item["adjustment"]

            selecionados.add(
                (
                    adjustment.adjustment_date.isoformat(),
                    adjustment.description,
                    adjustment.amount_cents,
                    adjustment.raw_title,
                )
            )

        return selecionados