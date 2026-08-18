from datetime import date

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QCheckBox,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.subscription_service import (
    SubscriptionService,
)

from modules.finance.services.recurring_payment_service import (
    RecurringPaymentService,
)

from modules.finance.services.finance_category_service import (
    FinanceCategoryService,
)

from modules.finance.ui.widget.category_combo_box import (
    CategoryComboBox,
)

from modules.finance.ui.dialogs.subscription_payment_dialog import (
    SubscriptionPaymentDialog,
)


class SubscriptionsPage(QWidget):
    back_requested = Signal()
    data_changed = Signal()

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self.username = username

        self.subscription_service = (
            SubscriptionService(
                username
            )
        )

        self.recurring_payment_service = (
            RecurringPaymentService(
                username
            )
        )

        self.category_service = (
            FinanceCategoryService(
                username
            )
        )

        hoje = date.today()

        self.selected_year = hoje.year
        self.selected_month = hoje.month

        self.categories = []

        self.show_inactive = False

        self._aplicar_estilo_base()
        self._montar_interface()
        self._carregar_tela()

    # =========================================================
    # ESTILO
    # =========================================================

    def _aplicar_estilo_base(
            self,
    ) -> None:

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
                border-color: #cbd5e1;
            }

            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QTextEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px 10px;
                color: #334155;
                font-size: 12px;
            }

            QLineEdit:focus,
            QSpinBox:focus,
            QDoubleSpinBox:focus,
            QTextEdit:focus {
                border: 1px solid #60a5fa;
            }

            QCheckBox {
                color: #475569;
                font-size: 12px;
                spacing: 7px;
            }
            """
        )

    # =========================================================
    # INTERFACE
    # =========================================================

    def _montar_interface(
            self,
    ) -> None:

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            28,
            22,
            28,
            18,
        )

        main_layout.setSpacing(
            16
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()

        voltar = QPushButton(
            "←"
        )

        voltar.setFixedSize(
            38,
            38,
        )

        voltar.clicked.connect(
            self.back_requested.emit
        )

        titulo = QLabel(
            "Assinaturas"
        )

        titulo.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        nova = QPushButton(
            "+ Nova assinatura"
        )

        nova.setObjectName(
            "NewSubscriptionButton"
        )

        nova.setStyleSheet(
            """
            QPushButton#NewSubscriptionButton {
                background-color: #0284c7;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: bold;
            }

            QPushButton#NewSubscriptionButton:hover {
                background-color: #0369a1;
            }
            """
        )

        nova.clicked.connect(
            self._abrir_dialog_nova_assinatura
        )

        header.addWidget(
            voltar
        )

        header.addWidget(
            titulo
        )

        header.addStretch()

        header.addWidget(
            nova
        )

        main_layout.addLayout(
            header
        )

        # =====================================================
        # SELETOR DE PERÍODO
        # =====================================================

        period_row = QHBoxLayout()

        period_row.setSpacing(
            8
        )

        anterior = QPushButton(
            "‹"
        )

        anterior.setFixedSize(
            34,
            34,
        )

        anterior.clicked.connect(
            lambda:
            self._mudar_mes(-1)
        )

        self.period_label = QLabel()

        self.period_label.setAlignment(
            Qt.AlignCenter
        )

        self.period_label.setMinimumWidth(
            130
        )

        self.period_label.setStyleSheet(
            """
            QLabel {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;

                padding: 8px 16px;

                color: #0f172a;

                font-size: 14px;
                font-weight: bold;
            }
            """
        )

        proximo = QPushButton(
            "›"
        )

        proximo.setFixedSize(
            34,
            34,
        )

        proximo.clicked.connect(
            lambda:
            self._mudar_mes(1)
        )

        hoje = QPushButton(
            "Mês atual"
        )

        hoje.clicked.connect(
            self._voltar_mes_atual
        )

        self.show_inactive_check = (
            QCheckBox(
                "Mostrar inativas"
            )
        )

        self.show_inactive_check.stateChanged.connect(
            self._alternar_visualizacao_inativas
        )

        period_row.addWidget(
            anterior
        )

        period_row.addWidget(
            self.period_label
        )

        period_row.addWidget(
            proximo
        )

        period_row.addWidget(
            hoje
        )

        period_row.addStretch()

        period_row.addWidget(
            self.show_inactive_check
        )

        main_layout.addLayout(
            period_row
        )

        # =====================================================
        # RESUMO
        # =====================================================

        self.summary_layout = (
            QHBoxLayout()
        )

        self.summary_layout.setSpacing(
            10
        )

        main_layout.addLayout(
            self.summary_layout
        )

        # =====================================================
        # LISTAGEM
        # =====================================================

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setFrameShape(
            QFrame.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.cards_container = QWidget()

        self.cards_layout = QVBoxLayout(
            self.cards_container
        )

        self.cards_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.cards_layout.setSpacing(
            10
        )

        self.cards_layout.addStretch()

        self.scroll.setWidget(
            self.cards_container
        )

        main_layout.addWidget(
            self.scroll,
            1,
        )

    # =========================================================
    # CARREGAMENTO
    # =========================================================

    def _carregar_tela(
            self,
    ) -> None:

        self._atualizar_periodo()
        self._carregar_resumo()
        self._carregar_cards()

    # =========================================================
    # PERÍODO
    # =========================================================

    def _atualizar_periodo(
            self,
    ) -> None:

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

        self.period_label.setText(
            (
                f"{meses[self.selected_month]} "
                f"{self.selected_year}"
            )
        )

    def _mudar_mes(
            self,
            deslocamento: int,
    ) -> None:

        total = (
            self.selected_month
            - 1
            + deslocamento
        )

        self.selected_year = (
            self.selected_year
            + total // 12
        )

        self.selected_month = (
            total % 12
            + 1
        )

        self._carregar_tela()

    def _voltar_mes_atual(
            self,
    ) -> None:

        hoje = date.today()

        self.selected_year = hoje.year
        self.selected_month = hoje.month

        self._carregar_tela()

    # =========================================================
    # RESUMO
    # =========================================================

    def _carregar_resumo(
            self,
    ) -> None:

        self._limpar_layout(
            self.summary_layout
        )

        assinaturas = (
            self.subscription_service
            .listar_assinaturas(
                include_inactive=False
            )
        )

        total_esperado = sum(
            int(
                item.get(
                    "amount_cents"
                )
                or 0
            )
            for item in assinaturas
        )

        pagas = 0
        valor_pago = 0

        for assinatura in assinaturas:

            pagamento = (
                self.recurring_payment_service
                .buscar_pagamento_assinatura_mes(
                    subscription_id=(
                        assinatura["id"]
                    ),
                    reference_year=(
                        self.selected_year
                    ),
                    reference_month=(
                        self.selected_month
                    ),
                )
            )

            if pagamento is None:
                continue

            pagas += 1

            valor_pago += int(
                pagamento.get(
                    "paid_amount_cents"
                )
                or 0
            )

        pendentes = (
            len(assinaturas)
            - pagas
        )

        self.summary_layout.addWidget(
            self._criar_card_resumo(
                titulo="Esperado",
                valor=self._formatar_moeda(
                    total_esperado
                ),
                cor="#0369a1",
            )
        )

        self.summary_layout.addWidget(
            self._criar_card_resumo(
                titulo="Pago",
                valor=self._formatar_moeda(
                    valor_pago
                ),
                cor="#15803d",
            )
        )

        self.summary_layout.addWidget(
            self._criar_card_resumo(
                titulo="Pagas",
                valor=str(
                    pagas
                ),
                cor="#15803d",
            )
        )

        self.summary_layout.addWidget(
            self._criar_card_resumo(
                titulo="Pendentes",
                valor=str(
                    pendentes
                ),
                cor="#b91c1c",
            )
        )

    def _criar_card_resumo(
            self,
            titulo: str,
            valor: str,
            cor: str,
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

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )

        layout.setSpacing(
            4
        )

        titulo_label = QLabel(
            titulo
        )

        titulo_label.setStyleSheet(
            """
            color: #64748b;
            font-size: 11px;
            border: none;
            """
        )

        valor_label = QLabel(
            valor
        )

        valor_label.setStyleSheet(
            f"""
            color: {cor};
            font-size: 18px;
            font-weight: bold;
            border: none;
            """
        )

        layout.addWidget(
            titulo_label
        )

        layout.addWidget(
            valor_label
        )

        return card

    # =========================================================
    # LISTAGEM
    # =========================================================

    def _alternar_visualizacao_inativas(
            self,
    ) -> None:

        self.show_inactive = (
            self.show_inactive_check
            .isChecked()
        )

        self._carregar_cards()

    def _carregar_cards(
            self,
    ) -> None:

        while (
            self.cards_layout.count()
            > 1
        ):

            item = (
                self.cards_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        assinaturas = (
            self.subscription_service
            .listar_assinaturas(
                include_inactive=(
                    self.show_inactive
                )
            )
        )

        if not assinaturas:

            self.cards_layout.insertWidget(
                0,
                self._criar_card_vazio(),
            )

            return

        for assinatura in assinaturas:

            self.cards_layout.insertWidget(
                self.cards_layout.count()
                - 1,
                self._criar_card_assinatura(
                    assinatura
                ),
            )

    def _criar_card_vazio(
            self,
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

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            22,
            22,
            22,
            22,
        )

        titulo = QLabel(
            "Nenhuma assinatura cadastrada"
        )

        titulo.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            border: none;
            """
        )

        detalhe = QLabel(
            "Clique em + Nova assinatura para começar."
        )

        detalhe.setStyleSheet(
            """
            color: #64748b;
            font-size: 12px;
            border: none;
            """
        )

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            detalhe
        )

        return card

    # =========================================================
    # CARD DE ASSINATURA
    # =========================================================

    def _criar_card_assinatura(
            self,
            assinatura: dict,
    ) -> QFrame:

        ativa = bool(
            assinatura["is_active"]
        )

        pagamento = (
            self.recurring_payment_service
            .buscar_pagamento_assinatura_mes(
                subscription_id=(
                    assinatura["id"]
                ),
                reference_year=(
                    self.selected_year
                ),
                reference_month=(
                    self.selected_month
                ),
            )
        )

        paga = (
            pagamento is not None
        )

        card = QFrame()

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {
                    "white"
                    if ativa
                    else "#f8fafc"
                };

                border: 1px solid {
                    "#e2e8f0"
                    if ativa
                    else "#cbd5e1"
                };

                border-radius: 16px;
            }}
            """
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18,
            14,
            18,
            14,
        )

        layout.setSpacing(
            9
        )

        # =====================================================
        # TOPO
        # =====================================================

        top = QHBoxLayout()

        nome = QLabel(
            assinatura["name"]
        )

        nome.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #0f172a;
            border: none;
            """
        )

        status = QLabel(
            "Paga"
            if paga
            else "Pendente"
        )

        status.setAlignment(
            Qt.AlignCenter
        )

        status.setStyleSheet(
            f"""
            QLabel {{
                background-color: {
                    "#dcfce7"
                    if paga
                    else "#fef3c7"
                };

                color: {
                    "#15803d"
                    if paga
                    else "#92400e"
                };

                border: none;
                border-radius: 9px;

                padding: 4px 9px;

                font-size: 10px;
                font-weight: bold;
            }}
            """
        )

        valor = QLabel(
            self._formatar_moeda(
                assinatura.get(
                    "amount_cents"
                )
            )
        )

        valor.setStyleSheet(
            """
            color: #0369a1;
            font-size: 16px;
            font-weight: bold;
            border: none;
            """
        )

        top.addWidget(
            nome
        )

        top.addWidget(
            status
        )

        top.addStretch()

        top.addWidget(
            valor
        )

        layout.addLayout(
            top
        )

        # =====================================================
        # DETALHES
        # =====================================================

        categoria = (
            assinatura.get(
                "category_name"
            )
            or "Sem categoria"
        )

        detalhe = QLabel(
            (
                f"Dia {int(assinatura['charge_day']):02d}"
                f"  •  {categoria}"
                f"  •  "
                f"{'Ativa' if ativa else 'Inativa'}"
            )
        )

        detalhe.setStyleSheet(
            """
            color: #64748b;
            font-size: 12px;
            border: none;
            """
        )

        layout.addWidget(
            detalhe
        )

        # =====================================================
        # PAGAMENTO VINCULADO
        # =====================================================

        if pagamento is not None:

            origem = {
                "pix": "PIX",
                "credit_card": "Cartão de Crédito",
            }.get(
                pagamento.get(
                    "payment_source"
                ),
                "Pagamento",
            )

            pagamento_label = QLabel(
                (
                    f"{origem}"
                    f"  •  "
                    f"{self._formatar_moeda(
                        pagamento.get(
                            'paid_amount_cents'
                        )
                    )}"
                    f"  •  "
                    f"{self._formatar_data(
                        pagamento.get(
                            'paid_date'
                        )
                    )}"
                )
            )

            pagamento_label.setStyleSheet(
                """
                color: #15803d;
                font-size: 12px;
                font-weight: 600;
                border: none;
                """
            )

            layout.addWidget(
                pagamento_label
            )

        # =====================================================
        # OBSERVAÇÕES
        # =====================================================

        if assinatura.get(
                "notes"
        ):

            observacoes = QLabel(
                assinatura["notes"]
            )

            observacoes.setWordWrap(
                True
            )

            observacoes.setStyleSheet(
                """
                color: #94a3b8;
                font-size: 11px;
                border: none;
                """
            )

            layout.addWidget(
                observacoes
            )

        # =====================================================
        # AÇÕES
        # =====================================================

        actions = QHBoxLayout()

        actions.addStretch()

        if pagamento is None:

            pagamento_button = QPushButton(
                "Já pagou?"
            )

            pagamento_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #eff6ff;
                    color: #1d4ed8;
                    border: 1px solid #93c5fd;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background-color: #dbeafe;
                }
                """
            )

            pagamento_button.clicked.connect(
                lambda checked=False,
                       item=assinatura:
                self._abrir_vinculo_pagamento(
                    item
                )
            )

        else:

            origem_curta = {
                "pix": "PIX",
                "credit_card": "Cartão",
            }.get(
                pagamento.get(
                    "payment_source"
                ),
                "Pagamento",
            )

            pagamento_button = QPushButton(
                f"✓ Pago via {origem_curta}"
            )

            pagamento_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #dcfce7;
                    color: #15803d;
                    border: 1px solid #86efac;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background-color: #bbf7d0;
                }
                """
            )

            pagamento_button.clicked.connect(
                lambda checked=False,
                       item=assinatura,
                       payment=pagamento:
                self._mostrar_pagamento_vinculado(
                    item,
                    payment,
                )
            )

        editar = QPushButton(
            "Editar"
        )

        editar.clicked.connect(
            lambda checked=False,
                   item=assinatura:
            self._abrir_dialog_editar_assinatura(
                item
            )
        )

        alternar = QPushButton(
            "Desativar"
            if ativa
            else "Reativar"
        )

        alternar.clicked.connect(
            lambda checked=False,
                   item=assinatura:
            self._alternar_assinatura(
                item
            )
        )

        excluir = QPushButton(
            "Excluir"
        )

        excluir.clicked.connect(
            lambda checked=False,
                   item=assinatura:
            self._excluir_assinatura(
                item
            )
        )

        actions.addWidget(
            pagamento_button
        )

        actions.addWidget(
            editar
        )

        actions.addWidget(
            alternar
        )

        actions.addWidget(
            excluir
        )

        layout.addLayout(
            actions
        )

        return card

    # =========================================================
    # VINCULAR PAGAMENTO
    # =========================================================

    def _abrir_vinculo_pagamento(
            self,
            assinatura: dict,
    ) -> None:

        dialog = SubscriptionPaymentDialog(
            username=self.username,
            subscription=assinatura,
            reference_year=self.selected_year,
            reference_month=self.selected_month,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.Accepted
        ):
            return

        dados = (
            dialog.obter_dados()
        )

        try:

            if (
                dados["payment_source"]
                == "pix"
            ):

                self.recurring_payment_service \
                    .marcar_assinatura_paga_por_pix(
                        subscription_id=(
                            assinatura["id"]
                        ),
                        pix_transaction_id=(
                            dados["payment_id"]
                        ),
                        reference_year=(
                            self.selected_year
                        ),
                        reference_month=(
                            self.selected_month
                        ),
                    )

            elif (
                dados["payment_source"]
                == "credit_card"
            ):

                self.recurring_payment_service \
                    .marcar_assinatura_paga_por_cartao(
                        subscription_id=(
                            assinatura["id"]
                        ),
                        credit_card_expense_id=(
                            dados["payment_id"]
                        ),
                        reference_year=(
                            self.selected_year
                        ),
                        reference_month=(
                            self.selected_month
                        ),
                    )

            else:

                raise ValueError(
                    "Origem de pagamento inválida."
                )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível vincular",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # PAGAMENTO EXISTENTE
    # =========================================================

    def _mostrar_pagamento_vinculado(
            self,
            assinatura: dict,
            pagamento: dict,
    ) -> None:

        origem = {
            "pix": "PIX",
            "credit_card": "Cartão de Crédito",
        }.get(
            pagamento.get(
                "payment_source"
            ),
            "Pagamento",
        )

        valor = self._formatar_moeda(
            pagamento.get(
                "paid_amount_cents"
            )
        )

        data_pagamento = (
            self._formatar_data(
                pagamento.get(
                    "paid_date"
                )
            )
        )

        resposta = QMessageBox.question(
            self,
            "Pagamento vinculado",
            (
                f"{assinatura['name']}\n"
                f"{self.selected_month:02d}/"
                f"{self.selected_year}\n\n"

                f"Origem: {origem}\n"
                f"Valor: {valor}\n"
                f"Data: {data_pagamento}\n\n"

                "Deseja desvincular este pagamento?\n\n"
                "O PIX ou lançamento do cartão "
                "não será apagado nem alterado."
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:

            self.recurring_payment_service \
                .desvincular_pagamento_assinatura(
                    subscription_id=(
                        assinatura["id"]
                    ),
                    reference_year=(
                        self.selected_year
                    ),
                    reference_month=(
                        self.selected_month
                    ),
                )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível desvincular",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # CATEGORIAS
    # =========================================================

    def _carregar_categorias(
            self,
    ) -> None:

        self.categories = (
            self.category_service
            .listar_categorias_ativas()
        )

    # =========================================================
    # NOVA ASSINATURA
    # =========================================================

    def _abrir_dialog_nova_assinatura(
            self,
    ) -> None:

        self._carregar_categorias()

        dialog = SubscriptionDialog(
            categories=self.categories,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.Accepted
        ):
            return

        try:

            self.subscription_service \
                .criar_assinatura(
                    **dialog.obter_dados()
                )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível salvar",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # EDITAR ASSINATURA
    # =========================================================

    def _abrir_dialog_editar_assinatura(
            self,
            assinatura: dict,
    ) -> None:

        self._carregar_categorias()

        dialog = SubscriptionDialog(
            categories=self.categories,
            subscription_data=assinatura,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.Accepted
        ):
            return

        try:

            self.subscription_service \
                .atualizar_assinatura(
                    subscription_id=(
                        assinatura["id"]
                    ),
                    **dialog.obter_dados(),
                )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível atualizar",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # ATIVAR / DESATIVAR
    # =========================================================

    def _alternar_assinatura(
            self,
            assinatura: dict,
    ) -> None:

        try:

            if assinatura["is_active"]:

                self.subscription_service \
                    .desativar_assinatura(
                        assinatura["id"]
                    )

            else:

                self.subscription_service \
                    .reativar_assinatura(
                        assinatura["id"]
                    )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível alterar",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # EXCLUIR
    # =========================================================

    def _excluir_assinatura(
            self,
            assinatura: dict,
    ) -> None:

        resposta = QMessageBox.question(
            self,
            "Excluir assinatura",
            (
                f"Deseja excluir "
                f"'{assinatura['name']}'?"
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:

            self.subscription_service \
                .arquivar_assinatura(
                    subscription_id=(
                        assinatura["id"]
                    ),
                    archive_reason=(
                        "Assinatura excluída."
                    ),
                )

        except ValueError as erro:

            QMessageBox.warning(
                self,
                "Não foi possível excluir",
                str(erro),
            )

            return

        self.data_changed.emit()

        self._carregar_tela()

    # =========================================================
    # HELPERS
    # =========================================================

    def _limpar_layout(
            self,
            layout,
    ) -> None:

        while layout.count():

            item = (
                layout.takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

            child_layout = (
                item.layout()
            )

            if child_layout:

                self._limpar_layout(
                    child_layout
                )

    def _formatar_moeda(
            self,
            cents: int | None,
    ) -> str:

        valor = int(
            cents or 0
        ) / 100

        texto = (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"R$ {texto}"
        )

    def _formatar_data(
            self,
            data_iso: str | None,
    ) -> str:

        if not data_iso:
            return "--"

        try:

            ano, mes, dia = (
                data_iso.split("-")
            )

            return (
                f"{dia}/{mes}/{ano}"
            )

        except ValueError:

            return data_iso


# =============================================================
# DIALOG DE CADASTRO / EDIÇÃO
# =============================================================


class SubscriptionDialog(QDialog):
    def __init__(
            self,
            categories: list[dict],
            subscription_data: dict | None = None,
            parent=None,
    ) -> None:

        super().__init__(parent)

        self.categories = (
            categories
        )

        self.subscription_data = (
            subscription_data
        )

        self.setWindowTitle(
            (
                "Editar assinatura"
                if subscription_data
                else "Nova assinatura"
            )
        )

        self.setFixedWidth(
            440
        )

        self._montar_interface()

        if self.subscription_data:

            self._preencher_dados()

    # =========================================================
    # INTERFACE
    # =========================================================

    def _montar_interface(
            self,
    ) -> None:

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            22,
            22,
            22,
            22,
        )

        layout.setSpacing(
            10
        )

        titulo = QLabel(
            (
                "Editar assinatura"
                if self.subscription_data
                else "Nova assinatura"
            )
        )

        titulo.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            titulo
        )

        # =====================================================
        # NOME
        # =====================================================

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "Ex.: Netflix"
        )

        layout.addWidget(
            QLabel("Nome")
        )

        layout.addWidget(
            self.name_input
        )

        # =====================================================
        # VALOR
        # =====================================================

        self.amount_input = (
            QDoubleSpinBox()
        )

        self.amount_input.setMaximum(
            9_999_999
        )

        self.amount_input.setDecimals(
            2
        )

        self.amount_input.setPrefix(
            "R$ "
        )

        self.amount_input.setSingleStep(
            1
        )

        layout.addWidget(
            QLabel(
                "Valor esperado"
            )
        )

        layout.addWidget(
            self.amount_input
        )

        # =====================================================
        # DIA
        # =====================================================

        self.charge_day_input = (
            QSpinBox()
        )

        self.charge_day_input.setRange(
            1,
            31,
        )

        self.charge_day_input.setValue(
            1
        )

        layout.addWidget(
            QLabel(
                "Dia da cobrança"
            )
        )

        layout.addWidget(
            self.charge_day_input
        )

        # =====================================================
        # CATEGORIA
        # =====================================================

        self.category_combo = (
            CategoryComboBox(
                categories=(
                    self.categories
                ),
                height=38,
                placeholder=(
                    "Escolha uma categoria"
                ),
            )
        )

        layout.addWidget(
            QLabel(
                "Categoria"
            )
        )

        layout.addWidget(
            self.category_combo
        )

        # =====================================================
        # DESCRIÇÃO
        # =====================================================

        self.description_input = (
            QLineEdit()
        )

        self.description_input.setPlaceholderText(
            "Descrição opcional"
        )

        layout.addWidget(
            QLabel(
                "Descrição"
            )
        )

        layout.addWidget(
            self.description_input
        )

        # =====================================================
        # OBSERVAÇÕES
        # =====================================================

        self.notes_input = QTextEdit()

        self.notes_input.setFixedHeight(
            70
        )

        self.notes_input.setPlaceholderText(
            "Observações"
        )

        layout.addWidget(
            QLabel(
                "Observações"
            )
        )

        layout.addWidget(
            self.notes_input
        )

        # =====================================================
        # FOOTER
        # =====================================================

        footer = QHBoxLayout()

        footer.addStretch()

        cancelar = QPushButton(
            "Cancelar"
        )

        cancelar.clicked.connect(
            self.reject
        )

        salvar = QPushButton(
            "Salvar"
        )

        salvar.setStyleSheet(
            """
            QPushButton {
                background-color: #0284c7;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #0369a1;
            }
            """
        )

        salvar.clicked.connect(
            self._salvar
        )

        footer.addWidget(
            cancelar
        )

        footer.addWidget(
            salvar
        )

        layout.addLayout(
            footer
        )

    # =========================================================
    # EDIÇÃO
    # =========================================================

    def _preencher_dados(
            self,
    ) -> None:

        self.name_input.setText(
            self.subscription_data.get(
                "name",
                "",
            )
        )

        self.amount_input.setValue(
            int(
                self.subscription_data.get(
                    "amount_cents"
                )
                or 0
            )
            / 100
        )

        self.charge_day_input.setValue(
            int(
                self.subscription_data.get(
                    "charge_day"
                )
                or 1
            )
        )

        self.category_combo.select_category(
            self.subscription_data.get(
                "category_id"
            )
        )

        self.description_input.setText(
            self.subscription_data.get(
                "description"
            )
            or ""
        )

        self.notes_input.setPlainText(
            self.subscription_data.get(
                "notes"
            )
            or ""
        )

    # =========================================================
    # SALVAR
    # =========================================================

    def _salvar(
            self,
    ) -> None:

        if not (
            self.name_input
            .text()
            .strip()
        ):

            QMessageBox.warning(
                self,
                "Nome obrigatório",
                "Informe o nome da assinatura.",
            )

            return

        if (
            self.amount_input.value()
            <= 0
        ):

            QMessageBox.warning(
                self,
                "Valor obrigatório",
                "Informe o valor da assinatura.",
            )

            return

        if (
            self.category_combo
            .category_id()
            is None
        ):

            QMessageBox.warning(
                self,
                "Categoria obrigatória",
                "Escolha uma categoria.",
            )

            return

        self.accept()

    # =========================================================
    # RESULTADO
    # =========================================================

    def obter_dados(
            self,
    ) -> dict:

        return {
            "name": (
                self.name_input
                .text()
                .strip()
            ),

            "amount_cents": int(
                round(
                    self.amount_input
                    .value()
                    * 100
                )
            ),

            "charge_day": (
                self.charge_day_input
                .value()
            ),

            "category_id": (
                self.category_combo
                .category_id()
            ),

            "description": (
                self.description_input
                .text()
                .strip()
                or None
            ),

            "notes": (
                self.notes_input
                .toPlainText()
                .strip()
                or None
            ),
        }