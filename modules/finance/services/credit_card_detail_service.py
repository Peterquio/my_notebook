from datetime import date
from uuid import uuid4

from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)

from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)

from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)

from modules.finance.repositories.credit_card_invoice_adjustment_repository import (
    CreditCardInvoiceAdjustmentRepository,
)

class CreditCardDetailService:
    def __init__(self, username: str) -> None:
        self.username = username
        self.invoice_repository = CreditCardInvoiceRepository(username)
        self.expense_repository = CreditCardExpenseRepository(username)
        self.invoice_service = CreditCardInvoiceService()
        self.adjustment_repository = CreditCardInvoiceAdjustmentRepository(username)

    def carregar_fatura_atual(
            self,
            credit_card: dict,
            sort_mode: str = "categoria",
    ) -> dict:
        hoje = date.today()

        invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
            purchase_date=hoje,
            closing_day=credit_card["closing_day"],
        )

        return self.carregar_fatura_por_mes(
            credit_card=credit_card,
            invoice_year=invoice_year,
            invoice_month=invoice_month,
            sort_mode=sort_mode,
        )

    def carregar_fatura_por_mes(
            self,
            credit_card: dict,
            invoice_year: int,
            invoice_month: int,
            sort_mode: str = "categoria",
    ) -> dict:
        lancamentos = self.expense_repository.listar_lancamentos_por_fatura(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
            sort_mode=sort_mode,
        )

        rows = self._montar_rows_tabela(
            lancamentos=lancamentos,
            agrupar_por_categoria=sort_mode == "categoria",
        )

        total_fatura_cents = sum(
            lancamento["effective_amount_cents"]
            for lancamento in lancamentos
        )

        total_ajustes_cents = self.adjustment_repository.somar_ajustes_fatura(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        valor_a_pagar_cents = total_fatura_cents + total_ajustes_cents

        return {
            "invoice_year": invoice_year,
            "invoice_month": invoice_month,
            "total_fatura_cents": total_fatura_cents,
            "total_ajustes_cents": total_ajustes_cents,
            "valor_a_pagar_cents": valor_a_pagar_cents,
            "total_lancamentos": len(lancamentos),
            "rows": rows,
        }

    def _montar_rows_tabela(
            self,
            lancamentos: list[dict],
            agrupar_por_categoria: bool = True,
    ) -> list[dict]:

        rows = []
        categoria_atual = None
        grupo_atual = None

        for lancamento in lancamentos:
            categoria = lancamento["category_name"] or "Sem categoria"
            cor = lancamento["category_color"] or "#6d28d9"

            if agrupar_por_categoria and categoria != categoria_atual:
                categoria_atual = categoria

                grupo_atual = {
                    "type": "group",
                    "name": categoria,
                    "icon": "■",
                    "count": "0 itens",
                    "total": self._formatar_moeda(0),
                    "total_cents": 0,
                    "items_count": 0,
                    "color": cor,
                    "background": "#f8fafc",
                }

                rows.append(grupo_atual)

            valor_parcela = lancamento["effective_amount_cents"]
            parcela_atual = lancamento["installment_number"]
            total_parcelas = lancamento["installment_total"]

            if grupo_atual is not None:
                grupo_atual["items_count"] += 1
                grupo_atual["total_cents"] += valor_parcela
                grupo_atual["count"] = (
                    f"{grupo_atual['items_count']} item"
                    if grupo_atual["items_count"] == 1
                    else f"{grupo_atual['items_count']} itens"
                )
                grupo_atual["total"] = self._formatar_moeda(
                    grupo_atual["total_cents"]
                )

            if total_parcelas > 1:
                parcelas_restantes = total_parcelas - parcela_atual + 1
                valor_restante = valor_parcela * parcelas_restantes
                texto_restante = self._formatar_moeda(valor_restante)
                texto_parcela = f"{parcela_atual:02d}/{total_parcelas:02d}"
            else:
                texto_restante = "-"
                texto_parcela = "-"

            rows.append(
                {
                    "type": "expense",
                    "expense_id": lancamento["expense_id"],
                    "amount_cents": valor_parcela,
                    "category_id": lancamento["category_id"],
                    "installment_number": lancamento["installment_number"],
                    "installment_total": lancamento["installment_total"],
                    "installment_group_id": lancamento["installment_group_id"],
                    "subcategory": lancamento.get("subcategory"),
                    "notes": lancamento.get("notes"),
                    "date": self._formatar_data_curta(
                        lancamento["effective_purchase_date"]
                    ),
                    "description": lancamento["effective_description"],
                    "category": categoria,
                    "category_color": cor,
                    "installment": texto_parcela,
                    "remaining": texto_restante,
                    "amount": self._formatar_moeda(valor_parcela),
                    "is_last_installment": total_parcelas > 1 and parcela_atual == total_parcelas,
                }
            )

        return rows

    def formatar_moeda(
            self,
            amount_cents: int,
    ) -> str:
        return self._formatar_moeda(amount_cents)

    def montar_cards_resumo_fatura(
            self,
            credit_card: dict,
            invoice_data: dict,
    ) -> list[dict]:
        hoje = date.today()

        current_invoice_year, current_invoice_month = (
            self.invoice_service.calcular_mes_fatura(
                purchase_date=hoje,
                closing_day=credit_card["closing_day"],
            )
        )

        total_fatura_atual_cents = self.expense_repository.somar_fatura(
            credit_card_id=credit_card["id"],
            invoice_year=current_invoice_year,
            invoice_month=current_invoice_month,
        )

        total_ajustes_atual_cents = (
            self.adjustment_repository.somar_ajustes_fatura(
                credit_card_id=credit_card["id"],
                invoice_year=current_invoice_year,
                invoice_month=current_invoice_month,
            )
        )

        valor_a_pagar_atual_cents = (
            total_fatura_atual_cents + total_ajustes_atual_cents
        )

        total_faturas_futuras_cents = (
            self.expense_repository.somar_faturas_futuras(
                credit_card_id=credit_card["id"],
                invoice_year=current_invoice_year,
                invoice_month=current_invoice_month,
            )
        )

        limite_total_cents = credit_card["limit_amount_cents"]

        limite_disponivel_cents = (
            limite_total_cents
            - valor_a_pagar_atual_cents
            - total_faturas_futuras_cents
        )

        return [
            {
                "icon": "📅",
                "title": "Fatura",
                "value": f"{invoice_data['invoice_month']:02d}/{invoice_data['invoice_year']}",
                "subtitle": "Mês selecionado",
            },
            {
                "icon": "💳",
                "title": "Valor Total",
                "value": self._formatar_moeda(
                    invoice_data["total_fatura_cents"]
                ),
                "subtitle": "Total da fatura exibida",
            },
            {
                "icon": "🧾",
                "title": "Valor a Pagar",
                "value": self._formatar_moeda(
                    invoice_data["valor_a_pagar_cents"]
                ),
                "subtitle": "Após pagamentos e créditos",
            },
            {
                "icon": "🕘",
                "title": "Próximas Faturas",
                "value": self._formatar_moeda(
                    total_faturas_futuras_cents
                ),
                "subtitle": "Parcelas e lançamentos futuros",
            },
            {
                "icon": "👛",
                "title": "Limite Disponível",
                "value": self._formatar_moeda(
                    limite_disponivel_cents
                ),
                "subtitle": f"de {self._formatar_moeda(limite_total_cents)}",
            },
        ]

    def reprocessar_faturas_cartao(
            self,
            credit_card: dict,
    ) -> int:
        return self.invoice_service.reprocessar_faturas_cartao(
            credit_card=credit_card,
            expense_repository=self.expense_repository,
            invoice_repository=self.invoice_repository,
        )

    def _formatar_moeda(
            self,
            amount_cents: int,
    ) -> str:

        valor = amount_cents / 100

        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def _formatar_data_curta(
            self,
            data_iso: str,
    ) -> str:

        ano, mes, dia = data_iso.split("-")

        return f"{dia}/{mes}"

    def carregar_diagnostico_parcelamento(
            self,
            expense_id: int,
    ) -> dict | None:

        lancamento = self.expense_repository.buscar_por_id(
            expense_id
        )

        if lancamento is None:
            return None

        installment_group_id = lancamento.get(
            "installment_group_id"
        )

        if not installment_group_id:
            return None

        parcelas = (
            self.expense_repository
            .listar_diagnostico_parcelas_grupo(
                installment_group_id=installment_group_id
            )
        )

        return {
            "installment_group_id": installment_group_id,
            "selected_expense_id": expense_id,
            "parcelas": parcelas,
        }

    def atualizar_categoria_lancamento(
            self,
            expense_id: int,
            category_id: int,
    ) -> None:
        expense_repository = CreditCardExpenseRepository(
            self.username
        )

        expense_repository.atualizar_categoria(
            expense_id=expense_id,
            category_id=category_id,
        )

    def atualizar_lancamento(
            self,
            credit_card: dict,
            expense_id: int,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            subcategory: str | None = None,
            notes: str | None = None,
    ) -> None:
        lancamento_atual = self.expense_repository.buscar_por_id(
            expense_id
        )

        if (
                lancamento_atual
                and lancamento_atual.get("installment_group_id")
        ):
            self._atualizar_grupo_parcelado_por_edicao(
                credit_card=credit_card,
                lancamento_base=lancamento_atual,
                category_id=category_id,
                effective_description=effective_description,
                effective_purchase_date=effective_purchase_date,
                effective_amount_cents=effective_amount_cents,
                subcategory=subcategory,
                notes=notes,
            )
            return

        purchase_date = date.fromisoformat(effective_purchase_date)

        invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
            purchase_date=purchase_date,
            closing_day=credit_card["closing_day"],
        )

        closing_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["closing_day"],
        )

        due_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["due_day"],
        )

        invoice = self.invoice_repository.buscar_por_cartao_mes(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        if invoice is None:
            invoice_id = self.invoice_repository.criar_fatura(
                credit_card_id=credit_card["id"],
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                closing_date=closing_date.isoformat(),
                due_date=due_date.isoformat(),
            )
        else:
            invoice_id = invoice["id"]

        self.expense_repository.atualizar_lancamento(
            expense_id=expense_id,
            invoice_id=invoice_id,
            category_id=category_id,
            effective_description=effective_description,
            effective_purchase_date=effective_purchase_date,
            billing_date=closing_date.isoformat(),
            effective_amount_cents=effective_amount_cents,
            subcategory=subcategory,
            notes=notes,
        )

    def _atualizar_grupo_parcelado_por_edicao(
            self,
            credit_card: dict,
            lancamento_base: dict,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            subcategory: str | None = None,
            notes: str | None = None,
    ) -> None:
        installment_group_id = lancamento_base["installment_group_id"]

        parcelas = self.expense_repository.listar_parcelas_grupo(
            installment_group_id=installment_group_id,
        )

        if not parcelas:
            return

        for parcela in parcelas:
            self.expense_repository.atualizar_lancamento(
                expense_id=parcela["id"],
                invoice_id=parcela["invoice_id"],
                category_id=category_id,
                effective_description=effective_description,
                effective_purchase_date=parcela["effective_purchase_date"],
                billing_date=parcela["billing_date"],
                effective_amount_cents=effective_amount_cents,
                subcategory=subcategory,
                notes=notes,
            )

    def criar_lancamento_manual(
            self,
            credit_card: dict,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            subcategory: str | None = None,
            notes: str | None = None,
            installment_number: int = 1,
            installment_total: int = 1,
    ) -> int:
        if installment_total <= 1:
            return self._criar_lancamento_unico(
                credit_card=credit_card,
                category_id=category_id,
                effective_description=effective_description,
                effective_purchase_date=effective_purchase_date,
                effective_amount_cents=effective_amount_cents,
                subcategory=subcategory,
                notes=notes,
            )

        return self._criar_lancamento_parcelado(
            credit_card=credit_card,
            category_id=category_id,
            effective_description=effective_description,
            effective_purchase_date=effective_purchase_date,
            effective_amount_cents=effective_amount_cents,
            subcategory=subcategory,
            notes=notes,
            installment_number=installment_number,
            installment_total=installment_total,
        )

    def _criar_lancamento_unico(
            self,
            credit_card: dict,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            subcategory: str | None = None,
            notes: str | None = None,
    ) -> int:
        invoice_id, closing_date = self._obter_ou_criar_fatura_por_data(
            credit_card=credit_card,
            purchase_date=date.fromisoformat(effective_purchase_date),
        )

        return self.expense_repository.criar_lancamento(
            credit_card_id=credit_card["id"],
            invoice_id=invoice_id,
            category_id=category_id,
            effective_description=effective_description,
            effective_purchase_date=effective_purchase_date,
            billing_date=closing_date.isoformat(),
            installment_number=1,
            installment_total=1,
            effective_amount_cents=effective_amount_cents,
            subcategory=subcategory,
            notes=notes,
            original_description=effective_description,
            original_purchase_date=effective_purchase_date,
            original_amount_cents=effective_amount_cents,
            source_type="manual",
            source_reference=None,
        )

    def criar_ou_completar_parcelamento(
            self,
            credit_card: dict,
            category_id: int,
            effective_description: str,
            parcela_atual_data: date,
            effective_amount_cents: int,
            installment_number: int,
            installment_total: int,
            subcategory: str | None = None,
            notes: str | None = None,
            source_type: str = "manual",
            source_reference: str | None = None,
    ) -> str:
        installment_group_id = (
            source_reference
            or self.gerar_installment_group_id(
                credit_card_id=credit_card["id"],
                effective_description=effective_description,
                effective_amount_cents=effective_amount_cents,
                installment_number=installment_number,
                installment_total=installment_total,
                parcela_atual_data=parcela_atual_data,
            )
        )
        for numero_parcela in range(1, installment_total + 1):
            deslocamento_meses = numero_parcela - installment_number

            data_parcela = self._somar_meses(
                parcela_atual_data,
                deslocamento_meses,
            )

            existe = (
                self.expense_repository.contar_lancamentos_por_assinatura(
                    credit_card_id=credit_card["id"],
                    original_description=effective_description,
                    original_purchase_date=data_parcela.isoformat(),
                    original_amount_cents=effective_amount_cents,
                    installment_number=numero_parcela,
                    installment_total=installment_total,
                )
            )

            if existe:
                continue

            invoice_id, closing_date = self._obter_ou_criar_fatura_por_data(
                credit_card=credit_card,
                purchase_date=data_parcela,
            )

            self.expense_repository.criar_lancamento(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                category_id=category_id,
                effective_description=effective_description,
                effective_purchase_date=data_parcela.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=numero_parcela,
                installment_total=installment_total,
                installment_group_id=installment_group_id,
                effective_amount_cents=effective_amount_cents,
                subcategory=subcategory,
                notes=notes if numero_parcela == installment_number else None,
                original_description=effective_description,
                original_purchase_date=parcela_atual_data.isoformat(),
                original_amount_cents=effective_amount_cents,
                source_type=source_type,
                source_reference=source_reference,
            )

        return installment_group_id

    def _criar_lancamento_parcelado(
            self,
            credit_card: dict,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
            subcategory: str | None,
            notes: str | None,
            installment_number: int,
            installment_total: int,
    ) -> int:

        if installment_number < 1:
            raise ValueError(
                "A parcela atual não pode ser menor que 1."
            )

        if (
                installment_total
                < installment_number
        ):
            raise ValueError(
                (
                    "O total de parcelas não pode "
                    "ser menor que a parcela atual."
                )
            )

        parcela_atual_data = (
            date.fromisoformat(
                effective_purchase_date
            )
        )

        installment_group_id = (
            self.criar_ou_completar_parcelamento(
                credit_card=credit_card,
                category_id=category_id,
                effective_description=(
                    effective_description
                ),
                parcela_atual_data=(
                    parcela_atual_data
                ),
                effective_amount_cents=(
                    effective_amount_cents
                ),
                installment_number=(
                    installment_number
                ),
                installment_total=(
                    installment_total
                ),
                subcategory=subcategory,
                notes=notes,
                source_type="manual",
            )
        )

        parcela = (
            self.expense_repository
            .buscar_parcela_grupo(
                installment_group_id=(
                    installment_group_id
                ),
                installment_number=(
                    installment_number
                ),
            )
        )

        if parcela is None:
            raise ValueError(
                (
                    "A parcela criada não pôde "
                    "ser localizada."
                )
            )

        return int(
            parcela["id"]
        )

    def _obter_ou_criar_fatura_por_data(
            self,
            credit_card: dict,
            purchase_date: date,
    ) -> tuple[int, date]:
        invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
            purchase_date=purchase_date,
            closing_day=credit_card["closing_day"],
        )

        closing_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["closing_day"],
        )

        due_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["due_day"],
        )

        invoice = self.invoice_repository.buscar_por_cartao_mes(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        if invoice is None:
            invoice_id = self.invoice_repository.criar_fatura(
                credit_card_id=credit_card["id"],
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                closing_date=closing_date.isoformat(),
                due_date=due_date.isoformat(),
            )
        else:
            invoice_id = invoice["id"]

        return invoice_id, closing_date

    def gerar_installment_group_id(
            self,
            credit_card_id: int,
            effective_description: str,
            effective_amount_cents: int,
            installment_number: int,
            installment_total: int,
            parcela_atual_data: date,
    ) -> str:
        primeira_parcela_data = self._somar_meses(
            parcela_atual_data,
            -(installment_number - 1),
        )

        descricao_normalizada = (
            effective_description
            .strip()
            .lower()
        )

        competencia_primeira = (
            primeira_parcela_data.strftime("%Y-%m")
        )

        return (
            f"{credit_card_id}|"
            f"{descricao_normalizada}|"
            f"{effective_amount_cents}|"
            f"{installment_total}|"
            f"{competencia_primeira}"
        )

    def reconciliar_parcelamentos_cartao(
            self,
            credit_card: dict,
            invoice_year: int,
            invoice_month: int,
    ) -> None:

        grupos = self.expense_repository.listar_grupos_parcelados(
            credit_card_id=credit_card["id"],
        )

        for installment_group_id in grupos:
            self._reconciliar_grupo_parcelado(
                credit_card=credit_card,
                installment_group_id=installment_group_id,
                reference_invoice_year=invoice_year,
                reference_invoice_month=invoice_month,
            )

    def _reconciliar_grupo_parcelado(
            self,
            credit_card: dict,
            installment_group_id: str,
    ) -> None:

        parcelas = self.expense_repository.listar_parcelas_grupo(
            installment_group_id=installment_group_id,
        )

        if not parcelas:
            return

        parcelas_reais = [
            parcela
            for parcela in parcelas
            if parcela["source_type"] != "projected_installment"
        ]

        if not parcelas_reais:
            return

        installment_total = max(
            parcela["installment_total"]
            for parcela in parcelas_reais
        )

        if installment_total <= 1:
            return

        maior_parcela_real = max(
            parcelas_reais,
            key=lambda parcela: parcela["installment_number"],
        )

        maior_numero_real = maior_parcela_real["installment_number"]

        # =========================================================
        # O REAL É VERDADE ABSOLUTA
        #
        # Qualquer projeção da parcela atual ou de parcelas
        # anteriores deixa de fazer sentido.
        # =========================================================

        for numero_parcela in range(1, maior_numero_real + 1):
            self.expense_repository.cancelar_projecoes_ativas_grupo_parcela(
                installment_group_id=installment_group_id,
                installment_number=numero_parcela,
            )

        # =========================================================
        # PARCELAMENTO TERMINOU
        # =========================================================

        if maior_numero_real >= installment_total:
            return

        # =========================================================
        # PROCURA UMA PROJEÇÃO FUTURA EXISTENTE
        #
        # Ela é nossa melhor referência da programação ORIGINAL.
        #
        # Isso é importante para antecipações:
        #
        # 7/10 -> setembro
        # 8/10 -> setembro (adiantada)
        #
        # A 9/10 já projetada para novembro NÃO deve virar outubro
        # só porque a 8/10 caiu antecipadamente em setembro.
        # =========================================================

        projecoes_futuras = [
            parcela
            for parcela in parcelas
            if (
                    parcela["source_type"] == "projected_installment"
                    and parcela["status"] != "cancelled"
                    and parcela["installment_number"] > maior_numero_real
            )
        ]

        ancora_projecao = None

        if projecoes_futuras:
            ancora_projecao = min(
                projecoes_futuras,
                key=lambda parcela: parcela["installment_number"],
            )

        # =========================================================
        # BASE VISUAL / FINANCEIRA
        #
        # Categoria, descrição e valor vêm da última parcela real.
        # =========================================================

        base = maior_parcela_real

        for numero_parcela in range(
                maior_numero_real + 1,
                installment_total + 1,
        ):

            # -----------------------------------------------------
            # Se já existe projeção ativa desta parcela,
            # NÃO reconstruímos.
            #
            # Mantemos exatamente a competência prevista.
            # -----------------------------------------------------

            projecao_existente = (
                self.expense_repository
                .buscar_projecao_ativa_grupo_parcela(
                    installment_group_id=installment_group_id,
                    installment_number=numero_parcela,
                )
            )

            if projecao_existente is not None:
                continue

            # -----------------------------------------------------
            # Determinação da data prevista
            # -----------------------------------------------------

            if ancora_projecao is not None:

                data_ancora = date.fromisoformat(
                    ancora_projecao["effective_purchase_date"]
                )

                deslocamento = (
                        numero_parcela
                        - ancora_projecao["installment_number"]
                )

                effective_purchase_date = self._somar_meses(
                    data_ancora,
                    deslocamento,
                )

            else:

                # Não existe nenhuma projeção anterior para preservar.
                #
                # Isso normalmente acontece na primeira vez que o
                # parcelamento entra no sistema.
                #
                # Nesse caso começamos a projeção a partir da
                # última parcela real conhecida.

                data_ultima_real = date.fromisoformat(
                    maior_parcela_real["effective_purchase_date"]
                )

                deslocamento = (
                        numero_parcela
                        - maior_numero_real
                )

                effective_purchase_date = self._somar_meses(
                    data_ultima_real,
                    deslocamento,
                )

            invoice_id, closing_date = (
                self._obter_ou_criar_fatura_por_data(
                    credit_card=credit_card,
                    purchase_date=effective_purchase_date,
                )
            )

            self.expense_repository.criar_lancamento(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                category_id=base["category_id"],
                effective_description=base["effective_description"],
                effective_purchase_date=effective_purchase_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=numero_parcela,
                installment_total=installment_total,
                installment_group_id=installment_group_id,
                effective_amount_cents=base["effective_amount_cents"],
                import_batch_id=None,
                created_by="reconcile_installment",
                notes="Parcela projetada automaticamente",
                original_description=base["original_description"],
                original_purchase_date=base["original_purchase_date"],
                original_amount_cents=base["original_amount_cents"],
                source_type="projected_installment",
                source_reference=installment_group_id,
            )

    def _obter_ou_criar_fatura_por_mes(
            self,
            credit_card: dict,
            invoice_year: int,
            invoice_month: int,
    ) -> int:
        closing_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["closing_day"],
        )

        due_date = self.invoice_service.montar_data_segura(
            invoice_year,
            invoice_month,
            credit_card["due_day"],
        )

        invoice = self.invoice_repository.buscar_por_cartao_mes(
            credit_card_id=credit_card["id"],
            invoice_year=invoice_year,
            invoice_month=invoice_month,
        )

        if invoice is None:
            return self.invoice_repository.criar_fatura(
                credit_card_id=credit_card["id"],
                invoice_year=invoice_year,
                invoice_month=invoice_month,
                closing_date=closing_date.isoformat(),
                due_date=due_date.isoformat(),
            )

        return invoice["id"]

    def analisar_exclusao_lancamento(
            self,
            credit_card: dict,
            expense_id: int,
    ) -> dict:
        lancamento = self.expense_repository.buscar_por_id(
            expense_id
        )

        if lancamento is None:
            raise ValueError(
                "Lançamento não encontrado."
            )

        parcelado = (
            int(lancamento["installment_total"] or 1) > 1
            and lancamento.get("installment_group_id") is not None
        )

        adiantada = False

        if parcelado:
            adiantada = self._parcela_esta_adiantada(
                credit_card=credit_card,
                lancamento=lancamento,
            )

        return {
            "expense_id": lancamento["id"],
            "parcelado": parcelado,
            "adiantada": adiantada,
            "installment_number": int(
                lancamento["installment_number"] or 1
            ),
            "installment_total": int(
                lancamento["installment_total"] or 1
            ),
            "installment_group_id": lancamento.get(
                "installment_group_id"
            ),
        }

    def excluir_lancamento(
            self,
            credit_card: dict,
            expense_id: int,
            modo: str,
            reference_invoice_year: int,
            reference_invoice_month: int,
    ) -> None:
        lancamento = self.expense_repository.buscar_por_id(
            expense_id
        )

        if lancamento is None:
            raise ValueError(
                "Lançamento não encontrado."
            )

        modos_validos = {
            "unico",
            "deste_em_diante",
            "parcelamento_inteiro",
        }

        if modo not in modos_validos:
            raise ValueError(
                f"Modo de exclusão inválido: {modo}"
            )

        installment_total = int(
            lancamento["installment_total"] or 1
        )

        installment_group_id = lancamento.get(
            "installment_group_id"
        )

        parcelado = (
            installment_total > 1
            and installment_group_id is not None
        )

        if not parcelado:
            self.expense_repository.cancelar_lancamento(
                expense_id=expense_id
            )
            return

        if self._parcela_esta_adiantada(
                credit_card=credit_card,
                lancamento=lancamento,
        ):
            raise ValueError(
                "Para apagar parcelas adiantadas, primeiro é necessário "
                "reajustar as parcelas extras dessa fatura para seu mês original."
            )

        if modo == "unico":
            self.expense_repository.cancelar_lancamento(
                expense_id=expense_id
            )
            return

        if modo == "parcelamento_inteiro":
            self.expense_repository.cancelar_parcelamento_inteiro(
                installment_group_id=installment_group_id
            )
            return

        if modo == "deste_em_diante":
            self.expense_repository.cancelar_parcelas_a_partir_de(
                installment_group_id=installment_group_id,
                installment_number=int(
                    lancamento["installment_number"]
                ),
                invoice_year=reference_invoice_year,
                invoice_month=reference_invoice_month,
            )
            return

    def _parcela_esta_adiantada(
            self,
            credit_card: dict,
            lancamento: dict,
    ) -> bool:
        installment_group_id = lancamento.get(
            "installment_group_id"
        )

        if not installment_group_id:
            return False

        parcelas = self.expense_repository.listar_parcelas_grupo(
            installment_group_id=installment_group_id
        )

        parcelas_reais = [
            parcela
            for parcela in parcelas
            if parcela["source_type"] != "projected_installment"
        ]

        if not parcelas_reais:
            return False

        parcela_base = min(
            parcelas_reais,
            key=lambda parcela: int(
                parcela["installment_number"]
            ),
        )

        numero_base = int(
            parcela_base["installment_number"]
        )

        data_base = date.fromisoformat(
            parcela_base["effective_purchase_date"]
        )

        data_primeira_parcela = self._somar_meses(
            data_base,
            -(numero_base - 1),
        )

        numero_parcela = int(
            lancamento["installment_number"]
        )

        data_esperada = self._somar_meses(
            data_primeira_parcela,
            numero_parcela - 1,
        )

        expected_year, expected_month = (
            self.invoice_service.calcular_mes_fatura(
                purchase_date=data_esperada,
                closing_day=credit_card["closing_day"],
            )
        )

        competencia_atual = None

        for parcela in parcelas:
            if parcela["id"] == lancamento["id"]:
                competencia_atual = (
                    int(parcela["invoice_year"]),
                    int(parcela["invoice_month"]),
                )
                break

        if competencia_atual is None:
            return False

        competencia_esperada = (
            expected_year,
            expected_month,
        )

        return competencia_atual < competencia_esperada

    def _somar_meses_competencia(
            self,
            year: int,
            month: int,
            deslocamento: int,
    ) -> tuple[int, int]:
        mes_total = month - 1 + deslocamento
        novo_ano = year + mes_total // 12
        novo_mes = mes_total % 12 + 1

        return novo_ano, novo_mes

    def _somar_meses(
            self,
            data_base: date,
            meses: int,
    ) -> date:
        mes_total = data_base.month - 1 + meses
        ano = data_base.year + mes_total // 12
        mes = mes_total % 12 + 1

        return self.invoice_service.montar_data_segura(
            ano,
            mes,
            data_base.day,
        )