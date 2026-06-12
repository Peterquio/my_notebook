from datetime import date

from dateutil.relativedelta import relativedelta

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.balance_service import BalanceService

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)


class BalanceDashboardPage(QWidget):
    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.balance_service = BalanceService(self.username)
        self.settings_repository = FinanceSettingsRepository(self.username)

        self.start_date_iso = None
        self.end_date_iso = None

        self._montar_interface()
        self._carregar_periodo_padrao()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Dashboard do Saldo")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        header.addWidget(titulo)
        header.addStretch()

        layout.addLayout(header)

        self.periodo_container = QVBoxLayout()
        self.periodo_container.setSpacing(8)

        layout.addLayout(self.periodo_container)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(12)

        layout.addLayout(self.cards_layout)
        layout.addStretch()

    def _carregar_periodo_padrao(self) -> None:
        inicio, fim = self._obter_periodo_padrao()

        self.start_date_iso = inicio
        self.end_date_iso = fim

        self._carregar_resumo()

    def _carregar_resumo(self) -> None:
        self._limpar_periodo()
        self._limpar_cards()

        if self.start_date_iso is None or self.end_date_iso is None:
            return

        barra_periodo = self._criar_barra_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
        )

        self.periodo_container.addWidget(barra_periodo)

        resumo = self.balance_service.obter_resumo_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
        )

        receitas_total = (
            resumo["receitas_recebidas_cents"]
            + resumo["receitas_previstas_cents"]
        )

        compromissos_total = (
            resumo["compromissos_pagos_cents"]
            + resumo["compromissos_previstos_cents"]
        )

        cards = [
            (
                "Saldo Inicial",
                resumo["saldo_inicial_periodo_cents"],
                "Saldo no começo do período",
            ),
            (
                "Saldo Final Estimado",
                resumo["saldo_final_estimado_cents"],
                "Saldo após reais e previstos",
            ),
            (
                "Movimentação Real",
                resumo["saldo_movimentado_real_cents"],
                "Recebidos menos pagos",
            ),
            (
                "Movimentação Prevista",
                resumo["saldo_movimentado_previsto_cents"],
                "Previstos menos pendentes",
            ),
            (
                "Receitas do Período",
                receitas_total,
                "Recebidas + previstas",
            ),
            (
                "Saídas do Período",
                compromissos_total,
                "Pagas + previstas",
            ),
        ]

        for index, (titulo, valor_cents, subtitulo) in enumerate(cards):
            self.cards_layout.addWidget(
                self._criar_card(
                    titulo=titulo,
                    valor_cents=valor_cents,
                    subtitulo=subtitulo,
                ),
                index // 3,
                index % 3,
            )

    def _criar_card(
            self,
            titulo: str,
            valor_cents: int,
            subtitulo: str,
    ) -> QFrame:
        cor_valor = self._obter_cor_valor(valor_cents)

        card = QFrame()
        card.setMinimumHeight(116)
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
            """
            QLabel {
                border: none;
                font-size: 12px;
                color: #64748b;
            }
            """
        )

        valor_label = QLabel(
            self._formatar_moeda(valor_cents)
        )
        valor_label.setStyleSheet(
            f"""
            QLabel {{
                border: none;
                font-size: 24px;
                font-weight: bold;
                color: {cor_valor};
            }}
            """
        )

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setStyleSheet(
            """
            QLabel {
                border: none;
                font-size: 11px;
                color: #94a3b8;
            }
            """
        )

        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)
        layout.addWidget(subtitulo_label)
        layout.addStretch()

        return card

    def _criar_barra_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> QFrame:
        card = QFrame()
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
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        barra = QFrame()
        barra.setFixedHeight(8)
        barra.setStyleSheet(
            """
            QFrame {
                border: none;
                border-radius: 4px;
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 1, y2: 0,
                    stop: 0 #22c55e,
                    stop: 1 #ef4444
                );
            }
            """
        )

        datas_layout = QHBoxLayout()
        datas_layout.setContentsMargins(0, 0, 0, 0)

        inicio = QLabel(
            f"Início\n{self._formatar_data(start_date)}"
        )
        inicio.setCursor(Qt.PointingHandCursor)
        inicio.mousePressEvent = lambda event: self._abrir_calendario_periodo(
            campo="inicio"
        )
        inicio.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #15803d;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        fim = QLabel(
            f"Fim\n{self._formatar_data(end_date)}"
        )
        fim.setAlignment(Qt.AlignRight)
        fim.setCursor(Qt.PointingHandCursor)
        fim.mousePressEvent = lambda event: self._abrir_calendario_periodo(
            campo="fim"
        )
        fim.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #be123c;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )

        datas_layout.addWidget(inicio)
        datas_layout.addStretch()
        datas_layout.addWidget(fim)

        layout.addWidget(barra)
        layout.addLayout(datas_layout)

        return card

    def _abrir_calendario_periodo(
            self,
            campo: str,
    ) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Selecionar data inicial"
            if campo == "inicio"
            else "Selecionar data final"
        )
        dialog.setModal(True)
        dialog.setMinimumWidth(320)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        calendario = QCalendarWidget()
        calendario.setGridVisible(True)

        data_atual = (
            self.start_date_iso
            if campo == "inicio"
            else self.end_date_iso
        )

        if data_atual is not None:
            calendario.setSelectedDate(
                QDate.fromString(
                    data_atual,
                    "yyyy-MM-dd",
                )
            )

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(dialog.reject)

        aplicar = QPushButton("Aplicar")
        aplicar.clicked.connect(dialog.accept)

        botoes.addWidget(cancelar)
        botoes.addWidget(aplicar)

        layout.addWidget(calendario)
        layout.addLayout(botoes)

        if dialog.exec() != QDialog.Accepted:
            return

        nova_data = calendario.selectedDate().toPython().isoformat()

        if campo == "inicio":
            self.start_date_iso = nova_data
        else:
            self.end_date_iso = nova_data

        self._carregar_resumo()

    def _limpar_periodo(self) -> None:
        while self.periodo_container.count():
            item = self.periodo_container.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _limpar_cards(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _obter_periodo_padrao(self) -> tuple[str, str]:
        reference_day = self.settings_repository.obter_reference_day()

        hoje = date.today()

        if hoje.day >= reference_day:
            inicio = hoje.replace(
                day=reference_day
            )
        else:
            inicio = (
                hoje.replace(day=1)
                + relativedelta(months=-1)
            )

            ultimo_dia = (
                inicio
                + relativedelta(day=31)
            ).day

            inicio = inicio.replace(
                day=min(
                    reference_day,
                    ultimo_dia,
                )
            )

        fim = (
            inicio
            + relativedelta(months=1)
            + relativedelta(days=-1)
        )

        return (
            inicio.isoformat(),
            fim.isoformat(),
        )

    def _obter_cor_valor(
            self,
            valor_cents: int,
    ) -> str:
        if valor_cents > 0:
            return "#15803d"

        if valor_cents < 0:
            return "#be123c"

        return "#1d4ed8"

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