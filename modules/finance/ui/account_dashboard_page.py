from datetime import date

from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QCalendarWidget,
    QDialog,
)

from modules.finance.services.balance_service import (
    BalanceService,
)

from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)

from dateutil.relativedelta import relativedelta

from modules.finance.ui.widget.balance_timeline_widget import (
    BalanceTimelineWidget,
)

class AccountDashboardPage(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(
            self,
            account: dict,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.account = account
        self.username = username

        self.balance_service = BalanceService(
            self.username
        )
        self.start_date_iso = self._obter_inicio_periodo()
        self.end_date_iso = self._obter_fim_periodo()

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        layout.addLayout(
            self._criar_header()
        )

        layout.addLayout(
            self._criar_cards_resumo()
        )

        self.timeline = BalanceTimelineWidget()

        self.timeline.on_period_start_clicked = (
            lambda: self._abrir_calendario_periodo("inicio")
        )

        self.timeline.on_period_end_clicked = (
            lambda: self._abrir_calendario_periodo("fim")
        )

        layout.addWidget(
            self.timeline,
            1,
        )

        self._carregar_timeline()

    def _criar_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        voltar = QPushButton("←")
        voltar.setFixedSize(38, 38)
        voltar.clicked.connect(
            self.back_requested.emit
        )

        titulo = QLabel(
            f"Conta {self.account.get('name') or 'bancária'}"
        )
        titulo.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        instituicao = QLabel(
            self.account.get("institution_name") or "Banco"
        )
        instituicao.setAlignment(Qt.AlignCenter)
        instituicao.setStyleSheet(
            """
            background-color: #e0f2fe;
            color: #0369a1;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            padding: 5px 10px;
            """
        )

        atualizado = QLabel(
            f"Período até {self._formatar_data(self._obter_fim_periodo())}"
        )
        atualizado.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addWidget(voltar)
        layout.addWidget(titulo)
        layout.addWidget(instituicao)
        layout.addStretch()
        layout.addWidget(atualizado)

        return layout

    def _criar_cards_resumo(self) -> QGridLayout:
        layout = QGridLayout()
        layout.setSpacing(10)

        hoje = date.today().isoformat()
        fim_periodo = self._obter_fim_periodo()

        saldo_atual = self.balance_service.calcular_saldo_conta_na_data(
            account_id=self.account["id"],
            data_iso=hoje,
        )

        saldo_previsto = self.balance_service.calcular_saldo_conta_na_data(
            account_id=self.account["id"],
            data_iso=fim_periodo,
        )

        cards = [
            {
                "icon": "💰",
                "title": "Saldo atual",
                "value": self._formatar_moeda(saldo_atual),
                "subtitle": f"Hoje, {self._formatar_data(hoje)}",
            },
            {
                "icon": "📅",
                "title": "Saldo previsto",
                "value": self._formatar_moeda(saldo_previsto),
                "subtitle": f"Até {self._formatar_data(fim_periodo)}",
            },
            {
                "icon": "⚡",
                "title": "Pix agendados",
                "value": "0",
                "subtitle": "Em breve",
            },
            {
                "icon": "📌",
                "title": "Snapshots",
                "value": "Em breve",
                "subtitle": "Reconciliação futura",
            },
        ]

        for index, card_data in enumerate(cards):
            layout.addWidget(
                self._criar_card_resumo(
                    icon=card_data["icon"],
                    title=card_data["title"],
                    value=card_data["value"],
                    subtitle=card_data["subtitle"],
                ),
                index // 4,
                index % 4,
            )

        return layout

    def _criar_card_resumo(
            self,
            icon: str,
            title: str,
            value: str,
            subtitle: str,
    ) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(78)
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            """
        )

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(34, 34)
        icon_label.setStyleSheet(
            """
            QLabel {
                background-color: #e0f2fe;
                color: #0369a1;
                border: none;
                border-radius: 17px;
                font-size: 16px;
            }
            """
        )

        textos = QVBoxLayout()
        textos.setSpacing(1)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "border: none; font-size: 11px; color: #64748b;"
        )

        value_label = QLabel(value)
        value_label.setStyleSheet(
            """
            border: none;
            font-size: 17px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "border: none; font-size: 10px; color: #64748b;"
        )

        textos.addWidget(title_label)
        textos.addWidget(value_label)
        textos.addWidget(subtitle_label)

        layout.addWidget(icon_label)
        layout.addLayout(textos)
        layout.addStretch()

        return card

    def _criar_timeline_placeholder(self) -> QFrame:
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
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)

        titulo = QLabel("Linha do tempo da conta")
        titulo.setStyleSheet(
            """
            border: none;
            font-size: 18px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo = QLabel(
            "Aqui vamos reaproveitar a Timeline do Saldo filtrando apenas "
            "os eventos desta conta."
        )
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet(
            """
            border: none;
            font-size: 13px;
            color: #64748b;
            """
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addStretch()

        return card

    def _obter_inicio_periodo(self) -> str:
        reference_day = FinanceSettingsRepository(
            self.username
        ).obter_reference_day()

        hoje = date.today()

        if hoje.day >= reference_day:
            inicio = hoje.replace(day=reference_day)
        else:
            inicio = hoje.replace(day=1) + relativedelta(months=-1)
            ultimo_dia = (inicio + relativedelta(day=31)).day
            inicio = inicio.replace(
                day=min(reference_day, ultimo_dia)
            )

        return inicio.isoformat()

    def _obter_fim_periodo(self) -> str:
        reference_day = FinanceSettingsRepository(
            self.username
        ).obter_reference_day()

        hoje = date.today()

        if hoje.day >= reference_day:
            inicio = hoje.replace(day=reference_day)
        else:
            inicio = hoje.replace(day=1) + relativedelta(months=-1)
            ultimo_dia = (inicio + relativedelta(day=31)).day
            inicio = inicio.replace(
                day=min(reference_day, ultimo_dia)
            )

        fim = inicio + relativedelta(months=1) - relativedelta(days=1)

        return fim.isoformat()

    def _formatar_moeda(
            self,
            valor_cents: int,
    ) -> str:
        valor = valor_cents / 100

        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:
        if not data_iso:
            return "--/--/----"

        partes = data_iso.split("-")

        if len(partes) != 3:
            return data_iso

        return f"{partes[2]}/{partes[1]}/{partes[0]}"

    def _carregar_timeline(self) -> None:
        eventos = self.balance_service.listar_eventos_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
            account_id=self.account["id"],
        )

        resumo = self.balance_service.obter_resumo_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
            account_id=self.account["id"],
        )

        self.timeline.renderizar(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
            eventos=eventos,
            resumo=resumo,
            accounts=[self.account],
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