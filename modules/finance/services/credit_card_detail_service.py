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

        for lancamento in lancamentos:
            categoria = lancamento["category_name"] or "Sem categoria"
            cor = lancamento["category_color"] or "#6d28d9"

            if agrupar_por_categoria and categoria != categoria_atual:
                categoria_atual = categoria

                rows.append(
                    {
                        "type": "group",
                        "name": categoria,
                        "icon": "■",
                        "count": "",
                        "total": "",
                        "color": cor,
                        "background": "#f8fafc",
                    }
                )

            valor_parcela = lancamento["effective_amount_cents"]
            parcela_atual = lancamento["installment_number"]
            total_parcelas = lancamento["installment_total"]

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
                    "category_id": lancamento["category_id"],
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
            notes: str | None = None,
    ) -> None:
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
            effective_amount_cents=effective_amount_cents,
            notes=notes,
        )

    def criar_lancamento_manual(
            self,
            credit_card: dict,
            category_id: int,
            effective_description: str,
            effective_purchase_date: str,
            effective_amount_cents: int,
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
                notes=notes,
            )

        return self._criar_lancamento_parcelado(
            credit_card=credit_card,
            category_id=category_id,
            effective_description=effective_description,
            effective_purchase_date=effective_purchase_date,
            effective_amount_cents=effective_amount_cents,
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
            notes: str | None,
            installment_number: int,
            installment_total: int,
    ) -> int:
        if installment_number < 1:
            raise ValueError(
                "A parcela atual não pode ser menor que 1."
            )

        if installment_total < installment_number:
            raise ValueError(
                "O total de parcelas não pode ser menor que a parcela atual."
            )

        parcela_atual_data = date.fromisoformat(
            effective_purchase_date
        )

        self.criar_ou_completar_parcelamento(
            credit_card=credit_card,
            category_id=category_id,
            effective_description=effective_description,
            parcela_atual_data=parcela_atual_data,
            effective_amount_cents=effective_amount_cents,
            installment_number=installment_number,
            installment_total=installment_total,
            notes=notes,
            source_type="manual",
        )

        return 0

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
    ) -> None:

        self.expense_repository.cancelar_projecoes_parcelamento_cartao(
            credit_card_id=credit_card["id"],
        )

        grupos = self.expense_repository.listar_grupos_parcelados(
            credit_card_id=credit_card["id"],
        )

        for installment_group_id in grupos:
            self._reconciliar_grupo_parcelado(
                credit_card=credit_card,
                installment_group_id=installment_group_id,
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

        installment_total = max(
            parcela["installment_total"]
            for parcela in parcelas
        )

        if installment_total <= 1:
            return

        parcelas_por_numero = {
            parcela["installment_number"]: parcela
            for parcela in parcelas
        }

        menor_parcela = min(
            parcelas,
            key=lambda parcela: parcela["installment_number"],
        )

        primeiro_mes_year, primeiro_mes_month = self._somar_meses_competencia(
            year=menor_parcela["invoice_year"],
            month=menor_parcela["invoice_month"],
            deslocamento=-(menor_parcela["installment_number"] - 1),
        )

        quantidade_por_competencia = {}

        for parcela in parcelas:
            competencia = (
                parcela["invoice_year"],
                parcela["invoice_month"],
            )

            quantidade_por_competencia[competencia] = (
                quantidade_por_competencia.get(competencia, 0) + 1
            )

        competencias_planejadas = []
        competencia_atual = (
            primeiro_mes_year,
            primeiro_mes_month,
        )

        while len(competencias_planejadas) < installment_total:
            quantidade_no_mes = max(
                quantidade_por_competencia.get(competencia_atual, 0),
                1,
            )

            for _ in range(quantidade_no_mes):
                competencias_planejadas.append(competencia_atual)

                if len(competencias_planejadas) >= installment_total:
                    break

            competencia_atual = self._somar_meses_competencia(
                year=competencia_atual[0],
                month=competencia_atual[1],
                deslocamento=1,
            )

        base = parcelas[0]

        for numero_parcela in range(1, installment_total + 1):
            invoice_year, invoice_month = competencias_planejadas[
                numero_parcela - 1
            ]

            closing_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                credit_card["closing_day"],
            )

            invoice_id = self._obter_ou_criar_fatura_por_mes(
                credit_card=credit_card,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            parcela_existente = parcelas_por_numero.get(numero_parcela)

            if parcela_existente:
                if parcela_existente["source_type"] == "projected_installment":
                    self.expense_repository.atualizar_parcela(
                        expense_id=parcela_existente["id"],
                        invoice_id=invoice_id,
                        effective_purchase_date=closing_date.isoformat(),
                    )

                continue

            self.expense_repository.criar_lancamento(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                category_id=base["category_id"],
                effective_description=base["effective_description"],
                effective_purchase_date=closing_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=numero_parcela,
                installment_total=installment_total,
                installment_group_id=installment_group_id,
                effective_amount_cents=base["effective_amount_cents"],
                notes="Parcela projetada automaticamente",
                original_description=base["original_description"],
                original_purchase_date=closing_date.isoformat(),
                original_amount_cents=base["effective_amount_cents"],
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