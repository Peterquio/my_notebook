from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class CreditCardImportPreviewDialog(QDialog):
    def __init__(
            self,
            expenses: list,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.expenses = expenses
        self.confirmed = False

        self.setWindowTitle("Prévia da importação")
        self.resize(900, 560)
        self.setMinimumSize(760, 460)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(14)

        title = QLabel("Prévia da importação")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        subtitle = QLabel(
            f"{len(self.expenses)} compras importáveis encontradas. "
            "Confira antes de salvar no banco."
        )
        subtitle.setStyleSheet(
            "font-size: 13px; color: #64748b;"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            [
                "DATA",
                "DESCRIÇÃO",
                "PARCELA",
                "VALOR",
                "ORIGEM",
            ]
        )

        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setRowCount(len(self.expenses))

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)

        table.setColumnWidth(0, 100)
        table.setColumnWidth(2, 90)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 110)

        for row_index, expense in enumerate(self.expenses):
            self._adicionar_linha(
                table,
                row_index,
                expense,
            )

        layout.addWidget(table, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)

        confirm_button = QPushButton("Confirmar importação")
        confirm_button.clicked.connect(self._confirmar)
        confirm_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6d28d9;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: bold;
            }
            """
        )

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)

        layout.addLayout(buttons_layout)

    def _adicionar_linha(
            self,
            table: QTableWidget,
            row_index: int,
            expense,
    ) -> None:

        valores = [
            expense.purchase_date.strftime("%d/%m/%Y"),
            expense.description,
            f"{expense.installment_number}/{expense.installment_total}",
            self._formatar_moeda(expense.amount_cents),
            expense.source,
        ]

        for col, value in enumerate(valores):
            item = QTableWidgetItem(value)

            if col in [0, 2]:
                item.setTextAlignment(Qt.AlignCenter)
            elif col == 3:
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            table.setItem(row_index, col, item)

    def _formatar_moeda(
            self,
            amount_cents: int,
    ) -> str:

        valor = amount_cents / 100

        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _confirmar(self) -> None:
        self.confirmed = True
        self.accept()