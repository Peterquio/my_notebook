from PySide6.QtWidgets import (
    QComboBox, QGridLayout, QHBoxLayout, QLabel,
    QFrame, QVBoxLayout, QWidget
)

from modules.finance.services.balance_service import BalanceService


class BalanceDashboardPage(QWidget):
    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.balance_service = BalanceService(self.username)

        self.cycles = []
        self.selected_cycle_id = None

        self._montar_interface()
        self._carregar_ciclos()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Dashboard do Saldo")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.cycle_combo = QComboBox()
        self.cycle_combo.setFixedWidth(260)
        self.cycle_combo.currentIndexChanged.connect(self._alterar_ciclo)

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Ciclo"))
        header.addWidget(self.cycle_combo)

        layout.addLayout(header)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(12)

        layout.addLayout(self.cards_layout)
        layout.addStretch()

    def _carregar_ciclos(self) -> None:
        self.cycles = self.balance_service.listar_ciclos()

        self.cycle_combo.blockSignals(True)
        self.cycle_combo.clear()

        for ciclo in self.cycles:
            texto = (
                f"{self._formatar_data(ciclo['start_date'])}"
                f" → "
                f"{self._formatar_data(ciclo['end_date'])}"
            )
            self.cycle_combo.addItem(texto, ciclo["id"])

        self.selected_cycle_id = self.cycle_combo.currentData()
        self.cycle_combo.blockSignals(False)

        self._carregar_resumo()

    def _alterar_ciclo(self) -> None:
        self.selected_cycle_id = self.cycle_combo.currentData()
        self._carregar_resumo()

    def _carregar_resumo(self) -> None:
        self._limpar_cards()

        if self.selected_cycle_id is None:
            return

        resumo = self.balance_service.obter_resumo_ciclo(
            self.selected_cycle_id
        )

        cards = [
            (
                "Saldo Atual",
                self._formatar_moeda(resumo["saldo_atual_cents"]),
                "Dinheiro real disponível",
            ),
            (
                "Saldo Previsto",
                self._formatar_moeda(resumo["saldo_previsto_cents"]),
                "Saldo atual + previstos",
            ),
            (
                "Receitas Recebidas",
                self._formatar_moeda(resumo["receitas_recebidas_cents"]),
                "Já confirmadas",
            ),
            (
                "Receitas Previstas",
                self._formatar_moeda(resumo["receitas_previstas_cents"]),
                "Ainda não recebidas",
            ),
            (
                "Compromissos Pagos",
                self._formatar_moeda(resumo["compromissos_pagos_cents"]),
                "Já pagos",
            ),
            (
                "Compromissos Previstos",
                self._formatar_moeda(resumo["compromissos_previstos_cents"]),
                "Ainda não pagos",
            ),
        ]

        for index, (titulo, valor, subtitulo) in enumerate(cards):
            self.cards_layout.addWidget(
                self._criar_card(titulo, valor, subtitulo),
                index // 3,
                index % 3,
            )

    def _criar_card(
            self,
            titulo: str,
            valor: str,
            subtitulo: str,
    ) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(110)
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(
            "border: none; font-size: 12px; color: #64748b;"
        )

        valor_label = QLabel(valor)
        valor_label.setStyleSheet(
            """
            border: none;
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setStyleSheet(
            "border: none; font-size: 11px; color: #94a3b8;"
        )

        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)
        layout.addWidget(subtitulo_label)
        layout.addStretch()

        return card

    def _limpar_cards(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _formatar_moeda(self, valor_cents: int) -> str:
        valor = valor_cents / 100
        texto = f"{valor:,.2f}"

        return (
            "R$ "
            + texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data(self, data_iso: str) -> str:
        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"