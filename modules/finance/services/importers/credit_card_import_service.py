from collections import Counter, defaultdict
from modules.finance.repositories.credit_card_invoice_repository import (
    CreditCardInvoiceRepository,
)
from modules.finance.repositories.credit_card_expense_repository import (
    CreditCardExpenseRepository,
)
from modules.finance.services.credit_card_invoice_service import (
    CreditCardInvoiceService,
)
from modules.finance.services.importers.credit_card_csv_import_handler import (
    CreditCardCsvImportHandler,
)
from modules.finance.services.importers.credit_card_csv_converters import (
    ImportedCreditCardExpense,
)

from modules.finance.repositories.credit_card_invoice_adjustment_repository import (
    CreditCardInvoiceAdjustmentRepository,
)

from modules.finance.services.credit_card_detail_service import (
    CreditCardDetailService,
)

class CreditCardImportService:
    def __init__(
            self,
            username: str,
    ) -> None:

        self.csv_handler = CreditCardCsvImportHandler()
        self.invoice_repository = CreditCardInvoiceRepository(username)
        self.expense_repository = CreditCardExpenseRepository(username)
        self.invoice_service = CreditCardInvoiceService()
        self.adjustment_repository = CreditCardInvoiceAdjustmentRepository(username)
        self.detail_service = CreditCardDetailService(username)

    def importar_preview(
            self,
            csv_path: str,
    ) -> list[ImportedCreditCardExpense]:

        return self.csv_handler.import_preview(
            csv_path
        )

    def _gerar_assinatura_importacao(
            self,
            expense: ImportedCreditCardExpense,
    ) -> tuple:
        return (
            expense.raw_title,
            expense.purchase_date.isoformat(),
            expense.amount_cents,
            expense.installment_number,
            expense.installment_total,
        )

    def _gerar_chave_familia_base(
            self,
            credit_card: dict,
            expense: ImportedCreditCardExpense,
    ) -> str:
        return self.detail_service.gerar_installment_group_id(
            credit_card_id=credit_card["id"],
            effective_description=expense.description,
            effective_amount_cents=expense.amount_cents,
            installment_number=expense.installment_number,
            installment_total=expense.installment_total,
            parcela_atual_data=expense.purchase_date,
        )

    def _valores_proximos(
            self,
            valor_a: int,
            valor_b: int,
            tolerancia_centavos: int = 50,
    ) -> bool:
        return abs(valor_a - valor_b) <= tolerancia_centavos

    def _obter_ou_criar_fatura(
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

    def confirmar_importacao(
            self,
            credit_card: dict,
            expenses: list[ImportedCreditCardExpense],
            category_id: int = 1,
    ) -> int:

        total_salvo = 0

        total_por_assinatura = Counter(
            self._gerar_assinatura_importacao(expense)
            for expense in expenses
        )

        total_por_familia_base = Counter(
            self._gerar_chave_familia_base(
                credit_card=credit_card,
                expense=expense,
            )
            for expense in expenses
            if expense.installment_total > 1
        )

        ocorrencias_familia_agora = defaultdict(int)

        familias_antecipadas_por_assinatura = {}

        grupos_possiveis_antecipacao = defaultdict(list)

        for expense in expenses:
            if expense.installment_total <= 1:
                continue

            invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
                purchase_date=expense.purchase_date,
                closing_day=credit_card["closing_day"],
            )

            chave = (
                expense.description,
                expense.installment_total,
                invoice_year,
                invoice_month,
            )

            grupos_possiveis_antecipacao[chave].append(expense)

        for grupo_expenses in grupos_possiveis_antecipacao.values():
            if len(grupo_expenses) <= 1:
                continue

            clusters_por_valor = []

            for expense in grupo_expenses:
                cluster_encontrado = None

                for cluster in clusters_por_valor:
                    valor_referencia = cluster[0].amount_cents

                    if self._valores_proximos(
                            expense.amount_cents,
                            valor_referencia,
                    ):
                        cluster_encontrado = cluster
                        break

                if cluster_encontrado is None:
                    clusters_por_valor.append([expense])
                else:
                    cluster_encontrado.append(expense)

            for cluster in clusters_por_valor:
                if len(cluster) <= 1:
                    continue

                grupo_ordenado = sorted(
                    cluster,
                    key=lambda item: item.installment_number,
                )

                numeros_parcelas = [
                    item.installment_number
                    for item in grupo_ordenado
                ]

                parcelas_consecutivas = numeros_parcelas == list(
                    range(
                        min(numeros_parcelas),
                        max(numeros_parcelas) + 1,
                    )
                )

                if not parcelas_consecutivas:
                    continue

                menor_parcela = grupo_ordenado[0]

                familia_base = self._gerar_chave_familia_base(
                    credit_card=credit_card,
                    expense=menor_parcela,
                )

                for item in grupo_ordenado:
                    familias_antecipadas_por_assinatura[
                        self._gerar_assinatura_importacao(item)
                    ] = familia_base
                    
        ja_importados_agora = defaultdict(int)

        total_inicial_no_banco = {}

        for assinatura in total_por_assinatura:
            total_inicial_no_banco[assinatura] = (
                self.expense_repository.contar_lancamentos_por_assinatura(
                    credit_card_id=credit_card["id"],
                    original_description=assinatura[0],
                    original_purchase_date=assinatura[1],
                    original_amount_cents=assinatura[2],
                    installment_number=assinatura[3],
                    installment_total=assinatura[4],
                )
            )

        for expense in expenses:
            assinatura = self._gerar_assinatura_importacao(expense)

            if total_inicial_no_banco[assinatura] + ja_importados_agora[assinatura] >= total_por_assinatura[assinatura]:
                continue

            invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
                purchase_date=expense.purchase_date,
                closing_day=credit_card["closing_day"],
            )

            invoice_id = self._obter_ou_criar_fatura(
                credit_card=credit_card,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            closing_date = self.invoice_service.montar_data_segura(
                invoice_year,
                invoice_month,
                credit_card["closing_day"],
            )

            installment_group_id = None

            if expense.installment_total > 1:
                assinatura = self._gerar_assinatura_importacao(expense)

                familia_base = familias_antecipadas_por_assinatura.get(
                    assinatura
                )

                if familia_base is None:
                    familia_base = self._gerar_chave_familia_base(
                        credit_card=credit_card,
                        expense=expense,
                    )

                if total_por_familia_base[familia_base] > 1:
                    ocorrencias_familia_agora[familia_base] += 1

                    installment_group_id = (
                        f"{familia_base}|occurrence:"
                        f"{ocorrencias_familia_agora[familia_base]}"
                    )
                else:
                    installment_group_id = familia_base

            self.expense_repository.criar_lancamento(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                category_id=category_id,
                effective_description=expense.description,
                effective_purchase_date=expense.purchase_date.isoformat(),
                billing_date=closing_date.isoformat(),
                installment_number=expense.installment_number,
                installment_total=expense.installment_total,
                effective_amount_cents=expense.amount_cents,
                installment_group_id=installment_group_id,
                notes=f"Importado via CSV - {expense.source}",
                original_description=expense.raw_title,
                original_purchase_date=expense.purchase_date.isoformat(),
                original_amount_cents=expense.amount_cents,
                source_type=expense.source,
                source_reference=expense.raw_title,
            )

            ja_importados_agora[assinatura] += 1
            total_salvo += 1

        self.detail_service.reconciliar_parcelamentos_cartao(
            credit_card=credit_card,
        )

        return total_salvo

    def importar_ajustes_csv(
            self,
            credit_card: dict,
            csv_path: str,
            previous_payment_keys: set[tuple] | None = None,
    ) -> int:
        adjustments = self.csv_handler.import_adjustments(csv_path)

        if previous_payment_keys is None:
            previous_payment_keys = set()

        total_salvo = 0

        for adjustment in adjustments:
            invoice_year, invoice_month = self.invoice_service.calcular_mes_fatura(
                purchase_date=adjustment.adjustment_date,
                closing_day=credit_card["closing_day"],
            )

            adjustment_key = (
                adjustment.adjustment_date.isoformat(),
                adjustment.description,
                adjustment.amount_cents,
                adjustment.raw_title,
            )

            adjustment_type = adjustment.adjustment_type

            if adjustment_key in previous_payment_keys:
                adjustment_type = "previous_invoice_payment"

            invoice_id = self._obter_ou_criar_fatura(
                credit_card=credit_card,
                invoice_year=invoice_year,
                invoice_month=invoice_month,
            )

            if self.adjustment_repository.existe_ajuste_importado(
                    credit_card_id=credit_card["id"],
                    description=adjustment.description,
                    adjustment_date=adjustment.adjustment_date.isoformat(),
                    amount_cents=adjustment.amount_cents,
                    source_type=adjustment.source,
                    source_reference=adjustment.raw_title,
            ):
                continue

            self.adjustment_repository.criar_ajuste(
                credit_card_id=credit_card["id"],
                invoice_id=invoice_id,
                adjustment_type=adjustment_type,
                description=adjustment.description,
                adjustment_date=adjustment.adjustment_date.isoformat(),
                amount_cents=adjustment.amount_cents,
                source_type=adjustment.source,
                source_reference=adjustment.raw_title,
                notes=f"Ajuste importado via CSV - {adjustment.source}",
            )

            total_salvo += 1

        return total_salvo