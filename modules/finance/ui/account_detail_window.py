from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


class AccountDetailWindow(QWidget):
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
        self.sidebar_buttons = {}

        self._aplicar_estilo_base()
        self._montar_interface()

    def _aplicar_estilo_base(self) -> None:
        self.setStyleSheet(
            """
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
            """
        )

    def _montar_interface(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(
            self._criar_sidebar()
        )

        main_layout.addWidget(
            self._criar_area_principal(),
            1,
        )

    def _criar_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
            """
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        logo = QLabel("🏦")
        logo.setStyleSheet(
            """
            font-size: 32px;
            font-weight: bold;
            """
        )

        layout.addWidget(logo)
        layout.addSpacing(28)

        botoes = [
            ("Dashboard", True),
            ("Pix", False),
            ("Extrato", False),
            ("Snapshots", False),
            ("Configurações", False),
        ]

        for texto, ativo in botoes:
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(
                self._estilo_botao_sidebar(ativo)
            )

            self.sidebar_buttons[texto] = botao

            if texto == "Dashboard":
                botao.clicked.connect(
                    self._mostrar_dashboard
                )

            if texto == "Pix":
                botao.clicked.connect(
                    lambda checked=False: self._mostrar_placeholder("Pix")
                )

            if texto == "Extrato":
                botao.clicked.connect(
                    lambda checked=False: self._mostrar_placeholder("Extrato")
                )

            if texto == "Snapshots":
                botao.clicked.connect(
                    lambda checked=False: self._mostrar_placeholder("Snapshots")
                )

            if texto == "Configurações":
                botao.clicked.connect(
                    lambda checked=False: self._mostrar_placeholder("Configurações")
                )

            layout.addWidget(botao)

        layout.addStretch()

        sair = QPushButton("Sair")
        sair.setCursor(Qt.PointingHandCursor)
        sair.clicked.connect(
            self.back_requested.emit
        )
        sair.setStyleSheet(
            """
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
            """
        )

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

        self.content_layout.addWidget(
            self._criar_dashboard_placeholder()
        )

    def _mostrar_placeholder(
            self,
            nome_pagina: str,
    ) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo(nome_pagina)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(16)

        layout.addLayout(
            self._criar_header(nome_pagina)
        )

        card = self._criar_card_placeholder(
            titulo=nome_pagina,
            subtitulo="Essa área será implementada em uma próxima etapa.",
        )

        layout.addWidget(card)
        layout.addStretch()

        self.content_layout.addWidget(container)

    def _criar_dashboard_placeholder(self) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        layout.addLayout(
            self._criar_header("Dashboard")
        )

        resumo = QHBoxLayout()
        resumo.setSpacing(12)

        resumo.addWidget(
            self._criar_card_info(
                titulo="Conta",
                valor=self.account.get("name") or "Conta bancária",
                subtitulo=self.account.get("institution_name") or "Instituição não informada",
            )
        )

        resumo.addWidget(
            self._criar_card_info(
                titulo="Tipo",
                valor=self._formatar_tipo_conta(),
                subtitulo=self.account.get("account_type") or "bank",
            )
        )

        resumo.addWidget(
            self._criar_card_info(
                titulo="Identificação",
                valor=self._formatar_identificacao(),
                subtitulo="Agência e conta",
            )
        )

        layout.addLayout(resumo)

        layout.addWidget(
            self._criar_card_placeholder(
                titulo="Dashboard da conta",
                subtitulo=(
                    "Aqui entraremos com resumo da conta, Pix agendados, "
                    "extrato, previsões e reconciliação de snapshots."
                ),
            ),
            1,
        )

        return container

    def _criar_header(
            self,
            titulo_pagina: str,
    ) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        voltar = QPushButton("←")
        voltar.setFixedSize(38, 38)
        voltar.clicked.connect(
            self.back_requested.emit
        )

        titulo = QLabel(
            f"{titulo_pagina} — {self.account.get('name') or 'Conta bancária'}"
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

        atualizado = QLabel("Estrutura inicial da conta")
        atualizado.setStyleSheet(
            "font-size: 12px; color: #64748b;"
        )

        layout.addWidget(voltar)
        layout.addWidget(titulo)
        layout.addWidget(instituicao)
        layout.addStretch()
        layout.addWidget(atualizado)

        return layout

    def _criar_card_info(
            self,
            titulo: str,
            valor: str,
            subtitulo: str,
    ) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(82)
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            """
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(
            "border: none; font-size: 11px; color: #64748b;"
        )

        valor_label = QLabel(valor)
        valor_label.setStyleSheet(
            """
            border: none;
            font-size: 17px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setStyleSheet(
            "border: none; font-size: 10px; color: #64748b;"
        )

        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)
        layout.addWidget(subtitulo_label)

        return card

    def _criar_card_placeholder(
            self,
            titulo: str,
            subtitulo: str,
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
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(
            """
            border: none;
            font-size: 18px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setWordWrap(True)
        subtitulo_label.setStyleSheet(
            """
            border: none;
            font-size: 13px;
            color: #64748b;
            """
        )

        layout.addWidget(titulo_label)
        layout.addWidget(subtitulo_label)
        layout.addStretch()

        return card

    def _estilo_botao_sidebar(
            self,
            ativo: bool,
    ) -> str:
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

    def _atualizar_botao_ativo(
            self,
            nome_botao: str,
    ) -> None:
        for nome, botao in self.sidebar_buttons.items():
            botao.setStyleSheet(
                self._estilo_botao_sidebar(
                    ativo=nome == nome_botao
                )
            )

    def _formatar_tipo_conta(self) -> str:
        labels = {
            "checking": "Conta corrente",
            "savings": "Conta poupança",
            "payment": "Conta pagamento",
            "other": "Conta bancária",
        }

        return labels.get(
            self.account.get("account_kind"),
            "Conta bancária",
        )

    def _formatar_identificacao(self) -> str:
        partes = []

        agency = self.account.get("agency")
        account_number = self.account.get("account_number")

        if agency:
            partes.append(f"Ag. {agency}")

        if account_number:
            partes.append(f"Conta {account_number}")

        return " • ".join(partes) if partes else "Não informado"