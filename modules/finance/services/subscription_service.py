from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

from modules.finance.repositories.balance_repository import BalanceRepository
from modules.finance.repositories.credit_card_repository import CreditCardRepository
from modules.finance.repositories.subscription_repository import SubscriptionRepository
from modules.finance.repositories.credit_card_repository import CreditCardRepository
from modules.finance.repositories.credit_card_expense_repository import CreditCardExpenseRepository
from modules.finance.services.credit_card_detail_service import CreditCardDetailService

class SubscriptionService:
    VALID_PAYMENT_METHODS = {
        "bank_account",
        "credit_card",
        "pix",
    }

    def __init__(self, username: str) -> None:
        self.username = username
        self.repository = SubscriptionRepository(username)
        self.balance_repository = BalanceRepository(username)
        self.credit_card_repository = CreditCardRepository(username)
        self.credit_card_expense_repository = CreditCardExpenseRepository(username)
        self.credit_card_detail_service = (CreditCardDetailService(username))

    def criar_assinatura(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            payment_method: str,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            description: str | None = None,
            match_keywords: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> int:
        self._validar_dados_assinatura(
            name=name,
            amount_cents=amount_cents,
            charge_day=charge_day,
            payment_method=payment_method,
            account_id=account_id,
            credit_card_id=credit_card_id,
        )

        return self.repository.criar_assinatura(
            name=name.strip(),
            amount_cents=amount_cents,
            charge_day=charge_day,
            payment_method=payment_method,
            account_id=account_id,
            credit_card_id=credit_card_id,
            description=self._normalizar_texto_opcional(description),
            match_keywords=self._normalizar_texto_opcional(match_keywords),
            start_date=start_date,
            end_date=end_date,
            notes=self._normalizar_texto_opcional(notes),
        )

    def atualizar_assinatura(
            self,
            subscription_id: int,
            name: str,
            amount_cents: int,
            charge_day: int,
            payment_method: str,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            description: str | None = None,
            match_keywords: str | None = None,
            start_date: str | None = None,
            end_date: str | None = None,
            notes: str | None = None,
    ) -> None:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        self._validar_dados_assinatura(
            name=name,
            amount_cents=amount_cents,
            charge_day=charge_day,
            payment_method=payment_method,
            account_id=account_id,
            credit_card_id=credit_card_id,
        )

        self.repository.atualizar_assinatura(
            subscription_id=subscription_id,
            name=name.strip(),
            amount_cents=amount_cents,
            charge_day=charge_day,
            payment_method=payment_method,
            account_id=account_id,
            credit_card_id=credit_card_id,
            description=self._normalizar_texto_opcional(description),
            match_keywords=self._normalizar_texto_opcional(match_keywords),
            start_date=start_date,
            end_date=end_date,
            notes=self._normalizar_texto_opcional(notes),
        )

    def listar_assinaturas(
            self,
            include_inactive: bool = False,
    ) -> list[dict]:
        return self.repository.listar_assinaturas(
            include_inactive=include_inactive
        )

    def buscar_assinatura_por_id(
            self,
            subscription_id: int,
    ) -> dict | None:
        return self.repository.buscar_assinatura_por_id(
            subscription_id
        )

    def desativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:
        self.repository.desativar_assinatura(
            subscription_id
        )

    def reativar_assinatura(
            self,
            subscription_id: int,
    ) -> None:
        self.repository.reativar_assinatura(
            subscription_id
        )

    def arquivar_assinatura(
            self,
            subscription_id: int,
            archive_reason: str | None = None,
    ) -> None:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        self.repository.arquivar_assinatura(
            subscription_id=subscription_id,
            archive_reason=archive_reason,
        )

    def criar_ou_atualizar_excecao_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
            expected_charge_date: str | None = None,
            expected_payment_date: str | None = None,
            amount_cents: int | None = None,
            status: str = "active",
            notes: str | None = None,
    ) -> int:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        if not 1 <= reference_month <= 12:
            raise ValueError("Mês de referência inválido.")

        if reference_year < 2000:
            raise ValueError("Ano de referência inválido.")

        if amount_cents is not None and amount_cents < 0:
            raise ValueError("Valor da exceção não pode ser negativo.")

        if status not in {"active", "ignored", "cancelled"}:
            raise ValueError("Status de exceção inválido.")

        return self.repository.criar_ou_atualizar_override(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
            expected_charge_date=expected_charge_date,
            expected_payment_date=expected_payment_date,
            amount_cents=amount_cents,
            status=status,
            notes=self._normalizar_texto_opcional(notes),
        )

    def nao_cobrar_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
            notes: str | None = None,
    ) -> int:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        return self.repository.criar_ou_atualizar_override(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
            expected_charge_date=None,
            expected_payment_date=None,
            amount_cents=0,
            status="ignored",
            actual_charge_date=None,
            actual_amount_cents=0,
            resolved_at=date.today().isoformat(),
            resolution_type="ignored",
            matched_credit_card_expense_id=None,
            matched_balance_commitment_id=None,
            notes=notes or "Cobrança ignorada pelo usuário neste mês.",
        )

    def retomar_cobranca_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
    ) -> None:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        override = self.repository.buscar_override_mes(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
        )

        if override is None:
            return

        if override["status"] != "ignored":
            raise ValueError(
                "Apenas cobranças ignoradas podem ser retomadas."
            )

        self.repository.excluir_override_mes(
            subscription_id=subscription_id,
            reference_year=reference_year,
            reference_month=reference_month,
        )

    def montar_data_cobranca(
            self,
            year: int,
            month: int,
            charge_day: int,
    ) -> str:
        ultimo_dia = calendar.monthrange(
            year,
            month,
        )[1]

        dia = min(
            charge_day,
            ultimo_dia,
        )

        return date(
            year,
            month,
            dia,
        ).isoformat()

    def _validar_dados_assinatura(
            self,
            name: str,
            amount_cents: int,
            charge_day: int,
            payment_method: str,
            account_id: int | None,
            credit_card_id: int | None,
    ) -> None:
        if not name or not name.strip():
            raise ValueError("Informe o nome da assinatura.")

        if amount_cents <= 0:
            raise ValueError("O valor da assinatura precisa ser maior que zero.")

        if not 1 <= charge_day <= 31:
            raise ValueError("O dia de cobrança precisa estar entre 1 e 31.")

        if payment_method not in self.VALID_PAYMENT_METHODS:
            raise ValueError("Forma de pagamento inválida.")

        if payment_method in {"bank_account", "pix"} and account_id is None:
            raise ValueError(
                "Assinaturas em conta ou PIX precisam de uma conta vinculada."
            )

        if payment_method == "credit_card" and credit_card_id is None:
            raise ValueError(
                "Assinaturas no cartão precisam de um cartão vinculado."
            )

    def _normalizar_texto_opcional(
            self,
            value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    def listar_projecoes_periodo(
            self,
            start_date: str,
            end_date: str,
            account_id: int | None = None,
    ) -> list[dict]:

        inicio = date.fromisoformat(start_date)
        fim = date.fromisoformat(end_date)

        assinaturas = self.repository.listar_assinaturas(
            include_inactive=False
        )

        eventos = []

        cursor = date(
            inicio.year,
            inicio.month,
            1,
        )

        fim_cursor = date(
            fim.year,
            fim.month,
            1,
        )

        while cursor <= fim_cursor:
            for assinatura in assinaturas:
                evento = self._montar_projecao_assinatura_mes(
                    assinatura=assinatura,
                    year=cursor.year,
                    month=cursor.month,
                    start_date=start_date,
                    end_date=end_date,
                    account_id=account_id,
                )

                if evento is not None:
                    eventos.append(evento)

            cursor = cursor + relativedelta(months=1)

        eventos = self._agrupar_projecoes_cartao(eventos)

        eventos.sort(
            key=lambda evento: (
                evento["date"],
                evento["description"].lower(),
            )
        )

        return eventos

    def _montar_projecao_assinatura_mes(
            self,
            assinatura: dict,
            year: int,
            month: int,
            start_date: str,
            end_date: str,
            account_id: int | None = None,
    ) -> dict | None:

        override = self.repository.buscar_override_mes(
            subscription_id=assinatura["id"],
            reference_year=year,
            reference_month=month,
        )

        if override is not None:
            if override["status"] in {
                "ignored",
                "cancelled",
                "charged",
                "matched",
            }:
                return None

        if assinatura["start_date"] is not None:
            inicio_assinatura = date.fromisoformat(
                assinatura["start_date"]
            )

            if date(year, month, 1) < date(
                    inicio_assinatura.year,
                    inicio_assinatura.month,
                    1,
            ):
                return None

        if assinatura["end_date"] is not None:
            fim_assinatura = date.fromisoformat(
                assinatura["end_date"]
            )

            if date(year, month, 1) > date(
                    fim_assinatura.year,
                    fim_assinatura.month,
                    1,
            ):
                return None

        if (
                account_id is not None
                and assinatura["payment_method"] in {"bank_account", "pix"}
                and assinatura["account_id"] != account_id
        ):
            return None

        data_cobranca = self.montar_data_cobranca(
            year=year,
            month=month,
            charge_day=assinatura["charge_day"],
        )

        valor_cents = int(
            assinatura["amount_cents"] or 0
        )

        if assinatura["payment_method"] == "credit_card":
            if self._assinatura_ja_caiu_no_cartao(
                    assinatura=assinatura,
                    charge_date=data_cobranca,
                    amount_cents=valor_cents,
            ):
                return None

            data_evento = self._calcular_vencimento_cartao_para_assinatura(
                assinatura=assinatura,
                charge_date=data_cobranca,
            )

            if data_evento is None:
                return None

            account_id_evento = self._obter_account_id_cartao(
                assinatura["credit_card_id"]
            )

            if (
                    account_id is not None
                    and account_id_evento != account_id
            ):
                return None

            payment_type = "credit_card"
            description = f"Assinatura {assinatura['name']} — projeção cartão"

        else:
            data_evento = data_cobranca
            account_id_evento = assinatura["account_id"]
            payment_type = assinatura["payment_method"]
            description = f"Assinatura {assinatura['name']}"

        if not start_date <= data_evento <= end_date:
            return None

        return {
            "kind": "commitment",
            "date": data_evento,
            "description": description,
            "amount_cents": valor_cents,
            "status": "expected",
            "account_id": account_id_evento,
            "payment_type": payment_type,
            "credit_card_id": assinatura["credit_card_id"],
            "projection_type": "projected",
            "commitment_origin": "subscription_projection",
            "subscription_id": assinatura["id"],
        }

    def _obter_cartao_por_id(
            self,
            credit_card_id: int,
    ) -> dict | None:

        for cartao in self.credit_card_repository.listar_cartoes_ativos():
            if cartao["id"] == credit_card_id:
                return cartao

        return None

    def _obter_account_id_cartao(
            self,
            credit_card_id: int | None,
    ) -> int | None:

        if credit_card_id is None:
            return None

        cartao = self._obter_cartao_por_id(
            credit_card_id
        )

        if cartao is None:
            return None

        return cartao["account_id"]

    def _calcular_vencimento_cartao_para_assinatura(
            self,
            assinatura: dict,
            charge_date: str,
    ) -> str | None:

        credit_card_id = assinatura["credit_card_id"]

        if credit_card_id is None:
            return None

        cartao = self._obter_cartao_por_id(
            credit_card_id
        )

        if cartao is None:
            return None

        data_cobranca = date.fromisoformat(
            charge_date
        )

        if data_cobranca.day < cartao["closing_day"]:
            invoice_year = data_cobranca.year
            invoice_month = data_cobranca.month
        else:
            proximo_mes = data_cobranca + relativedelta(months=1)
            invoice_year = proximo_mes.year
            invoice_month = proximo_mes.month

        ultimo_dia = calendar.monthrange(
            invoice_year,
            invoice_month,
        )[1]

        dia_vencimento = min(
            cartao["due_day"],
            ultimo_dia,
        )

        return date(
            invoice_year,
            invoice_month,
            dia_vencimento,
        ).isoformat()

    def _assinatura_ja_caiu_no_cartao(
            self,
            assinatura: dict,
            charge_date: str,
            amount_cents: int,
    ) -> bool:

        return (
            self._buscar_lancamento_cartao_assinatura(
                assinatura=assinatura,
                charge_date=charge_date,
                amount_cents=amount_cents,
            )
            is not None
        )

    def _obter_palavras_match(
            self,
            assinatura: dict,
    ) -> list[str]:

        textos = []

        if assinatura["name"]:
            textos.append(assinatura["name"])

        if assinatura["match_keywords"]:
            textos.extend(
                assinatura["match_keywords"].split(";")
            )

        palavras = []

        for texto in textos:
            texto = texto.strip().lower()

            if texto:
                palavras.append(texto)

        return palavras

    def _agrupar_projecoes_cartao(
            self,
            eventos: list[dict],
    ) -> list[dict]:

        eventos_finais = []
        grupos_cartao = {}

        for evento in eventos:
            if evento.get("payment_type") != "credit_card":
                eventos_finais.append(evento)
                continue

            chave = (
                evento.get("date"),
                evento.get("credit_card_id"),
                evento.get("account_id"),
            )

            if chave not in grupos_cartao:
                grupos_cartao[chave] = {
                    "kind": "commitment",
                    "date": evento["date"],
                    "description": "Assinaturas Previstas",
                    "amount_cents": 0,
                    "status": "expected",
                    "account_id": evento.get("account_id"),
                    "payment_type": "credit_card",
                    "credit_card_id": evento.get("credit_card_id"),
                    "projection_type": "projected",
                    "commitment_origin": "subscription_projection",
                    "subscription_ids": [],
                    "details": [],
                }

            grupos_cartao[chave]["amount_cents"] += int(
                evento["amount_cents"] or 0
            )

            grupos_cartao[chave]["subscription_ids"].append(
                evento["subscription_id"]
            )

            grupos_cartao[chave]["details"].append(
                {
                    "subscription_id": evento["subscription_id"],
                    "description": evento["description"],
                    "amount_cents": evento["amount_cents"],
                }
            )

        eventos_finais.extend(
            grupos_cartao.values()
        )

        return eventos_finais

    def cobrar_mes(
            self,
            subscription_id: int,
            reference_year: int,
            reference_month: int,
            paid_date: str | None = None,
            account_id: int | None = None,
            notes: str | None = None,
    ) -> int:
        assinatura = self.repository.buscar_assinatura_por_id(
            subscription_id
        )

        if assinatura is None:
            raise ValueError("Assinatura não encontrada.")

        if assinatura["payment_method"] == "credit_card":
            return self._cobrar_cartao(
                assinatura=assinatura,
                reference_year=reference_year,
                reference_month=reference_month,
                notes=notes,
            )

        return self._cobrar_conta(
            assinatura=assinatura,
            reference_year=reference_year,
            reference_month=reference_month,
            paid_date=paid_date,
            account_id=account_id,
            notes=notes,
        )

    def _resolver_conta_cobranca(
            self,
            assinatura: dict,
    ) -> int | None:
        if assinatura["payment_method"] in {"bank_account", "pix"}:
            return assinatura["account_id"]

        if assinatura["payment_method"] == "credit_card":
            credit_card_id = assinatura["credit_card_id"]

            if credit_card_id is None:
                return None

            for cartao in self.credit_card_repository.listar_cartoes_ativos():
                if cartao["id"] == credit_card_id:
                    return cartao["account_id"]

        return None

    def _cobrar_conta(
            self,
            assinatura: dict,
    ) -> int | None:
        if assinatura["payment_method"] in {"bank_account", "pix"}:
            return assinatura["account_id"]

        if assinatura["payment_method"] == "credit_card":
            credit_card_id = assinatura["credit_card_id"]

            if credit_card_id is None:
                return None

            for cartao in self.credit_card_repository.listar_cartoes_ativos():
                if cartao["id"] == credit_card_id:
                    return cartao["account_id"]

        return None

    def _cobrar_cartao(
            self,
            assinatura: dict,
            reference_year: int,
            reference_month: int,
            notes: str | None,
    ) -> int:

        cartao = self._obter_cartao_por_id(
            assinatura["credit_card_id"]
        )

        if cartao is None:
            raise ValueError("Cartão da assinatura não encontrado.")

        data_cobranca = self.montar_data_cobranca(
            year=reference_year,
            month=reference_month,
            charge_day=int(assinatura["charge_day"]),
        )

        valor_cents = int(
            assinatura["amount_cents"] or 0
        )

        lancamento_existente = self._buscar_lancamento_cartao_assinatura(
            assinatura=assinatura,
            charge_date=data_cobranca,
            amount_cents=valor_cents,
        )

        if lancamento_existente is not None:
            expense_id = lancamento_existente["id"]

            self.repository.criar_ou_atualizar_override(
                subscription_id=assinatura["id"],
                reference_year=reference_year,
                reference_month=reference_month,
                expected_charge_date=data_cobranca,
                expected_payment_date=None,
                amount_cents=valor_cents,
                status="matched",
                actual_charge_date=lancamento_existente["effective_purchase_date"],
                actual_amount_cents=lancamento_existente["effective_amount_cents"],
                resolved_at=date.today().isoformat(),
                resolution_type="matched_credit_card",
                matched_credit_card_expense_id=expense_id,
                matched_balance_commitment_id=None,
                notes="Cobrança encontrada no cartão de crédito.",
            )

            return expense_id

        expense_id = self.credit_card_detail_service.criar_lancamento_manual(
            credit_card=cartao,
            category_id=1,
            effective_description=assinatura["name"],
            effective_purchase_date=data_cobranca,
            effective_amount_cents=valor_cents,
            notes=notes,
            installment_number=1,
            installment_total=1,
        )

        self.credit_card_detail_service.reprocessar_faturas_cartao(
            cartao
        )

        self.repository.criar_ou_atualizar_override(
            subscription_id=assinatura["id"],
            reference_year=reference_year,
            reference_month=reference_month,
            expected_charge_date=data_cobranca,
            expected_payment_date=None,
            amount_cents=valor_cents,
            status="charged",
            actual_charge_date=data_cobranca,
            actual_amount_cents=valor_cents,
            resolved_at=date.today().isoformat(),
            resolution_type="manual_credit_card",
            matched_credit_card_expense_id=expense_id,
            matched_balance_commitment_id=None,
            notes=notes,
        )

        return expense_id

    def _buscar_lancamento_cartao_assinatura(
            self,
            assinatura: dict,
            charge_date: str,
            amount_cents: int,
    ) -> dict | None:

        credit_card_id = assinatura["credit_card_id"]

        if credit_card_id is None:
            return None

        palavras = self._obter_palavras_match(
            assinatura
        )

        data_base = date.fromisoformat(
            charge_date
        )

        data_inicio = (
            data_base
            + relativedelta(days=-3)
        ).isoformat()

        data_fim = (
            data_base
            + relativedelta(days=3)
        ).isoformat()

        lancamentos = (
            self.credit_card_expense_repository
            .listar_lancamentos_match_assinatura(
                credit_card_id=credit_card_id,
                start_date=data_inicio,
                end_date=data_fim,
                amount_cents=amount_cents,
            )
        )

        if not lancamentos:
            return None

        if not palavras:
            return lancamentos[0]

        for lancamento in lancamentos:
            descricao = (
                lancamento["effective_description"]
                or lancamento["original_description"]
                or ""
            ).lower()

            for palavra in palavras:
                if palavra in descricao:
                    return lancamento

        return None