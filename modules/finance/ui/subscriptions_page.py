from datetime import date

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QCalendarWidget,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.subscription_service import SubscriptionService
from modules.finance.services.balance_account_service import BalanceAccountService
from modules.finance.services.credit_card_service import CreditCardService


class SubscriptionsPage(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(self, username: str, parent=None) -> None:
        super().__init__(parent)

        self.username = username
        self.subscription_service = SubscriptionService(username)
        self.account_service = BalanceAccountService(username)
        self.credit_card_service = CreditCardService(username)

        self.selected_year = date.today().year
        self.selected_month = date.today().month
        self.month_buttons = []
        self.accounts = []
        self.credit_cards = []

        self.show_inactive = False

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

            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
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

        logo = QLabel("Assinaturas")
        logo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(logo)
        layout.addSpacing(18)

        self.sidebar_buttons = {}

        for texto in ["Dashboard", "Assinaturas", "Configurações"]:
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setStyleSheet(
                self._estilo_botao_sidebar(texto == "Dashboard")
            )

            if texto == "Dashboard":
                botao.clicked.connect(self._mostrar_dashboard)

            if texto == "Assinaturas":
                botao.clicked.connect(self._mostrar_lista_assinaturas)

            if texto == "Configurações":
                botao.clicked.connect(self._mostrar_configuracoes)

            self.sidebar_buttons[texto] = botao
            layout.addWidget(botao)

        layout.addSpacing(18)

        meses_titulo = QLabel("Período")
        meses_titulo.setStyleSheet("""
            color: #64748b;
            font-size: 11px;
            font-weight: bold;
        """)

        layout.addWidget(meses_titulo)

        self.month_buttons_layout = QVBoxLayout()
        self.month_buttons_layout.setSpacing(6)

        layout.addLayout(self.month_buttons_layout)

        self._renderizar_botoes_mes()

        layout.addStretch()

        sair = QPushButton("Sair")
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

    def _carregar_bases(self) -> None:
        self.accounts = self.account_service.listar_contas()
        self.credit_cards = self.credit_card_service.listar_cartoes_ativos()

    def _mostrar_dashboard(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Dashboard")

        assinaturas = self.subscription_service.listar_assinaturas(
            include_inactive=False
        )

        total_cents = sum(
            int(item["amount_cents"] or 0)
            for item in assinaturas
        )

        page = self._criar_placeholder(
            titulo="Dashboard de Assinaturas",
            subtitulo=self._formatar_moeda(total_cents),
            descricao=(
                f"{len(assinaturas)} assinatura(s) ativa(s) no cadastro.\n"
                f"Período selecionado: {self.selected_month:02d}/{self.selected_year}"
            ),
            mostrar_botao=True,
        )

        self.content_layout.addWidget(page)

    def _mostrar_lista_assinaturas(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Assinaturas")
        self._carregar_bases()

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo = QLabel("Assinaturas")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        atualizar = QPushButton("Atualizar")
        atualizar.clicked.connect(self._mostrar_lista_assinaturas)

        nova = QPushButton("Nova assinatura")
        nova.clicked.connect(self._abrir_dialog_nova_assinatura)

        self.show_inactive_check = QCheckBox("Mostrar inativas")
        self.show_inactive_check.setChecked(self.show_inactive)
        self.show_inactive_check.stateChanged.connect(
            self._alternar_visualizacao_inativas
        )

        header.addWidget(self.show_inactive_check)

        header.addWidget(titulo)
        header.addStretch()
        header.addWidget(self.show_inactive_check)
        header.addWidget(atualizar)
        header.addWidget(nova)

        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.cards_layout = QVBoxLayout(content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.content_layout.addWidget(container)

        self._carregar_cards_assinaturas()

    def _alternar_visualizacao_inativas(
            self,
    ) -> None:
        self.show_inactive = self.show_inactive_check.isChecked()
        self._mostrar_lista_assinaturas()

    def _carregar_cards_assinaturas(self) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        assinaturas = self.subscription_service.listar_assinaturas(
            include_inactive=self.show_inactive
        )

        if not assinaturas:
            vazio = self._criar_card_vazio()
            self.cards_layout.insertWidget(0, vazio)
            return

        for assinatura in assinaturas:
            card = self._criar_card_assinatura(assinatura)
            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1,
                card,
            )

    def _criar_card_vazio(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(6)

        titulo = QLabel("Nenhuma assinatura cadastrada")
        titulo.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #0f172a;"
        )

        detalhe = QLabel(
            "Clique em Nova assinatura para cadastrar a primeira."
        )
        detalhe.setStyleSheet("font-size: 13px; color: #64748b;")

        layout.addWidget(titulo)
        layout.addWidget(detalhe)

        return card

    def _criar_card_assinatura(self, assinatura: dict) -> QFrame:
        ativa = bool(assinatura["is_active"])

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {"white" if ativa else "#f8fafc"};
                border: 1px solid {"#dbeafe" if ativa else "#e2e8f0"};
                border-radius: 18px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()

        nome = QLabel(assinatura["name"])
        nome.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #0f172a;
            border: none;
        """)

        valor = QLabel(self._formatar_moeda(assinatura["amount_cents"]))
        valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        valor.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #0369a1;
            border: none;
        """)

        top.addWidget(nome, 1)
        top.addWidget(valor)

        detalhe = QLabel(self._montar_detalhe_assinatura(assinatura))
        detalhe.setWordWrap(True)
        detalhe.setStyleSheet("""
            font-size: 12px;
            color: #64748b;
            border: none;
        """)

        actions = QHBoxLayout()
        actions.addStretch()

        cobranca_ignorada = self._assinatura_ignorada_no_mes(
            assinatura
        )

        cobranca_cobrada = self._assinatura_cobrada_no_mes(
            assinatura
        )

        cobrar = QPushButton(
            "Cobrado este mês" if cobranca_cobrada else "Cobrar"
        )
        cobrar.setEnabled(not cobranca_cobrada)

        if not cobranca_cobrada:
            cobrar.clicked.connect(
                lambda checked=False, item=assinatura:
                self._cobrar_assinatura_mes(item)
            )

        nao_cobrar = QPushButton(
            "Retomar cobrança este mês"
            if cobranca_ignorada
            else "Não cobrar este mês"
        )

        if cobranca_ignorada:
            nao_cobrar.clicked.connect(
                lambda checked=False, item=assinatura:
                self._retomar_cobranca_assinatura_mes(item)
            )
        else:
            nao_cobrar.clicked.connect(
                lambda checked=False, item=assinatura:
                self._nao_cobrar_assinatura_mes(item)
            )

        editar = QPushButton("Editar")
        editar.clicked.connect(
            lambda checked=False, item=assinatura:
            self._abrir_dialog_editar_assinatura(item)
        )

        alternar = QPushButton(
            "Desativar assinatura" if ativa else "Reativar assinatura"
        )
        alternar.clicked.connect(
            lambda checked=False, item=assinatura:
            self._alternar_assinatura(item)
        )

        excluir = QPushButton("Excluir assinatura")
        excluir.clicked.connect(
            lambda checked=False, item=assinatura:
            self._excluir_assinatura(item)
        )

        actions.addWidget(cobrar)
        actions.addWidget(nao_cobrar)
        actions.addWidget(editar)
        actions.addWidget(alternar)
        actions.addWidget(excluir)

        layout.addLayout(top)
        layout.addWidget(detalhe)
        layout.addLayout(actions)

        return card

    def _montar_detalhe_assinatura(self, assinatura: dict) -> str:
        metodo = {
            "bank_account": "Conta",
            "credit_card": "Cartão",
            "pix": "PIX",
        }.get(
            assinatura["payment_method"],
            assinatura["payment_method"],
        )

        destino = "Não definido"

        if assinatura["payment_method"] in {"bank_account", "pix"}:
            destino = assinatura.get("account_name") or "Conta não encontrada"

        if assinatura["payment_method"] == "credit_card":
            destino = assinatura.get("credit_card_name") or "Cartão não encontrado"

        status = "Ativa" if assinatura["is_active"] else "Inativa"

        keywords = assinatura.get("match_keywords") or "Sem palavras-chave"

        periodo = "Sem período definido"

        if assinatura.get("start_date") and assinatura.get("end_date"):
            periodo = (
                f"{assinatura['start_date']} até "
                f"{assinatura['end_date']}"
            )
        elif assinatura.get("start_date"):
            periodo = f"A partir de {assinatura['start_date']}"
        elif assinatura.get("end_date"):
            periodo = f"Até {assinatura['end_date']}"

        return (
            f"Cobrança: todo dia {int(assinatura['charge_day']):02d}  •  "
            f"Pagamento: {metodo} — {destino}  •  "
            f"Status: {status}"
            f"\nPeríodo: {periodo}"
            f"\nMatch: {keywords}"
        )

    def _abrir_dialog_nova_assinatura(self) -> None:
        self._carregar_bases()

        dialog = SubscriptionDialog(
            accounts=self.accounts,
            credit_cards=self.credit_cards,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.subscription_service.criar_assinatura(**dados)
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao criar assinatura",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _abrir_dialog_editar_assinatura(self, assinatura: dict) -> None:
        self._carregar_bases()

        dialog = SubscriptionDialog(
            accounts=self.accounts,
            credit_cards=self.credit_cards,
            subscription_data=assinatura,
            parent=self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.subscription_service.atualizar_assinatura(
                subscription_id=assinatura["id"],
                **dados,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao editar assinatura",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _alternar_assinatura(self, assinatura: dict) -> None:
        try:
            if assinatura["is_active"]:
                self.subscription_service.desativar_assinatura(
                    assinatura["id"]
                )
            else:
                self.subscription_service.reativar_assinatura(
                    assinatura["id"]
                )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao alterar assinatura",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _assinatura_cobrada_no_mes(
            self,
            assinatura: dict,
    ) -> bool:
        override = (
            self.subscription_service.repository.buscar_override_mes(
                subscription_id=assinatura["id"],
                reference_year=self.selected_year,
                reference_month=self.selected_month,
            )
        )

        return (
            override is not None
            and override["status"] == "charged"
        )

    def _cobrar_assinatura_mes(
            self,
            assinatura: dict,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Cobrar assinatura",
            (
                f"Deseja confirmar a cobrança de "
                f"'{assinatura['name']}' em "
                f"{self.selected_month:02d}/{self.selected_year}?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.subscription_service.cobrar_mes(
                subscription_id=assinatura["id"],
                reference_year=self.selected_year,
                reference_month=self.selected_month,
                notes="Cobrança confirmada pela interface de Assinaturas.",
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao cobrar assinatura",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _nao_cobrar_assinatura_mes(
            self,
            assinatura: dict,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Não cobrar este mês",
            (
                f"Deseja ignorar a cobrança de "
                f"'{assinatura['name']}' em "
                f"{self.selected_month:02d}/{self.selected_year}?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.subscription_service.nao_cobrar_mes(
                subscription_id=assinatura["id"],
                reference_year=self.selected_year,
                reference_month=self.selected_month,
                notes=(
                    "Cobrança ignorada pela interface de Assinaturas."
                ),
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao ignorar cobrança",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _assinatura_ignorada_no_mes(
            self,
            assinatura: dict,
    ) -> bool:
        override = (
            self.subscription_service.repository.buscar_override_mes(
                subscription_id=assinatura["id"],
                reference_year=self.selected_year,
                reference_month=self.selected_month,
            )
        )

        return (
            override is not None
            and override["status"] == "ignored"
        )

    def _retomar_cobranca_assinatura_mes(
            self,
            assinatura: dict,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Retomar cobrança este mês",
            (
                f"Deseja retomar a cobrança de "
                f"'{assinatura['name']}' em "
                f"{self.selected_month:02d}/{self.selected_year}?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.subscription_service.retomar_cobranca_mes(
                subscription_id=assinatura["id"],
                reference_year=self.selected_year,
                reference_month=self.selected_month,
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao retomar cobrança",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _excluir_assinatura(
            self,
            assinatura: dict,
    ) -> None:
        resposta = QMessageBox.question(
            self,
            "Excluir assinatura",
            (
                f"Deseja excluir definitivamente "
                f"'{assinatura['name']}'?\n\n"
                "Ela não aparecerá mais nas listas e "
                "não poderá ser reativada pela interface."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.subscription_service.arquivar_assinatura(
                subscription_id=assinatura["id"],
                archive_reason=(
                    "Assinatura Excluída."
                ),
            )
        except Exception as erro:
            QMessageBox.warning(
                self,
                "Erro ao excluir assinatura",
                str(erro),
            )
            return

        self.data_changed.emit()
        self._mostrar_lista_assinaturas()

    def _mostrar_configuracoes(self) -> None:
        self._limpar_area_principal()
        self._atualizar_botao_ativo("Configurações")

        page = self._criar_placeholder(
            titulo="Configurações de Assinaturas",
            subtitulo="Regras de projeção",
            descricao=(
                "Aqui vamos definir tolerância de match, palavras-chave "
                "e comportamento quando uma cobrança mudar de data."
            ),
            mostrar_botao=False,
        )

        self.content_layout.addWidget(page)

    def _criar_placeholder(
            self,
            titulo: str,
            subtitulo: str,
            descricao: str,
            mostrar_botao: bool = False,
    ) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 22, 28, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #0f172a;"
        )

        header.addWidget(titulo_label)
        header.addStretch()

        if mostrar_botao:
            nova = QPushButton("Nova assinatura")
            nova.clicked.connect(self._abrir_dialog_nova_assinatura)
            header.addWidget(nova)

        layout.addLayout(header)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(8)

        subtitulo_label = QLabel(subtitulo)
        subtitulo_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #0f172a;"
        )

        descricao_label = QLabel(descricao)
        descricao_label.setWordWrap(True)
        descricao_label.setStyleSheet(
            "font-size: 13px; color: #64748b;"
        )

        card_layout.addWidget(subtitulo_label)
        card_layout.addWidget(descricao_label)

        layout.addWidget(card)
        layout.addStretch()

        return container

    def _renderizar_botoes_mes(self) -> None:
        while self.month_buttons_layout.count():
            item = self.month_buttons_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.month_buttons = []

        for deslocamento in range(-2, 3):
            year, month = self._somar_meses(
                self.selected_year,
                self.selected_month,
                deslocamento,
            )

            botao_mes = QPushButton(
                self._formatar_mes_sidebar(year, month)
            )
            botao_mes.setCursor(Qt.PointingHandCursor)
            botao_mes.setStyleSheet(
                self._estilo_botao_mes(
                    ativo=(
                        year == self.selected_year
                        and month == self.selected_month
                    )
                )
            )

            botao_mes.clicked.connect(
                lambda checked=False, year=year, month=month:
                self._selecionar_mes(year, month)
            )

            self.month_buttons.append(botao_mes)
            self.month_buttons_layout.addWidget(botao_mes)

    def _selecionar_mes(self, year: int, month: int) -> None:
        self.selected_year = year
        self.selected_month = month

        self._renderizar_botoes_mes()
        self._mostrar_dashboard()

    def _somar_meses(
            self,
            year: int,
            month: int,
            deslocamento: int,
    ) -> tuple[int, int]:
        mes_total = month - 1 + deslocamento
        novo_ano = year + mes_total // 12
        novo_mes = mes_total % 12 + 1

        return novo_ano, novo_mes

    def _formatar_mes_sidebar(self, year: int, month: int) -> str:
        nomes = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Abr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Ago",
            9: "Set",
            10: "Out",
            11: "Nov",
            12: "Dez",
        }

        return f"{nomes[month]}/{year}"

    def _estilo_botao_mes(self, ativo: bool) -> str:
        if ativo:
            return """
                QPushButton {
                    background-color: #e0f2fe;
                    color: #0369a1;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    text-align: left;
                    padding: 9px 12px;
                }
            """

        return """
            QPushButton {
                background-color: white;
                color: #64748b;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding: 9px 12px;
            }

            QPushButton:hover {
                background-color: #f8fafc;
            }
        """

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
                self._estilo_botao_sidebar(
                    ativo=nome == nome_botao
                )
            )

    def _formatar_moeda(self, valor_cents: int) -> str:
        valor = int(valor_cents or 0) / 100
        texto = f"{valor:,.2f}"

        return (
            "R$ "
            + texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )


class SubscriptionDialog(QDialog):
    def __init__(
            self,
            accounts: list[dict],
            credit_cards: list[dict],
            subscription_data: dict | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = accounts
        self.credit_cards = credit_cards
        self.subscription_data = subscription_data

        self.setWindowTitle(
            "Editar assinatura"
            if subscription_data
            else "Nova assinatura"
        )
        self.setMinimumWidth(460)
        self.setMaximumHeight(520)

        self._montar_interface()

        if self.subscription_data:
            self._preencher_dados()

        self._atualizar_destino()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        titulo = QLabel(
            "Editar assinatura"
            if self.subscription_data
            else "Nova assinatura"
        )
        titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f172a;"
        )

        layout.addWidget(titulo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Panobianco, Spotify, Netflix")

        layout.addWidget(QLabel("Nome"))
        layout.addWidget(self.name_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(9999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("R$ ")
        self.amount_input.setSingleStep(10)

        layout.addWidget(QLabel("Valor"))
        layout.addWidget(self.amount_input)

        self.charge_day_input = QSpinBox()
        self.charge_day_input.setMinimum(1)
        self.charge_day_input.setMaximum(31)
        self.charge_day_input.setValue(1)

        layout.addWidget(QLabel("Dia da cobrança"))
        layout.addWidget(self.charge_day_input)

        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItem("Conta", "bank_account")
        self.payment_method_combo.addItem("Cartão de crédito", "credit_card")
        self.payment_method_combo.addItem("PIX", "pix")
        self.payment_method_combo.currentIndexChanged.connect(
            self._atualizar_destino
        )

        layout.addWidget(QLabel("Forma de pagamento"))
        layout.addWidget(self.payment_method_combo)

        self.account_combo = QComboBox()
        for account in self.accounts:
            self.account_combo.addItem(account["name"], account["id"])

        self.destination_label = QLabel("Destino")
        layout.addWidget(self.destination_label)

        self.destination_combo = QComboBox()
        layout.addWidget(self.destination_combo)

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Ex: panobianco; academia")

        layout.addWidget(QLabel("Palavras-chave de identificação"))
        layout.addWidget(self.keywords_input)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Observações")

        layout.addWidget(QLabel("Observações"))
        layout.addWidget(self.notes_input)

        footer = QHBoxLayout()
        footer.addStretch()

        cancelar = QPushButton("Cancelar")
        cancelar.clicked.connect(self.reject)

        salvar = QPushButton("Salvar")
        salvar.clicked.connect(self._salvar)

        footer.addWidget(cancelar)
        footer.addWidget(salvar)

        layout.addStretch()
        layout.addLayout(footer)

    def _preencher_dados(self) -> None:
        self.name_input.setText(self.subscription_data["name"])
        self.amount_input.setValue(
            int(self.subscription_data["amount_cents"] or 0) / 100
        )
        self.charge_day_input.setValue(
            int(self.subscription_data["charge_day"] or 1)
        )
        self._selecionar_combo_por_data(
            self.payment_method_combo,
            self.subscription_data["payment_method"],
        )

        self._atualizar_destino()

        destino_id = (
            self.subscription_data["credit_card_id"]
            if self.subscription_data["payment_method"] == "credit_card"
            else self.subscription_data["account_id"]
        )

        self._selecionar_combo_por_data(
            self.destination_combo,
            destino_id,
        )

        self.keywords_input.setText(
            self.subscription_data["match_keywords"] or ""
        )

        self.notes_input.setText(
            self.subscription_data["notes"] or ""
        )

    def _selecionar_combo_por_data(
            self,
            combo: QComboBox,
            value,
    ) -> None:
        for index in range(combo.count()):
            if combo.itemData(index) == value:
                combo.setCurrentIndex(index)
                return

    def _atualizar_destino(self) -> None:
        metodo = self.payment_method_combo.currentData()

        self.destination_combo.clear()

        if metodo in {"bank_account", "pix"}:
            self.destination_label.setText("Conta")

            for account in self.accounts:
                self.destination_combo.addItem(
                    account["name"],
                    account["id"],
                )

            return

        if metodo == "credit_card":
            self.destination_label.setText("Cartão")

            for card in self.credit_cards:
                self.destination_combo.addItem(
                    card["name"],
                    card["id"],
                )

    def _salvar(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Nome obrigatório",
                "Informe o nome da assinatura.",
            )
            return

        if self.destination_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Destino obrigatório",
                "Selecione o destino da assinatura.",
            )
            return

        self.accept()

    def obter_dados(self) -> dict:
        metodo = self.payment_method_combo.currentData()

        account_id = None
        credit_card_id = None

        if metodo in {"bank_account", "pix"}:
            account_id = self.destination_combo.currentData()

        if metodo == "credit_card":
            credit_card_id = self.destination_combo.currentData()

        return {
            "name": self.name_input.text().strip(),
            "amount_cents": int(round(self.amount_input.value() * 100)),
            "charge_day": self.charge_day_input.value(),
            "payment_method": metodo,
            "account_id": account_id,
            "credit_card_id": credit_card_id,
            "description": None,
            "match_keywords": self.keywords_input.text().strip(),
            "start_date": None,
            "end_date": None,
            "notes": self.notes_input.text().strip(),
        }