from datetime import date

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLineEdit,
    QDialog,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QMessageBox,
    QScrollArea,
)

from modules.finance.services.calculator_service import CalculatorService
from ui.widgets.add_card_button import AddCardButton

class TwoLineElideLabel(QLabel):
    def __init__(
            self,
            text: str = "",
            parent=None,
    ) -> None:
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
            candidate = (
                word
                if not current_line
                else f"{current_line} {word}"
            )

            if metrics.horizontalAdvance(candidate) <= self.width():
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

            if len(lines) == 2:
                break

        if current_line and len(lines) < 2:
            lines.append(current_line)

        if len(lines) < 2 and " ".join(lines) == self.full_text:
            super().setText(self.full_text)
            return

        visible_text = "\n".join(lines)

        if visible_text.replace("\n", " ") != self.full_text:
            second_line = lines[-1] if lines else ""
            lines[-1] = metrics.elidedText(
                second_line,
                Qt.ElideRight,
                self.width(),
            )
            visible_text = "\n".join(lines)

        super().setText(visible_text)


class CalculatorWindow(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.service = CalculatorService(username)
        self.sidebar_buttons = {}
        self.current_simulation_id = None

        self._aplicar_estilo_base()
        self._montar_interface()

    def _aplicar_estilo_base(self) -> None:
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: Segoe UI;
                color: #0f172a;
            }

            QLabel {
                color: #0f172a;
            }

            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 9px 14px;
                color: #334155;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #f1f5f9;
            }

            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 10px;
                color: #334155;
                font-size: 12px;
            }
        """)

    def _montar_interface(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._criar_sidebar())
        main_layout.addWidget(self._criar_area_principal(), 1)

    def _criar_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        logo = QLabel("🧮")
        logo.setStyleSheet("font-size: 32px; font-weight: bold;")

        layout.addWidget(logo)
        layout.addSpacing(28)

        botoes = [
            ("Dashboard", True),
            ("Simulação", False),
        ]

        for texto, ativo in botoes:
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(self._estilo_botao_sidebar(ativo))

            self.sidebar_buttons[texto] = botao

            if texto == "Dashboard":
                botao.clicked.connect(self._mostrar_dashboard)

            if texto == "Simulação":
                botao.clicked.connect(self._mostrar_simulacao_atual)

            layout.addWidget(botao)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.setCursor(Qt.PointingHandCursor)
        sair.clicked.connect(self.back_requested.emit)
        sair.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #475569;
                border: none;
                text-align: left;
                padding: 10px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)

        layout.addWidget(sair)

        return sidebar

    def _criar_area_principal(self) -> QWidget:
        container = QWidget()

        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self._mostrar_dashboard()

        return container

    def _limpar_area_principal(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def _mostrar_dashboard(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Dashboard")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Calculadora")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        header.addWidget(titulo)
        header.addStretch()

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.simulations_grid = QGridLayout(content)
        self.simulations_grid.setContentsMargins(0, 0, 0, 0)
        self.simulations_grid.setSpacing(12)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.content_layout.addWidget(container)
        self._carregar_cards_simulacoes()

    def _carregar_cards_simulacoes(self) -> None:
        simulacoes = self.service.listar_simulacoes()

        add_button = AddCardButton()
        add_button.set_base_size(240, 168)
        add_button.clicked.connect(
            self._abrir_dialog_nova_simulacao
        )

        self.simulations_grid.addWidget(
            add_button,
            0,
            0,
        )

        for index, simulacao in enumerate(simulacoes, start=1):
            row = index // 4
            column = index % 4

            self.simulations_grid.addWidget(
                self._criar_card_simulacao(simulacao),
                row,
                column,
            )

    def _criar_card_simulacao(self, simulacao: dict) -> QFrame:
        card = QFrame()
        card.setFixedSize(240, 168)
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet("""
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

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(8)

        titulo = TwoLineElideLabel(simulacao["name"])
        titulo.setStyleSheet("""
            border: none;
            font-size: 15px;
            font-weight: bold;
            color: #0f172a;
        """)

        excluir = QPushButton("×")
        excluir.setFixedSize(28, 28)
        excluir.setCursor(Qt.PointingHandCursor)
        excluir.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }

            QPushButton:hover {
                background-color: #fee2e2;
            }
        """)
        excluir.clicked.connect(
            lambda checked=False, item=simulacao:
            self._excluir_simulacao(item)
        )

        top.addWidget(titulo, 1)
        top.addWidget(excluir)

        tipo = self._formatar_tipo_simulacao(
            simulacao["simulation_type"]
        )

        periodo = self._formatar_periodo_simulacao(simulacao)

        detalhe = QLabel(f"{tipo}\n{periodo}")
        detalhe.setStyleSheet("""
            border: none;
            font-size: 12px;
            color: #64748b;
        """)

        layout.addLayout(top)
        layout.addWidget(detalhe)
        layout.addStretch()

        card.mousePressEvent = (
            lambda event, item=simulacao: self._abrir_simulacao(
                item["id"]
            )
        )

        return card

    def _abrir_dialog_nova_simulacao(self) -> None:
        dialog = CalculatorSimulationDialog(parent=self)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            simulation_id = self.service.criar_simulacao(**dados)
        except Exception as erro:
            QMessageBox.warning(self, "Erro ao criar simulação", str(erro))
            return

        self.current_simulation_id = simulation_id
        self._mostrar_simulacao(simulation_id)
        self.data_changed.emit()

    def _abrir_simulacao(self, simulation_id: int) -> None:
        self.current_simulation_id = simulation_id
        self._mostrar_simulacao(simulation_id)

    def _mostrar_simulacao_atual(self) -> None:
        if self.current_simulation_id is None:
            self._mostrar_dashboard()
            return

        self._mostrar_simulacao(self.current_simulation_id)

    def _mostrar_simulacao(self, simulation_id: int) -> None:
        simulacao = self.service.buscar_simulacao_com_itens(simulation_id)

        if simulacao is None:
            self.current_simulation_id = None
            self._mostrar_dashboard()
            return

        self._limpar_area_principal()
        self._atualizar_botao_ativo("Simulação")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        voltar = QPushButton("←")
        voltar.setFixedSize(38, 38)
        voltar.clicked.connect(self._mostrar_dashboard)

        titulo = QLabel(simulacao["name"])
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        novo_item = QPushButton("+ Adicionar item")
        novo_item.clicked.connect(
            lambda checked=False, item=simulacao:
            self._abrir_dialog_novo_item(item)
        )

        header.addWidget(voltar)
        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(novo_item)

        layout.addLayout(header)
        layout.addLayout(self._criar_resumo_simulacao(simulacao))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.items_layout = QVBoxLayout(content)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(10)
        self.items_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.content_layout.addWidget(container)
        self._renderizar_itens_simulacao(simulacao)

    def _criar_resumo_simulacao(self, simulacao: dict) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        resumo = simulacao["summary"]

        if simulacao["simulation_type"] == "sum_values":
            layout.addWidget(
                self._criar_card_resumo(
                    titulo="Total",
                    valor_cents=resumo["total_cents"],
                    cor="blue",
                )
            )
            return layout

        layout.addWidget(
            self._criar_card_resumo(
                titulo="Entradas",
                valor_cents=resumo["income_cents"],
                cor="green",
            )
        )

        layout.addWidget(
            self._criar_card_resumo(
                titulo="Saídas",
                valor_cents=resumo["expense_cents"],
                cor="red",
            )
        )

        cor_total = (
            "green"
            if resumo["balance_cents"] >= 0
            else "red"
        )

        layout.addWidget(
            self._criar_card_resumo(
                titulo="Total",
                valor_cents=resumo["balance_cents"],
                cor=cor_total,
            )
        )

        return layout

    def _criar_card_resumo(
            self,
            titulo: str,
            valor_cents: int,
            cor: str,
    ) -> QFrame:
        cores = {
            "green": ("#ecfdf5", "#86efac", "#15803d"),
            "red": ("#fff1f2", "#fda4af", "#be123c"),
            "blue": ("#eff6ff", "#93c5fd", "#1d4ed8"),
        }

        fundo, borda, texto = cores[cor]

        card = QFrame()
        card.setMinimumHeight(82)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {fundo};
                border: 1px solid {borda};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            border: none;
            color: {texto};
            font-size: 12px;
            font-weight: bold;
        """)

        valor_label = QLabel(self._formatar_moeda(valor_cents))
        valor_label.setStyleSheet(f"""
            border: none;
            color: {texto};
            font-size: 22px;
            font-weight: bold;
        """)

        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)

        return card

    def _renderizar_itens_simulacao(self, simulacao: dict) -> None:
        itens = simulacao.get("items", [])

        if not itens:
            self.items_layout.insertWidget(
                0,
                self._criar_card_placeholder(
                    "Nenhum item lançado",
                    "Clique em Adicionar item para montar a simulação.",
                ),
            )
            return

        for item in itens:
            self.items_layout.insertWidget(
                self.items_layout.count() - 1,
                self._criar_card_item(item, simulacao),
            )

    def _criar_card_item(
            self,
            item: dict,
            simulacao: dict,
    ) -> QFrame:
        kind = item["kind"]

        if simulacao["simulation_type"] == "sum_values":
            fundo = "#eff6ff"
            borda = "#93c5fd"
            texto = "#1d4ed8"
            tipo = "Valor"
        elif kind == "income":
            fundo = "#ecfdf5"
            borda = "#86efac"
            texto = "#15803d"
            tipo = "Entrada"
        else:
            fundo = "#fff1f2"
            borda = "#fda4af"
            texto = "#be123c"
            tipo = "Saída"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {fundo};
                border: 1px solid {borda};
                border-radius: 16px;
            }}
        """)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        data_label = QLabel(
            self._formatar_data_curta(item.get("item_date"))
        )
        data_label.setFixedWidth(76)
        data_label.setAlignment(Qt.AlignCenter)
        data_label.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                color: {texto};
                border: 1px solid {borda};
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }}
        """)

        info = QVBoxLayout()
        info.setSpacing(2)

        titulo = QLabel(item["title"])
        titulo.setStyleSheet(f"""
            border: none;
            color: {texto};
            font-size: 15px;
            font-weight: bold;
        """)

        detalhe = QLabel(
            f"{tipo} • {self._formatar_moeda(item['amount_cents'])}"
        )
        detalhe.setStyleSheet("""
            border: none;
            color: #64748b;
            font-size: 12px;
        """)

        info.addWidget(titulo)
        info.addWidget(detalhe)

        excluir = QPushButton("×")
        excluir.setFixedSize(30, 30)
        excluir.clicked.connect(
            lambda checked=False, item_id=item["id"]:
            self._excluir_item(item_id)
        )

        layout.addWidget(data_label)
        layout.addLayout(info, 1)
        layout.addWidget(excluir)

        return card

    def _abrir_dialog_novo_item(self, simulacao: dict) -> None:
        dialog = CalculatorItemDialog(
            simulation_type=simulacao["simulation_type"],
            period_mode=simulacao["period_mode"],
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.service.criar_item(
                simulation_id=simulacao["id"],
                **dados,
            )
        except Exception as erro:
            QMessageBox.warning(self, "Erro ao criar item", str(erro))
            return

        self._mostrar_simulacao(simulacao["id"])
        self.data_changed.emit()

    def _excluir_simulacao(self, simulacao: dict) -> None:
        resposta = QMessageBox.question(
            self,
            "Excluir simulação",
            f"Deseja excluir a simulação '{simulacao['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        self.service.excluir_simulacao(simulacao["id"])

        if self.current_simulation_id == simulacao["id"]:
            self.current_simulation_id = None

        self._mostrar_dashboard()
        self.data_changed.emit()

    def _excluir_item(self, item_id: int) -> None:
        if self.current_simulation_id is None:
            return

        self.service.excluir_item(item_id)
        self._mostrar_simulacao(self.current_simulation_id)
        self.data_changed.emit()

    def _criar_card_placeholder(self, titulo: str, subtitulo: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(
            "border: none; font-size: 18px; font-weight: bold;"
        )

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setWordWrap(True)
        subtitulo_label.setStyleSheet(
            "border: none; font-size: 13px; color: #64748b;"
        )

        layout.addWidget(titulo_label)
        layout.addWidget(subtitulo_label)
        layout.addStretch()

        return card

    def _estilo_botao_sidebar(self, ativo: bool) -> str:
        if ativo:
            return """
                QPushButton {
                    background-color: #e0f2fe;
                    color: #0369a1;
                    border: 1px solid #bae6fd;
                    border-radius: 12px;
                    font-weight: bold;
                    text-align: left;
                    padding: 11px 12px;
                }

                QPushButton:hover {
                    background-color: #bae6fd;
                }
            """

        return """
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                text-align: left;
                padding: 11px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
                color: #334155;
                border: 1px solid #cbd5e1;
            }
        """

    def _atualizar_botao_ativo(self, nome_botao: str) -> None:
        for nome, botao in self.sidebar_buttons.items():
            botao.setStyleSheet(
                self._estilo_botao_sidebar(nome == nome_botao)
            )

    def _formatar_tipo_simulacao(self, simulation_type: str) -> str:
        labels = {
            "statement": "Simular Extrato",
            "sum_values": "Somar Valores",
        }

        return labels.get(simulation_type, simulation_type)

    def _formatar_periodo_simulacao(self, simulacao: dict) -> str:
        if simulacao["period_mode"] == "one_month":
            return "Calcular 1 mês"

        start = simulacao.get("start_date") or "--"
        end = simulacao.get("end_date") or "--"

        return f"{self._formatar_data(start)} até {self._formatar_data(end)}"

    def _formatar_moeda(self, valor_cents: int) -> str:
        valor = int(valor_cents or 0) / 100
        texto = f"{valor:,.2f}"

        return (
            "R$ "
            + texto.replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def _formatar_data(self, data_iso: str | None) -> str:
        if not data_iso or data_iso == "--":
            return "--"

        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}/{ano}"

    def _formatar_data_curta(self, data_iso: str | None) -> str:
        if not data_iso:
            return "--"

        ano, mes, dia = data_iso.split("-")
        return f"{dia}/{mes}"


class CalculatorSimulationDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Nova simulação")
        self.setMinimumWidth(420)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        titulo = QLabel("Nova simulação")
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Simulação Julho")

        self.type_combo = QComboBox()
        self.type_combo.addItem("Simular Extrato", "statement")
        self.type_combo.addItem("Somar Valores", "sum_values")

        self.period_combo = QComboBox()
        self.period_combo.addItem("Calcular 1 mês", "one_month")
        self.period_combo.addItem("Período livre", "free_period")
        self.period_combo.currentIndexChanged.connect(
            self._atualizar_campos_periodo
        )

        hoje = QDate.currentDate()

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(hoje)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(hoje)

        layout.addWidget(titulo)
        layout.addWidget(QLabel("Título"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Tipo"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Período"))
        layout.addWidget(self.period_combo)
        layout.addWidget(QLabel("Data inicial"))
        layout.addWidget(self.start_date_input)
        layout.addWidget(QLabel("Data final"))
        layout.addWidget(self.end_date_input)

        footer = QHBoxLayout()
        footer.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Criar")
        salvar.clicked.connect(self._salvar)

        footer.addWidget(cancelar)
        footer.addWidget(salvar)

        layout.addStretch()
        layout.addLayout(footer)

        self._atualizar_campos_periodo()

    def _atualizar_campos_periodo(self) -> None:
        free_period = self.period_combo.currentData() == "free_period"

        self.start_date_input.setVisible(free_period)
        self.end_date_input.setVisible(free_period)

    def _salvar(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Título obrigatório",
                "Informe o título da simulação.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        period_mode = self.period_combo.currentData()

        start_date = None
        end_date = None

        if period_mode == "free_period":
            start_date = self.start_date_input.date().toString("yyyy-MM-dd")
            end_date = self.end_date_input.date().toString("yyyy-MM-dd")

        return {
            "name": self.name_input.text().strip(),
            "simulation_type": self.type_combo.currentData(),
            "period_mode": period_mode,
            "start_date": start_date,
            "end_date": end_date,
            "notes": None,
        }


class CalculatorItemDialog(QDialog):
    def __init__(
            self,
            simulation_type: str,
            period_mode: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.simulation_type = simulation_type
        self.period_mode = period_mode

        self.setWindowTitle("Novo item")
        self.setMinimumWidth(420)

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        titulo = QLabel("Novo item")
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex: Salário, mercado, boleto")

        self.kind_combo = QComboBox()
        self.kind_combo.addItem("Entrada", "income")
        self.kind_combo.addItem("Saída", "expense")

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(999999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("R$ ")
        self.amount_input.setSingleStep(10)

        layout.addWidget(titulo)
        layout.addWidget(QLabel("Título"))
        layout.addWidget(self.title_input)

        if self.simulation_type == "statement":
            layout.addWidget(QLabel("Tipo"))
            layout.addWidget(self.kind_combo)

        layout.addWidget(QLabel("Data"))
        layout.addWidget(self.date_input)
        layout.addWidget(QLabel("Valor"))
        layout.addWidget(self.amount_input)

        footer = QHBoxLayout()
        footer.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Adicionar")
        salvar.clicked.connect(self._salvar)

        footer.addWidget(cancelar)
        footer.addWidget(salvar)

        layout.addStretch()
        layout.addLayout(footer)

    def _salvar(self) -> None:
        if not self.title_input.text().strip():
            QMessageBox.warning(
                self,
                "Título obrigatório",
                "Informe o título do item.",
            )
            return

        if self.amount_input.value() <= 0:
            QMessageBox.warning(
                self,
                "Valor obrigatório",
                "Informe um valor maior que zero.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        kind = "neutral"

        if self.simulation_type == "statement":
            kind = self.kind_combo.currentData()

        return {
            "title": self.title_input.text().strip(),
            "kind": kind,
            "item_date": self.date_input.date().toString("yyyy-MM-dd"),
            "amount_cents": int(round(self.amount_input.value() * 100)),
            "sort_order": 0,
            "notes": None,
        }