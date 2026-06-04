import calendar
from datetime import date

from modules.finance.repositories.balance_repository import (
    BalanceRepository,
)

from modules.finance.repositories.monthly_template_repository import (
    MonthlyTemplateRepository,
)


class MonthlyTemplateMaterializationService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.template_repository = MonthlyTemplateRepository(username)
        self.balance_repository = BalanceRepository(username)

    def materializar_mes(
            self,
            ano: int,
            mes: int,
            respeitar_limite_31_dias: bool = False,
    ) -> dict:
        ano = int(ano)
        mes = int(mes)

        if mes < 1 or mes > 12:
            raise ValueError(
                "O mês precisa estar entre 1 e 12."
            )

        templates = self.template_repository.listar_ativos()

        receitas_criadas = 0
        compromissos_criados = 0
        ignorados = 0
        bloqueados_por_limite = 0

        for template in templates:
            if not template["auto_materialize"]:
                ignorados += 1
                continue

            data_ocorrencia = self._calcular_data_ocorrencia(
                ano=ano,
                mes=mes,
                day_of_month=template["day_of_month"],
            )

            if not self._template_valido_para_data(
                    template=template,
                    data_ocorrencia=data_ocorrencia,
            ):
                ignorados += 1
                continue

            if respeitar_limite_31_dias:
                if not self._dentro_limite_materializacao_manual(
                        data_ocorrencia
                ):
                    bloqueados_por_limite += 1
                    continue

            external_reference = self._montar_external_reference(
                template_id=template["id"],
                ano=ano,
                mes=mes,
            )

            ciclo = self._obter_ou_criar_ciclo_para_data(
                data_ocorrencia
            )

            if template["template_type"] == "income":
                criado = self._materializar_receita(
                    template=template,
                    cycle_id=ciclo["id"],
                    data_ocorrencia=data_ocorrencia,
                    external_reference=external_reference,
                )

                if criado:
                    receitas_criadas += 1
                else:
                    ignorados += 1

                continue

            if template["template_type"] == "commitment":
                criado = self._materializar_compromisso(
                    template=template,
                    cycle_id=ciclo["id"],
                    data_ocorrencia=data_ocorrencia,
                    external_reference=external_reference,
                )

                if criado:
                    compromissos_criados += 1
                else:
                    ignorados += 1

                continue

            ignorados += 1

        return {
            "ano": ano,
            "mes": mes,
            "receitas_criadas": receitas_criadas,
            "compromissos_criados": compromissos_criados,
            "ignorados": ignorados,
            "bloqueados_por_limite": bloqueados_por_limite,
        }

    def _materializar_receita(
            self,
            template: dict,
            cycle_id: int,
            data_ocorrencia: date,
            external_reference: str,
    ) -> bool:
        receita_existente = (
            self.balance_repository.buscar_receita_por_external_reference(
                external_reference
            )
        )

        if receita_existente is not None:
            return False

        self.balance_repository.criar_receita(
            cycle_id=cycle_id,
            account_id=template["account_id"],
            description=template["description"],
            expected_amount_cents=template["estimated_amount_cents"],
            expected_date=data_ocorrencia.isoformat(),
            is_recurring=True,
            notes=template["notes"],
            external_reference=external_reference,
        )

        return True

    def _materializar_compromisso(
            self,
            template: dict,
            cycle_id: int,
            data_ocorrencia: date,
            external_reference: str,
    ) -> bool:
        compromisso_existente = (
            self.balance_repository.buscar_compromisso_por_external_reference(
                external_reference
            )
        )

        if compromisso_existente is not None:
            return False

        self.balance_repository.criar_compromisso(
            cycle_id=cycle_id,
            description=template["description"],
            expected_amount_cents=template["estimated_amount_cents"],
            due_date=data_ocorrencia.isoformat(),
            payment_type=template["payment_type"],
            account_id=template["account_id"],
            credit_card_id=template["credit_card_id"],
            is_recurring=True,
            notes=template["notes"],
            external_reference=external_reference,
            status="expected",
        )

        return True

    def _obter_ou_criar_ciclo_para_data(
            self,
            data_ocorrencia: date,
    ) -> dict:
        ciclos = self.balance_repository.listar_ciclos_ativos()

        for ciclo in ciclos:
            data_inicio = date.fromisoformat(
                ciclo["start_date"]
            )

            data_fim = date.fromisoformat(
                ciclo["end_date"]
            )

            if data_inicio <= data_ocorrencia <= data_fim:
                return ciclo

        if not ciclos:
            raise ValueError(
                "Nenhum ciclo financeiro foi criado ainda. "
                "Crie o primeiro ciclo antes de materializar templates."
            )

        ciclos_ordenados = sorted(
            ciclos,
            key=lambda item: item["start_date"],
        )

        ultimo_ciclo = ciclos_ordenados[-1]

        while data_ocorrencia > date.fromisoformat(ultimo_ciclo["end_date"]):
            ultimo_ciclo = self._criar_proximo_ciclo(
                ultimo_ciclo
            )

        if date.fromisoformat(ultimo_ciclo["start_date"]) <= data_ocorrencia <= date.fromisoformat(ultimo_ciclo["end_date"]):
            return ultimo_ciclo

        raise ValueError(
            "Não foi possível encontrar ou criar um ciclo para a data informada."
        )

    def _criar_proximo_ciclo(
            self,
            ciclo_base: dict,
    ) -> dict:
        data_fim_atual = date.fromisoformat(
            ciclo_base["end_date"]
        )

        nova_data_inicio = date.fromordinal(
            data_fim_atual.toordinal() + 1
        )

        nova_data_fim = self._calcular_fim_ciclo(
            nova_data_inicio
        )

        novo_cycle_id = self.balance_repository.criar_ciclo(
            name=(
                f"Ciclo {nova_data_inicio.isoformat()} "
                f"até {nova_data_fim.isoformat()}"
            ),
            start_date=nova_data_inicio.isoformat(),
            end_date=nova_data_fim.isoformat(),
            opening_balance_source="auto",
        )

        novo_ciclo = self.balance_repository.buscar_ciclo_por_id(
            novo_cycle_id
        )

        if novo_ciclo is None:
            raise ValueError(
                "O ciclo foi criado, mas não pôde ser carregado."
            )

        return novo_ciclo

    def _calcular_fim_ciclo(
            self,
            data_inicio: date,
    ) -> date:
        if data_inicio.day == 1:
            ultimo_dia = calendar.monthrange(
                data_inicio.year,
                data_inicio.month,
            )[1]

            return date(
                data_inicio.year,
                data_inicio.month,
                ultimo_dia,
            )

        proximo_mes_ano = data_inicio.year
        proximo_mes = data_inicio.month + 1

        if proximo_mes > 12:
            proximo_mes = 1
            proximo_mes_ano += 1

        ultimo_dia_proximo_mes = calendar.monthrange(
            proximo_mes_ano,
            proximo_mes,
        )[1]

        dia_fim = min(
            data_inicio.day - 1,
            ultimo_dia_proximo_mes,
        )

        return date(
            proximo_mes_ano,
            proximo_mes,
            dia_fim,
        )

    def _calcular_data_ocorrencia(
            self,
            ano: int,
            mes: int,
            day_of_month: int,
    ) -> date:
        ultimo_dia_mes = calendar.monthrange(
            ano,
            mes,
        )[1]

        dia = min(
            int(day_of_month),
            ultimo_dia_mes,
        )

        return date(
            ano,
            mes,
            dia,
        )

    def _template_valido_para_data(
            self,
            template: dict,
            data_ocorrencia: date,
    ) -> bool:
        start_date = template["start_date"]
        end_date = template["end_date"]

        if start_date:
            if data_ocorrencia < date.fromisoformat(start_date):
                return False

        if end_date:
            if data_ocorrencia > date.fromisoformat(end_date):
                return False

        return True

    def _dentro_limite_materializacao_manual(
            self,
            data_ocorrencia: date,
    ) -> bool:
        hoje = date.today()
        limite = date.fromordinal(
            hoje.toordinal() + 31
        )

        return data_ocorrencia <= limite

    def _montar_external_reference(
            self,
            template_id: int,
            ano: int,
            mes: int,
    ) -> str:
        return f"template:{template_id}:{ano}-{mes:02d}"