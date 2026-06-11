from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.balance_service import BalanceService
from modules.finance.services.balance_account_service import BalanceAccountService


class BalanceTimelinePage(QWidget):
    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.balance_service = BalanceService(username)
        self.account_service = BalanceAccountService(username)

        self.cycles = []
        self.accounts = []
        self.selected_cycle_id = None

        self._montar_interface()
        self._carregar_dados_base()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Timeline Financeira")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        self.cycle_combo = QComboBox()
        self.cycle_combo.setFixedWidth(280)
        self.cycle_combo.currentIndexChanged.connect(
            self._alterar_ciclo
        )

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(QLabel("Ciclo"))
        header.addWidget(self.cycle_combo)

        layout.addLayout(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)

        layout.addWidget(self.scroll_area, 1)

    def _carregar_dados_base(self) -> None:
        self.accounts = self.account_service.listar_contas()
        self.cycles = self.balance_service.listar_ciclos()

        self.cycle_combo.blockSignals(True)
        self.cycle_combo.clear()

        if not self.cycles:
            self.cycle_combo.addItem("Nenhum ciclo encontrado", None)
            self.selected_cycle_id = None
            self.cycle_combo.blockSignals(False)
            self._carregar_timeline()
            return

        for ciclo in self.cycles:
            texto = (
                f"{self._formatar_data(ciclo['start_date'])}"
                f" → "
                f"{self._formatar_data(ciclo['end_date'])}"
            )

            self.cycle_combo.addItem(
                texto,
                ciclo["id"],
            )

        self.selected_cycle_id = self.cycle_combo.currentData()
        self.cycle_combo.blockSignals(False)

        self._carregar_timeline()

    def _alterar_ciclo(self) -> None:
        self.selected_cycle_id = self.cycle_combo.currentData()
        self._carregar_timeline()

    def _carregar_timeline(self) -> None:
        self._limpar_cards()

        if self.selected_cycle_id is None:
            return

        receitas = self.balance_service.listar_receitas_ciclo(
            self.selected_cycle_id
        )

        compromissos = self.balance_service.listar_compromissos_ciclo(
            self.selected_cycle_id
        )

        eventos = []

        for receita in receitas:
            eventos.append(
                {
                    "kind": "income",
                    "date": receita["received_date"] or receita["expected_date"],
                    "description": receita["description"],
                    "amount_cents": (
                        receita["actual_amount_cents"]
                        if receita["status"] == "received"
                        and receita["actual_amount_cents"] is not None
                        else receita["expected_amount_cents"]
                    ),
                    "status": receita["status"],
                    "account_id": receita["account_id"],
                    "projection_type": "real",
                }
            )

        for compromisso in compromissos:
            eventos.append(
                {
                    "kind": "commitment",
                    "date": compromisso["paid_date"] or compromisso["due_date"],
                    "description": compromisso["description"],
                    "amount_cents": (
                        compromisso["actual_amount_cents"]
                        if compromisso["status"] == "paid"
                        and compromisso["actual_amount_cents"] is not None
                        else compromisso["expected_amount_cents"]
                    ),
                    "status": compromisso["status"],
                    "account_id": compromisso["account_id"],
                    "payment_type": compromisso["payment_type"],
                    "projection_type": compromisso.get("projection_type", "real"),
                }
            )

        eventos.sort(
            key=lambda evento: (
                evento["date"],
                0 if evento["kind"] == "income" else 1,
                evento["description"].lower(),
            )
        )

        resumo = self.balance_service.obter_resumo_ciclo(
            self.selected_cycle_id
        )

        saldo_acumulado = resumo["saldo_inicio_ciclo_cents"]

        for evento in eventos:
            if evento["kind"] == "income":
                saldo_acumulado += evento["amount_cents"]
            else:
                saldo_acumulado -= evento["amount_cents"]

            evento["balance_after_cents"] = saldo_acumulado

        for evento in eventos:
            card = self._criar_card_evento(evento)

            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1,
                card,
            )

    def _criar_card_evento(
            self,
            evento: dict,
    ) -> QFrame:
        is_income = evento["kind"] == "income"
        is_done = evento["status"] in ["received", "paid"]
        is_projected = evento.get("projection_type") == "projected"

        if is_income and is_done:
            cor_fundo = "#dcfce7"
            cor_borda = "#86efac"
            cor_titulo = "#15803d"
            tipo_texto = "Entrada recebida"
        elif is_income:
            cor_fundo = "#f0fdf4"
            cor_borda = "#bbf7d0"
            cor_titulo = "#16a34a"
            tipo_texto = "Entrada prevista"
        elif is_projected:
            cor_fundo = "#fff7ed"
            cor_borda = "#fed7aa"
            cor_titulo = "#c2410c"
            tipo_texto = "Saída projetada"
        elif is_done:
            cor_fundo = "#ffe4e6"
            cor_borda = "#fda4af"
            cor_titulo = "#be123c"
            tipo_texto = "Saída paga"
        else:
            cor_fundo = "#fff1f2"
            cor_borda = "#fecdd3"
            cor_titulo = "#e11d48"
            tipo_texto = "Saída prevista"

        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {cor_fundo};
                border: 1px solid {cor_borda};
                border-radius: 16px;
            }}
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        data_label = QLabel(self._formatar_data_curta(evento["date"]))
        data_label.setFixedWidth(76)
        data_label.setAlignment(Qt.AlignCenter)
        data_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: white;
                color: {cor_titulo};
                border: 1px solid {cor_borda};
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }}
            """
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        titulo = QLabel(evento["description"])
        titulo.setStyleSheet(
            f"""
            QLabel {{
                border: none;
                color: {cor_titulo};
                font-size: 15px;
                font-weight: bold;
            }}
            """
        )

        subtitulo = QLabel(
            f"{tipo_texto} • {self._formatar_moeda(evento['amount_cents'])}"
        )
        subtitulo.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #64748b;
                font-size: 12px;
            }
            """
        )

        conta = self._obter_nome_conta(
            evento["account_id"]
        )

        saldo_apos = self._formatar_moeda(
            evento.get("balance_after_cents", 0)
        )

        detalhe = QLabel(
            f"Conta: {conta} • Saldo após evento: {saldo_apos}"
        )

        detalhe.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #94a3b8;
                font-size: 11px;
            }
            """
        )

        info_layout.addWidget(titulo)
        info_layout.addWidget(subtitulo)
        info_layout.addWidget(detalhe)

        layout.addWidget(data_label)
        layout.addLayout(info_layout, 1)

        return card

    def _limpar_cards(self) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _obter_nome_conta(
            self,
            account_id: int | None,
    ) -> str:
        if account_id is None:
            return "Nenhuma"

        for account in self.accounts:
            if account["id"] == account_id:
                return account["name"]

        return "Conta não encontrada"

    def _formatar_moeda(
            self,
            valor_cents: int,
    ) -> str:
        valor = valor_cents / 100
        texto = f"{valor:,.2f}"

        return (
            "R$ "
            + texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:
        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"

    def _formatar_data_curta(
            self,
            data_iso: str,
    ) -> str:
        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}"