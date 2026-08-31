from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modules.finance.services.credit_card_debug_logger import (
    CreditCardDebugLogger,
)
from modules.finance.services.credit_card_debug_service import (
    CreditCardDebugService,
)


class CreditCardDebugWindow(QDialog):

    def __init__(
            self,
            username: str,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.username = username

        self.logger = CreditCardDebugLogger(
            username=self.username
        )

        self.service = CreditCardDebugService(
            username=username,
            logger=self.logger,
        )

        self.setWindowTitle(
            "Diagnóstico de Faturas"
        )

        self.resize(
            1500,
            850,
        )

        self._montar_interface()

        self._carregar_cartoes()
        self._carregar_grupos()
        self._carregar_problemas()
        self._atualizar_log()

    # ============================================================
    # INTERFACE
    # ============================================================

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)

        # --------------------------------------------------------
        # CABEÇALHO
        # --------------------------------------------------------

        titulo = QLabel(
            "Diagnóstico de Faturas"
        )

        titulo.setStyleSheet(
            """
            font-size: 22px;
            font-weight: 700;
            """
        )

        subtitulo = QLabel(
            "Ferramenta de inspeção e correção manual "
            "dos lançamentos de cartão."
        )

        subtitulo.setStyleSheet(
            """
            color: #888888;
            """
        )

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)

        # --------------------------------------------------------
        # ABAS
        # --------------------------------------------------------

        self.tabs = QTabWidget()

        self.tab_grupos = QWidget()
        self.tab_faturas = QWidget()
        self.tab_problemas = QWidget()
        self.tab_log = QWidget()

        self.tabs.addTab(
            self.tab_grupos,
            "Grupos",
        )

        self.tabs.addTab(
            self.tab_faturas,
            "Faturas",
        )

        self.tabs.addTab(
            self.tab_problemas,
            "Problemas",
        )

        self.tabs.addTab(
            self.tab_log,
            "Log",
        )

        layout.addWidget(
            self.tabs,
            1,
        )

        self._montar_aba_grupos()
        self._montar_aba_faturas()
        self._montar_aba_problemas()
        self._montar_aba_log()

    # ============================================================
    # ABA — GRUPOS
    # ============================================================

    def _montar_aba_grupos(self) -> None:
        layout = QVBoxLayout(
            self.tab_grupos
        )

        barra = QHBoxLayout()

        self.filtro_grupo = QLineEdit()

        self.filtro_grupo.setPlaceholderText(
            "Filtrar installment_group_id..."
        )

        self.filtro_grupo.textChanged.connect(
            self._filtrar_grupos
        )

        botao_atualizar = QPushButton(
            "Atualizar"
        )

        botao_atualizar.clicked.connect(
            self._carregar_grupos
        )

        barra.addWidget(
            self.filtro_grupo,
            1,
        )

        barra.addWidget(
            botao_atualizar
        )

        layout.addLayout(barra)

        # --------------------------------------------------------
        # GRUPOS
        # --------------------------------------------------------

        self.tabela_grupos = QTableWidget()

        self.tabela_grupos.setColumnCount(9)

        self.tabela_grupos.setHorizontalHeaderLabels(
            [
                "Installment Group ID",
                "Registros",
                "Ativos",
                "Cancelados",
                "Reais",
                "Projetados",
                "Cartões",
                "Totais",
                "Parcelas",
            ]
        )

        self.tabela_grupos.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabela_grupos.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabela_grupos.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela_grupos.itemSelectionChanged.connect(
            self._grupo_selecionado
        )

        self.tabela_grupos.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addWidget(
            self.tabela_grupos,
            1,
        )

        # --------------------------------------------------------
        # DETALHES DO GRUPO
        # --------------------------------------------------------

        self.label_grupo = QLabel(
            "Selecione um grupo."
        )

        self.label_grupo.setStyleSheet(
            """
            font-weight: 700;
            """
        )

        layout.addWidget(
            self.label_grupo
        )

        self.tabela_parcelas = QTableWidget()

        self.tabela_parcelas.setColumnCount(
            12
        )

        self.tabela_parcelas.setHorizontalHeaderLabels(
            [
                "ID",
                "Parcela",
                "Fatura",
                "Cartão",
                "Valor",
                "Descrição",
                "Data",
                "Origem",
                "Criado por",
                "Status",
                "Problemas",
                "Warnings",
            ]
        )

        self.tabela_parcelas.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabela_parcelas.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabela_parcelas.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela_parcelas.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addWidget(
            self.tabela_parcelas,
            1,
        )

        # --------------------------------------------------------
        # CIRURGIA
        # --------------------------------------------------------

        cirurgia = QHBoxLayout()

        self.input_novo_grupo = QLineEdit()

        self.input_novo_grupo.setPlaceholderText(
            "Novo installment_group_id"
        )

        botao_mover = QPushButton(
            "Mover lançamento para grupo"
        )

        botao_mover.clicked.connect(
            self._mover_lancamento_grupo
        )

        cirurgia.addWidget(
            self.input_novo_grupo,
            1,
        )

        cirurgia.addWidget(
            botao_mover
        )

        layout.addLayout(
            cirurgia
        )

    # ============================================================
    # ABA — FATURAS
    # ============================================================

    def _montar_aba_faturas(self) -> None:
        layout = QVBoxLayout(
            self.tab_faturas
        )

        barra = QHBoxLayout()

        barra.addWidget(
            QLabel("Cartão:")
        )

        self.combo_cartao = QComboBox()

        self.combo_cartao.currentIndexChanged.connect(
            self._carregar_faturas
        )

        barra.addWidget(
            self.combo_cartao
        )

        barra.addWidget(
            QLabel("Fatura:")
        )

        self.combo_fatura = QComboBox()

        barra.addWidget(
            self.combo_fatura,
            1,
        )

        botao_auditar = QPushButton(
            "Auditar fatura"
        )

        botao_auditar.clicked.connect(
            self._auditar_fatura
        )

        barra.addWidget(
            botao_auditar
        )

        layout.addLayout(
            barra
        )

        # --------------------------------------------------------
        # RESUMO
        # --------------------------------------------------------

        self.label_resumo_fatura = QLabel(
            "Selecione uma fatura para auditoria."
        )

        self.label_resumo_fatura.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout.addWidget(
            self.label_resumo_fatura
        )

        # --------------------------------------------------------
        # LANÇAMENTOS
        # --------------------------------------------------------

        self.tabela_fatura = QTableWidget()

        self.tabela_fatura.setColumnCount(
            12
        )

        self.tabela_fatura.setHorizontalHeaderLabels(
            [
                "ID",
                "Usado?",
                "Motivo",
                "Parcela",
                "Grupo",
                "Valor",
                "Descrição",
                "Origem",
                "Status",
                "Esperada",
                "Atual",
                "Problemas",
            ]
        )

        self.tabela_fatura.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabela_fatura.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.tabela_fatura.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela_fatura.horizontalHeader().setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addWidget(
            self.tabela_fatura,
            1,
        )

    # ============================================================
    # ABA — PROBLEMAS
    # ============================================================

    def _montar_aba_problemas(self) -> None:
        layout = QVBoxLayout(
            self.tab_problemas
        )

        barra = QHBoxLayout()

        self.label_total_problemas = QLabel(
            "Problemas: -"
        )

        botao_auditar = QPushButton(
            "Executar auditoria global"
        )

        botao_auditar.clicked.connect(
            self._carregar_problemas
        )

        barra.addWidget(
            self.label_total_problemas
        )

        barra.addStretch()

        barra.addWidget(
            botao_auditar
        )

        layout.addLayout(
            barra
        )

        self.tabela_problemas = QTableWidget()

        self.tabela_problemas.setColumnCount(
            4
        )

        self.tabela_problemas.setHorizontalHeaderLabels(
            [
                "Tipo",
                "ID / Grupo",
                "Descrição",
                "Dados",
            ]
        )

        self.tabela_problemas.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.tabela_problemas.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.tabela_problemas.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addWidget(
            self.tabela_problemas,
            1,
        )

    # ============================================================
    # ABA — LOG
    # ============================================================

    def _montar_aba_log(self) -> None:
        layout = QVBoxLayout(
            self.tab_log
        )

        botoes = QHBoxLayout()

        botao_atualizar = QPushButton(
            "Atualizar"
        )

        botao_atualizar.clicked.connect(
            self._atualizar_log
        )

        botao_copiar = QPushButton(
            "Copiar tudo"
        )

        botao_copiar.clicked.connect(
            self._copiar_log
        )

        botao_limpar = QPushButton(
            "Limpar log"
        )

        botao_limpar.clicked.connect(
            self._limpar_log
        )

        botoes.addWidget(
            botao_atualizar
        )

        botoes.addWidget(
            botao_copiar
        )

        botoes.addWidget(
            botao_limpar
        )

        botoes.addStretch()

        layout.addLayout(
            botoes
        )

        self.texto_log = QTextEdit()

        self.texto_log.setReadOnly(
            True
        )

        self.texto_log.setLineWrapMode(
            QTextEdit.LineWrapMode.NoWrap
        )

        layout.addWidget(
            self.texto_log,
            1,
        )

    # ============================================================
    # CARREGAMENTO — CARTÕES / FATURAS
    # ============================================================

    def _carregar_cartoes(self) -> None:
        self.combo_cartao.blockSignals(
            True
        )

        self.combo_cartao.clear()

        cartoes = (
            self.service.listar_cartoes()
        )

        for cartao in cartoes:
            nome = cartao.get(
                "name"
            ) or f"Cartão {cartao['id']}"

            if not cartao.get(
                    "is_active"
            ):
                nome += " [INATIVO]"

            self.combo_cartao.addItem(
                nome,
                cartao["id"],
            )

        self.combo_cartao.blockSignals(
            False
        )

        self._carregar_faturas()

    def _carregar_faturas(self) -> None:
        if not hasattr(
                self,
                "combo_fatura",
        ):
            return

        self.combo_fatura.clear()

        credit_card_id = (
            self.combo_cartao.currentData()
        )

        if credit_card_id is None:
            return

        faturas = self.service.listar_faturas(
            credit_card_id=credit_card_id,
        )

        for fatura in faturas:
            texto = (
                f"{fatura['invoice_month']:02d}/"
                f"{fatura['invoice_year']} "
                f"— ID {fatura['id']}"
            )

            self.combo_fatura.addItem(
                texto,
                fatura["id"],
            )

    # ============================================================
    # GRUPOS
    # ============================================================

    def _carregar_grupos(self) -> None:
        grupos = self.service.listar_grupos()

        self.tabela_grupos.setRowCount(
            len(grupos)
        )

        for linha, grupo in enumerate(
                grupos
        ):
            valores = [
                grupo.get(
                    "installment_group_id"
                ),
                grupo.get(
                    "total_rows"
                ),
                grupo.get(
                    "active_rows"
                ),
                grupo.get(
                    "cancelled_rows"
                ),
                grupo.get(
                    "real_rows"
                ),
                grupo.get(
                    "projected_rows"
                ),
                grupo.get(
                    "credit_card_count"
                ),
                grupo.get(
                    "installment_total_variants"
                ),
                grupo.get(
                    "installment_number_count"
                ),
            ]

            for coluna, valor in enumerate(
                    valores
            ):
                item = QTableWidgetItem(
                    str(
                        valor
                        if valor is not None
                        else ""
                    )
                )

                self.tabela_grupos.setItem(
                    linha,
                    coluna,
                    item,
                )

        self._filtrar_grupos(
            self.filtro_grupo.text()
        )

    def _filtrar_grupos(
            self,
            texto: str,
    ) -> None:
        texto = texto.lower().strip()

        for linha in range(
                self.tabela_grupos.rowCount()
        ):
            item = (
                self.tabela_grupos.item(
                    linha,
                    0,
                )
            )

            grupo = (
                item.text().lower()
                if item is not None
                else ""
            )

            self.tabela_grupos.setRowHidden(
                linha,
                bool(
                    texto
                    and texto not in grupo
                ),
            )

    def _grupo_selecionado(self) -> None:
        linha = (
            self.tabela_grupos.currentRow()
        )

        if linha < 0:
            return

        item = self.tabela_grupos.item(
            linha,
            0,
        )

        if item is None:
            return

        grupo_id = item.text()

        self._carregar_detalhes_grupo(
            grupo_id
        )

    def _carregar_detalhes_grupo(
            self,
            grupo_id: str,
    ) -> None:
        try:
            resultado = (
                self.service.auditar_grupo(
                    grupo_id
                )
            )

        except Exception as exc:
            self._mostrar_erro(exc)
            return

        rows = resultado["rows"]

        problemas_grupo = resultado[
            "problems"
        ]

        self.label_grupo.setText(
            f"{grupo_id} | "
            f"{len(rows)} registro(s) | "
            f"{len(problemas_grupo)} problema(s)"
        )

        self.tabela_parcelas.setRowCount(
            len(rows)
        )

        for linha, row in enumerate(rows):
            competencia = (
                self._formatar_competencia(
                    row.get("actual_invoice")
                )
            )

            parcela = (
                f"{row.get('installment_number', '')}/"
                f"{row.get('installment_total', '')}"
            )

            problemas = ", ".join(
                row.get(
                    "debug_problems",
                    [],
                )
            )

            warnings = ", ".join(
                row.get(
                    "debug_warnings",
                    [],
                )
            )

            valores = [
                row.get("id"),
                parcela,
                competencia,
                row.get(
                    "expense_credit_card_name"
                ),
                self._formatar_centavos(
                    row.get(
                        "effective_amount_cents"
                    )
                ),
                row.get(
                    "effective_description"
                ),
                row.get(
                    "effective_purchase_date"
                ),
                row.get(
                    "source_type"
                ),
                row.get(
                    "created_by"
                ),
                row.get(
                    "status"
                ),
                problemas,
                warnings,
            ]

            for coluna, valor in enumerate(
                    valores
            ):
                item = QTableWidgetItem(
                    str(
                        valor
                        if valor is not None
                        else ""
                    )
                )

                if coluna == 0:
                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        row["id"],
                    )

                self.tabela_parcelas.setItem(
                    linha,
                    coluna,
                    item,
                )

        self._atualizar_log()

    # ============================================================
    # AUDITAR FATURA
    # ============================================================

    def _auditar_fatura(self) -> None:
        invoice_id = (
            self.combo_fatura.currentData()
        )

        if invoice_id is None:
            return

        try:
            resultado = (
                self.service.auditar_fatura(
                    invoice_id
                )
            )

        except Exception as exc:
            self._mostrar_erro(exc)
            return

        resumo = resultado["summary"]

        self.label_resumo_fatura.setText(
            (
                f"Banco cru: "
                f"{resumo['raw_rows']} lançamento(s) | "
                f"{self._formatar_centavos(resumo['raw_total_cents'])}"
                "     •     "
                f"Cálculo: "
                f"{resumo['calculation_rows']} lançamento(s) | "
                f"{self._formatar_centavos(resumo['calculation_total_cents'])}"
                "     •     "
                f"Excluídos: "
                f"{resumo['excluded_rows']} | "
                f"{self._formatar_centavos(resumo['excluded_total_cents'])}"
                "     •     "
                f"Ajustes: "
                f"{self._formatar_centavos(resumo['official_total_ajustes_cents'])}"
                "     •     "
                f"A pagar: "
                f"{self._formatar_centavos(resumo['official_valor_a_pagar_cents'])}"
            )
        )

        rows = resultado["rows"]

        self.tabela_fatura.setRowCount(
            len(rows)
        )

        for linha, row in enumerate(rows):
            usado = (
                "SIM"
                if row[
                    "used_in_calculation"
                ]
                else "NÃO"
            )

            parcela = (
                f"{row.get('installment_number', '')}/"
                f"{row.get('installment_total', '')}"
            )

            problemas = list(
                row.get(
                    "debug_problems",
                    []
                )
            )

            problemas.extend(
                row.get(
                    "debug_warnings",
                    []
                )
            )

            valores = [
                row.get("id"),
                usado,
                row.get(
                    "calculation_status"
                ),
                parcela,
                row.get(
                    "installment_group_id"
                ),
                self._formatar_centavos(
                    row.get(
                        "effective_amount_cents"
                    )
                ),
                row.get(
                    "effective_description"
                ),
                row.get(
                    "source_type"
                ),
                row.get(
                    "status"
                ),
                self._formatar_competencia(
                    row.get(
                        "expected_invoice"
                    )
                ),
                self._formatar_competencia(
                    row.get(
                        "actual_invoice"
                    )
                ),
                ", ".join(
                    problemas
                ),
            ]

            for coluna, valor in enumerate(
                    valores
            ):
                self.tabela_fatura.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(
                            valor
                            if valor is not None
                            else ""
                        )
                    ),
                )

        self._atualizar_log()

    # ============================================================
    # PROBLEMAS
    # ============================================================

    def _carregar_problemas(self) -> None:
        try:
            resultado = (
                self.service
                .auditar_problemas_globais()
            )

        except Exception as exc:
            self._mostrar_erro(exc)
            return

        self.label_total_problemas.setText(
            f"Problemas: "
            f"{resultado['total_problems']}"
        )

        linhas = []

        categorias = [
            (
                "NO_INVOICE",
                resultado["no_invoice"],
            ),
            (
                "ORPHAN_INVOICE",
                resultado["orphan_invoice"],
            ),
            (
                "CARD_INVOICE_MISMATCH",
                resultado[
                    "card_invoice_mismatch"
                ],
            ),
            (
                "DUPLICATE_INSTALLMENT",
                resultado[
                    "duplicate_installments"
                ],
            ),
            (
                "PROJECTED_REAL_COLLISION",
                resultado[
                    "projected_real_collisions"
                ],
            ),
            (
                "FOREIGN_KEY_ERROR",
                resultado[
                    "foreign_key_errors"
                ],
            ),
        ]

        for tipo, registros in categorias:
            for registro in registros:
                identificador = (
                    registro.get("id")
                    or registro.get(
                        "installment_group_id"
                    )
                    or ""
                )

                descricao = (
                    registro.get(
                        "effective_description"
                    )
                    or registro.get(
                        "source_reference"
                    )
                    or ""
                )

                linhas.append(
                    (
                        tipo,
                        identificador,
                        descricao,
                        registro,
                    )
                )

        self.tabela_problemas.setRowCount(
            len(linhas)
        )

        for linha, dados in enumerate(
                linhas
        ):
            tipo, identificador, descricao, registro = dados

            valores = [
                tipo,
                identificador,
                descricao,
                str(registro),
            ]

            for coluna, valor in enumerate(
                    valores
            ):
                self.tabela_problemas.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(
                        str(valor)
                    ),
                )

        self._atualizar_log()

    # ============================================================
    # MOVER GRUPO
    # ============================================================

    def _mover_lancamento_grupo(self) -> None:
        linha = (
            self.tabela_parcelas.currentRow()
        )

        if linha < 0:
            QMessageBox.warning(
                self,
                "Diagnóstico",
                "Selecione um lançamento.",
            )
            return

        item = self.tabela_parcelas.item(
            linha,
            0,
        )

        if item is None:
            return

        expense_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        novo_grupo = (
            self.input_novo_grupo
            .text()
            .strip()
        )

        if not novo_grupo:
            novo_grupo = None

        resposta = QMessageBox.question(
            self,
            "Confirmar alteração",
            (
                f"Alterar SOMENTE o installment_group_id "
                f"do lançamento {expense_id}?\n\n"
                f"Novo grupo:\n"
                f"{novo_grupo or 'NULL'}\n\n"
                "Nenhuma reconciliação será executada."
            ),
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.mover_lancamento_para_grupo(
                expense_id=expense_id,
                novo_installment_group_id=(
                    novo_grupo
                ),
            )

        except Exception as exc:
            self._mostrar_erro(exc)
            return

        QMessageBox.information(
            self,
            "Diagnóstico",
            "Grupo alterado.",
        )

        self.input_novo_grupo.clear()

        self._carregar_grupos()
        self._atualizar_log()

    # ============================================================
    # LOG
    # ============================================================

    def _atualizar_log(self) -> None:
        self.texto_log.setPlainText(
            self.service.obter_log()
        )

        cursor = (
            self.texto_log.textCursor()
        )

        cursor.movePosition(
            cursor.MoveOperation.End
        )

        self.texto_log.setTextCursor(
            cursor
        )

    def _copiar_log(self) -> None:
        texto = self.service.obter_log()

        QApplication.clipboard().setText(
            texto
        )

        QMessageBox.information(
            self,
            "Diagnóstico",
            "Log copiado.",
        )

    def _limpar_log(self) -> None:
        resposta = QMessageBox.question(
            self,
            "Limpar log",
            "Limpar todo o log desta sessão?",
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        self.service.limpar_log()

        self._atualizar_log()

    # ============================================================
    # HELPERS
    # ============================================================

    def _formatar_centavos(
            self,
            valor,
    ) -> str:
        try:
            valor = int(
                valor or 0
            )
        except (
                TypeError,
                ValueError,
        ):
            valor = 0

        return (
            f"R$ {valor / 100:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_competencia(
            self,
            competencia,
    ) -> str:
        if not competencia:
            return "-"

        try:
            ano, mes = competencia

            return (
                f"{int(mes):02d}/"
                f"{int(ano)}"
            )

        except (
                TypeError,
                ValueError,
        ):
            return str(
                competencia
            )

    def _mostrar_erro(
            self,
            erro: Exception,
    ) -> None:
        self.logger.error(
            f"{type(erro).__name__}: {erro}"
        )

        self._atualizar_log()

        QMessageBox.critical(
            self,
            "Erro no diagnóstico",
            (
                f"{type(erro).__name__}\n\n"
                f"{erro}"
            ),
        )