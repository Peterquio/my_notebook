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

from modules.finance.ui.widget.balance_timeline_widget import (
    BalanceTimelineWidget,
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

        self.accounts = []

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

        self.timeline = BalanceTimelineWidget()

        self.timeline.on_period_start_clicked = (
            lambda: self._abrir_calendario_periodo("inicio")
        )

        self.timeline.on_period_end_clicked = (
            lambda: self._abrir_calendario_periodo("fim")
        )

        self.timeline.on_fix_estimated_balance = (
            self._fixar_saldo_estimado
        )

        layout.addWidget(
            self.timeline,
            1,
        )

    def _carregar_dados_base(self) -> None:
        self.accounts = self.account_service.listar_contas()

        inicio, fim = self._obter_periodo_padrao()

        self.start_date_iso = inicio
        self.end_date_iso = fim

        self._carregar_timeline()

    def _fixar_saldo_estimado(
            self,
            data_iso: str,
    ) -> None:
        self.balance_service.fixar_saldo_estimado_na_data(
            data_iso
        )

        self.accounts = self.account_service.listar_contas()

        self._carregar_timeline()

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

    def _carregar_timeline(self) -> None:
        if not self.start_date_iso or not self.end_date_iso:
            return

        eventos = self.balance_service.listar_eventos_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
        )

        resumo = self.balance_service.obter_resumo_periodo(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
        )

        self.timeline.renderizar(
            start_date=self.start_date_iso,
            end_date=self.end_date_iso,
            eventos=eventos,
            resumo=resumo,
            accounts=self.accounts,
        )