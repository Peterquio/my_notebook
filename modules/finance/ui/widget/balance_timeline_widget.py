from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class BalanceTimelineWidget(QWidget):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = []
        self.on_period_start_clicked = None
        self.on_period_end_clicked = None
        self.on_fix_estimated_balance = None

        self._montar_interface()

    def _montar_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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

    def renderizar(
            self,
            start_date: str,
            end_date: str,
            eventos: list[dict],
            resumo: dict,
            accounts: list[dict] | None = None,
    ) -> None:
        self.accounts = accounts or []
        self._limpar_cards()

        saldo_acumulado = resumo["saldo_inicial_periodo_cents"]

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            self._criar_barra_periodo(
                start_date=start_date,
                end_date=end_date,
            ),
        )

        tipo_card_inicial = (
            "estimado"
            if resumo.get("saldo_inicial_estimado")
            else "inicio"
        )

        titulo_card_inicial = (
            "Saldo estimado do período"
            if resumo.get("saldo_inicial_estimado")
            else "Saldo inicial do período"
        )

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            self._criar_card_saldo_periodo(
                titulo=titulo_card_inicial,
                data=start_date,
                valor_cents=saldo_acumulado,
                tipo=tipo_card_inicial,
            ),
        )

        primeiro_snapshot_futuro_date = resumo.get(
            "primeiro_snapshot_futuro_date"
        )

        for evento in eventos:
            evento = dict(evento)

            evento["balance_is_estimated"] = (
                primeiro_snapshot_futuro_date is not None
                and evento["date"] < primeiro_snapshot_futuro_date
            )

            if evento["kind"] == "income":
                saldo_acumulado += evento["amount_cents"]
            else:
                saldo_acumulado -= evento["amount_cents"]

            evento["balance_after_cents"] = saldo_acumulado

            self.cards_layout.insertWidget(
                self.cards_layout.count() - 1,
                self._criar_card_evento(evento),
            )

        self.cards_layout.insertWidget(
            self.cards_layout.count() - 1,
            self._criar_card_saldo_periodo(
                titulo="Saldo final estimado",
                data=end_date,
                valor_cents=resumo["saldo_final_estimado_cents"],
                tipo="fim",
            ),
        )

    def _criar_card_saldo_periodo(
            self,
            titulo: str,
            data: str,
            valor_cents: int,
            tipo: str,
    ) -> QFrame:
        if tipo == "estimado":
            cor_fundo = "#faf5ff"
            cor_borda = "#d8b4fe"
            cor_titulo = "#a21caf"
            simbolo = "◆"
        elif valor_cents > 0:
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

        if tipo == "estimado":
            botao = QPushButton("Fixar saldo nesta data")
            botao.setCursor(Qt.PointingHandCursor)

            botao.clicked.connect(
                lambda checked=False, current_date=data: (
                    self.on_fix_estimated_balance(current_date)
                    if self.on_fix_estimated_balance
                    else None
                )
            )

            botao.setStyleSheet(
                """
                QPushButton {
                    background-color: #a21caf;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    padding: 9px 14px;
                    margin-top: 8px;
                }

                QPushButton:hover {
                    background-color: #86198f;
                }
                """
            )

            layout.addWidget(botao)

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
        inicio.setCursor(Qt.PointingHandCursor)
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
        inicio.mousePressEvent = (
            lambda event: self.on_period_start_clicked()
            if self.on_period_start_clicked
            else None
        )

        fim = QLabel(
            f"Fim\n{self._formatar_data(end_date)}"
        )
        fim.setAlignment(Qt.AlignRight)
        fim.setCursor(Qt.PointingHandCursor)
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
        fim.mousePressEvent = (
            lambda event: self.on_period_end_clicked()
            if self.on_period_end_clicked
            else None
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
        is_estimated_balance = evento.get("balance_is_estimated") is True

        if is_estimated_balance:
            cor_fundo = "#faf5ff"
            cor_borda = "#d8b4fe"
            cor_titulo = "#a21caf"
            tipo_texto = (
                "Entrada em trecho estimado"
                if is_income
                else "Saída em trecho estimado"
            )
        elif is_income and is_done:
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

        titulo_layout = QHBoxLayout()
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(8)

        descricao = evento["description"]

        if (
                evento["kind"] == "commitment"
                and evento.get("payment_type") == "credit_card"
                and evento["status"] == "paid"
        ):
            descricao = descricao.replace(
                " — saldo em aberto",
                ""
            )

        titulo = QLabel(descricao)
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

        badge = None

        if evento["kind"] == "commitment":
            status = evento["status"]

            if status == "paid":
                texto = "Pago"
                cor = "#15803d"
                fundo = "#dcfce7"
                borda = "#86efac"

            else:
                from datetime import date

                hoje = date.today().isoformat()

                if evento["date"] < hoje:
                    texto = "Atrasado"
                    cor = "#be123c"
                    fundo = "#ffe4e6"
                    borda = "#fda4af"
                else:
                    texto = "Pendente"
                    cor = "#c2410c"
                    fundo = "#fff7ed"
                    borda = "#fed7aa"

            badge = QLabel(texto)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedWidth(76)
            badge.setMinimumHeight(42)

            badge.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {fundo};
                    color: {cor};
                    border: 1px solid {borda};
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px;
                }}
                """
            )

        titulo_layout.addWidget(titulo)
        titulo_layout.addStretch()

        if badge is not None:
            titulo_layout.addWidget(badge)

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
            evento.get("account_id")
        )

        texto_saldo = (
            "Saldo estimado após evento"
            if evento.get("balance_is_estimated") is True
            else "Saldo após evento"
        )

        detalhe = QLabel(
            f"Conta: {conta} • {texto_saldo}: "
            f"{self._formatar_moeda(evento.get('balance_after_cents', 0))}"
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

        info_layout.addLayout(titulo_layout)
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