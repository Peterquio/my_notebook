import calendar
from datetime import date

from dateutil.relativedelta import relativedelta
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class BalanceInitialCycleDialog(QDialog):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Configurar primeiro ciclo")
        self.setMinimumWidth(430)

        self._montar_interface()
        self._carregar_meses()
        self._atualizar_datas_calculadas()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(12)

        titulo = QLabel("Configurar primeiro ciclo")
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        descricao = QLabel(
            "Antes de cadastrar receitas e compromissos, vamos criar o primeiro ciclo financeiro."
        )
        descricao.setWordWrap(True)
        descricao.setStyleSheet(
            "font-size: 12px; color: #475569;"
        )

        self.month_combo = QComboBox()
        self.month_combo.currentIndexChanged.connect(
            self._atualizar_datas_calculadas
        )

        self.start_day_input = QSpinBox()
        self.start_day_input.setRange(1, 31)
        self.start_day_input.setValue(1)
        self.start_day_input.valueChanged.connect(
            self._atualizar_datas_calculadas
        )

        self.start_date_label = QLabel()
        self.start_date_label.setStyleSheet(
            """
            QLabel {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 12px;
            }
            """
        )

        self.end_date_label = QLabel()
        self.end_date_label.setStyleSheet(
            """
            QLabel {
                background-color: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 12px;
            }
            """
        )

        layout.addWidget(titulo)
        layout.addWidget(descricao)

        layout.addWidget(QLabel("Mês inicial"))
        layout.addWidget(self.month_combo)

        layout.addWidget(QLabel("Dia de início do ciclo"))
        layout.addWidget(self.start_day_input)

        layout.addWidget(QLabel("Data de início"))
        layout.addWidget(self.start_date_label)

        layout.addWidget(QLabel("Data de término"))
        layout.addWidget(self.end_date_label)

        botoes = QHBoxLayout()
        botoes.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        criar = QPushButton("Criar ciclo")
        criar.clicked.connect(self._criar)

        botoes.addWidget(cancelar)
        botoes.addWidget(criar)

        layout.addLayout(botoes)

    def _carregar_meses(self) -> None:
        hoje = date.today()
        mes_base = date(hoje.year, hoje.month, 1)

        self.month_combo.blockSignals(True)
        self.month_combo.clear()

        for deslocamento in range(0, 25):
            mes = mes_base - relativedelta(months=deslocamento)

            texto = self._formatar_mes_ano(mes)

            if deslocamento == 0:
                texto = f"Atual — {texto}"

            self.month_combo.addItem(
                texto,
                mes.isoformat(),
            )

        self.month_combo.blockSignals(False)
        self.month_combo.setCurrentIndex(0)

    def _obter_datas_calculadas(self) -> tuple[date, date]:
        mes_iso = self.month_combo.currentData()

        if mes_iso is None:
            hoje = date.today()
            mes_base = date(hoje.year, hoje.month, 1)
        else:
            mes_base = date.fromisoformat(mes_iso)

        dia_escolhido = self.start_day_input.value()

        ultimo_dia_mes = calendar.monthrange(
            mes_base.year,
            mes_base.month,
        )[1]

        dia_inicio = min(
            dia_escolhido,
            ultimo_dia_mes,
        )

        data_inicio = date(
            mes_base.year,
            mes_base.month,
            dia_inicio,
        )

        if dia_inicio == 1:
            data_fim = (
                data_inicio
                + relativedelta(months=1)
                - relativedelta(days=1)
            )
        else:
            proximo_mes = data_inicio + relativedelta(months=1)

            ultimo_dia_proximo_mes = calendar.monthrange(
                proximo_mes.year,
                proximo_mes.month,
            )[1]

            dia_fim = min(
                dia_inicio - 1,
                ultimo_dia_proximo_mes,
            )

            data_fim = date(
                proximo_mes.year,
                proximo_mes.month,
                dia_fim,
            )

        return data_inicio, data_fim

    def _atualizar_datas_calculadas(self) -> None:
        data_inicio, data_fim = self._obter_datas_calculadas()

        self.start_date_label.setText(
            self._formatar_data(data_inicio)
        )

        self.end_date_label.setText(
            self._formatar_data(data_fim)
        )

    def _formatar_mes_ano(
            self,
            data_mes: date,
    ) -> str:
        meses = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }

        return f"{meses[data_mes.month]}/{data_mes.year}"

    def _formatar_data(
            self,
            data: date,
    ) -> str:
        return data.strftime("%d/%m/%Y")

    def _criar(self) -> None:
        data_inicio, data_fim = self._obter_datas_calculadas()

        if data_fim <= data_inicio:
            QMessageBox.warning(
                self,
                "Período inválido",
                "A data de término precisa ser maior que a data de início.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        data_inicio, data_fim = self._obter_datas_calculadas()

        return {
            "name": (
                f"Ciclo "
                f"{self._formatar_data(data_inicio)}"
                f" até "
                f"{self._formatar_data(data_fim)}"
            ),
            "start_date": data_inicio.isoformat(),
            "end_date": data_fim.isoformat(),
            "reference_day": self.start_day_input.value(),
        }