from datetime import date
from dateutil.relativedelta import relativedelta
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.balance_service import BalanceService
from modules.finance.services.balance_account_service import BalanceAccountService

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)

class BalanceTimelinePage(QWidget):
    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.balance_service = BalanceService(username)
        self.account_service = BalanceAccountService(username)
        self.settings_repository = (
            FinanceSettingsRepository(username)
        )

        self.cycles = []
        self.accounts = []
        self.selected_cycle_id = None

        self.start_date_iso = None
        self.end_date_iso = None

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

        header.addWidget(titulo)
        header.addStretch()

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

        inicio, fim = self._obter_periodo_padrao()

        self.start_date_iso = inicio
        self.end_date_iso = fim

        self._carregar_timeline()

    def _carregar_timeline(self) -> None:
        self._limpar_cards()

        start_date = self.start_date_iso
        end_date = self.end_date_iso

        if start_date is None or end_date is None:
            return

        eventos = self.balance_service.listar_eventos_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        resumo = self.balance_service.obter_resumo_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        saldo_acumulado = resumo["saldo_inicial_periodo_cents"]

        barra_periodo = self._criar_barra_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            barra_periodo,
        )

        card_inicial = self._criar_card_saldo_periodo(
            titulo="Saldo inicial do período",
            data=start_date,
            valor_cents=saldo_acumulado,
            tipo="inicio",
        )

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            card_inicial,
        )

        for evento in eventos:
            if evento["kind"] == "income":
                saldo_acumulado += evento["amount_cents"]
            else:
                saldo_acumulado -= evento["amount_cents"]

            evento["balance_after_cents"] = saldo_acumulado

            card = self._criar_card_evento(evento)

            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1,
                card,
            )

        card_final = self._criar_card_saldo_periodo(
            titulo="Saldo final estimado",
            data=end_date,
            valor_cents=resumo["saldo_final_estimado_cents"],
            tipo="fim",
        )

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            card_final,
        )

    def _criar_card_saldo_periodo(
            self,
            titulo: str,
            data: str,
            valor_cents: int,
            tipo: str,
    ) -> QFrame:
        if valor_cents > 0:
            cor_fundo = "#ecfdf5"
            cor_borda = "#86efac"
            cor_titulo = "#15803d"
            simbolo = "●"
        elif valor_cents < 0:
            cor_fundo = "#fff1f2"
            cor_borda = "#fda4af"
            cor_titulo = "#be123c"
            simbolo = "●"
        else:
            cor_fundo = "#eff6ff"
            cor_borda = "#93c5fd"
            cor_titulo = "#1d4ed8"
            simbolo = "●"

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

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        titulo_label = QLabel(f"{simbolo}  {titulo}")
        titulo_label.setStyleSheet(
            f"""
            QLabel {{
                border: none;
                color: {cor_titulo};
                font-size: 16px;
                letter-spacing: 0.5px;
                font-weight: bold;
            }}
            """
        )

        data_label = QLabel(self._formatar_data(data))
        data_label.setStyleSheet(
            """
            QLabel {
                border: none;
                color: #64748b;
                font-size: 12px;
            }
            """
        )

        valor_label = QLabel(self._formatar_moeda(valor_cents))
        valor_label.setStyleSheet(
            f"""
            QLabel {{
                border: none;
                color: {cor_titulo};
                font-size: 22px;
                font-weight: bold;
            }}
            """
        )

        layout.addWidget(titulo_label)
        layout.addWidget(data_label)
        layout.addWidget(valor_label)

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

        inicio.setCursor(Qt.PointingHandCursor)
        inicio.mousePressEvent = lambda event: self._abrir_calendario_periodo(
            campo="inicio"
        )

        fim = QLabel(
            f"Fim\n{self._formatar_data(end_date)}"
        )
        fim.setAlignment(Qt.AlignRight)
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

        fim.setCursor(Qt.PointingHandCursor)
        fim.mousePressEvent = lambda event: self._abrir_calendario_periodo(
            campo="fim"
        )

        datas_layout.addWidget(inicio)
        datas_layout.addStretch()
        datas_layout.addWidget(fim)

        layout.addWidget(barra)
        layout.addLayout(datas_layout)

        return card

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


    def _obter_periodo_padrao(self) -> tuple[str, str]:

        reference_day = (
            self.settings_repository.obter_reference_day()
        )

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

        self._carregar_timeline()