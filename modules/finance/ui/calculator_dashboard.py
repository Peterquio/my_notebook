from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics

from core.shared.dashboard.dashboard_home_base import DashboardHomeBase
from ui.widgets.app_card import AppCard
from ui.widgets.card_slot import CardSlot

from modules.finance.services.calculator_service import CalculatorService


class TwoLineElideLabel(QLabel):
    def __init__(self, text: str = "", parent=None) -> None:
        super().__init__(parent)
        self.full_text = text
        self.setWordWrap(True)
        self.setText(text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._aplicar_elide()

    def setText(self, text: str) -> None:
        self.full_text = text
        super().setText(text)

    def _aplicar_elide(self) -> None:
        if not self.full_text:
            return

        metrics = QFontMetrics(self.font())
        line_height = metrics.lineSpacing()
        self.setMaximumHeight(line_height * 2 + 4)

        words = self.full_text.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = word if not current_line else f"{current_line} {word}"

            if metrics.horizontalAdvance(candidate) <= self.width():
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

            if len(lines) == 2:
                break

        if current_line and len(lines) < 2:
            lines.append(current_line)

        visible_text = "\n".join(lines)

        if visible_text.replace("\n", " ") != self.full_text:
            lines[-1] = metrics.elidedText(
                lines[-1],
                Qt.ElideRight,
                self.width(),
            )
            visible_text = "\n".join(lines)

        super().setText(visible_text)


class CalculatorSimulationCard(QFrame):
    def __init__(self, simulation: dict, parent=None) -> None:
        super().__init__(parent)

        self.simulation = simulation
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("CalculatorSimulationCard")

        self._montar_interface()

    def _montar_interface(self) -> None:
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }

            QFrame:hover {
                border: 1px solid #93c5fd;
                background-color: #f8fafc;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        titulo = TwoLineElideLabel(self.simulation["name"])
        titulo.setStyleSheet("""
            border: none;
            font-size: 15px;
            font-weight: bold;
            color: #0f172a;
        """)

        tipo = QLabel(self._formatar_tipo())
        tipo.setStyleSheet("""
            border: none;
            font-size: 12px;
            color: #64748b;
        """)

        periodo = QLabel(self._formatar_periodo())
        periodo.setStyleSheet("""
            border: none;
            font-size: 12px;
            color: #64748b;
        """)

        layout.addWidget(titulo)
        layout.addWidget(tipo)
        layout.addWidget(periodo)
        layout.addStretch()

    def _formatar_tipo(self) -> str:
        labels = {
            "statement": "Simular Extrato",
            "sum_values": "Somar Valores",
        }

        return labels.get(
            self.simulation["simulation_type"],
            self.simulation["simulation_type"],
        )

    def _formatar_periodo(self) -> str:
        if self.simulation["period_mode"] == "one_month":
            return "Calcular 1 mês"

        start = self.simulation.get("start_date") or "--"
        end = self.simulation.get("end_date") or "--"

        return f"{self._formatar_data(start)} até {self._formatar_data(end)}"

    def _formatar_data(self, data_iso: str) -> str:
        if not data_iso or data_iso == "--":
            return "--"

        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"


class CalculatorDashboard(DashboardHomeBase):
    def __init__(
            self,
            username: str,
            on_create_requested,
            on_simulation_open_requested,
            on_simulation_delete_requested,
            parent=None,
    ) -> None:

        self.username = username
        self.service = CalculatorService(username)

        self.on_create_requested = on_create_requested
        self.on_simulation_open_requested = on_simulation_open_requested
        self.on_simulation_delete_requested = on_simulation_delete_requested

        super().__init__(
            title="Calculadora",
            subtitle="Crie e organize suas simulações.",
            spacing=20,
            grid_strategy="sequential",
        )

        self.dashboard_area.add_card_requested.connect(
            self.on_create_requested
        )

        self.setParent(parent)
        self._carregar_simulacoes()

    def _formatar_tipo_simulacao(
            self,
            simulacao: dict,
    ) -> str:

        labels = {
            "statement": "Simular Extrato",
            "sum_values": "Somar Valores",
        }

        return labels.get(
            simulacao["simulation_type"],
            simulacao["simulation_type"],
        )

    def _formatar_periodo_simulacao(
            self,
            simulacao: dict,
    ) -> str:

        if simulacao["period_mode"] == "one_month":
            return "Calcular 1 mês"

        start = simulacao.get("start_date") or "--"
        end = simulacao.get("end_date") or "--"

        return (
            f"{self._formatar_data(start)} até "
            f"{self._formatar_data(end)}"
        )

    def _formatar_data(
            self,
            data_iso: str,
    ) -> str:

        if not data_iso or data_iso == "--":
            return "--"

        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"

    def _salvar_layout_dashboard(self, layout_items: list[dict]) -> None:
        ordered_ids = [
            int(item["card_id"])
            for item in layout_items
            if str(item.get("card_type")) == "calculator_simulation"
        ]

        self.service.atualizar_ordem_simulacoes(
            ordered_ids
        )

    def _carregar_simulacoes(self) -> None:
        self.limpar_dashboard()

        for simulacao in self.service.listar_simulacoes():
            card = AppCard(
                title=simulacao["name"],
                value=self._formatar_tipo_simulacao(simulacao),
                subtitle=self._formatar_periodo_simulacao(simulacao),
                icon="🧮",
            )

            slot = CardSlot(
                card,
                size="1x1",
                card_id=str(simulacao["id"]),
            )

            slot.card_type = "calculator_simulation"
            slot.card_config = simulacao

            slot.clicked.connect(
                lambda current_id=simulacao["id"]:
                self.on_simulation_open_requested(current_id)
            )

            slot.delete_requested.connect(
                lambda _card_id, _config, item=simulacao:
                self.on_simulation_delete_requested(item)
            )

            self.dashboard_area.add_card(
                slot,
                size="1x1",
            )