from datetime import date
from dateutil.relativedelta import relativedelta
from modules.finance.repositories.balance_repository import BalanceRepository
from modules.finance.repositories.balance_account_repository import BalanceAccountRepository
from modules.finance.repositories.balance_account_snapshot_repository import BalanceAccountSnapshotRepository

class BalanceService:
    def __init__(self, username: str) -> None:
        self.repository = BalanceRepository(username)
        self.account_repository = BalanceAccountRepository(username)
        self.snapshot_repository = BalanceAccountSnapshotRepository(username)

    def calcular_saldo_conta_na_data(
            self,
            account_id: int,
            data_iso: str,
    ) -> int:
        snapshot = self.snapshot_repository.buscar_snapshot_mais_recente_ate_data(
            account_id=account_id,
            data_iso=data_iso,
        )

        if snapshot is None:
            saldo = 0
            data_inicio = "0001-01-01"
        else:
            saldo = snapshot["balance_cents"]
            data_inicio = snapshot["snapshot_date"]

        receitas = self.repository.listar_receitas_periodo(
            start_date=data_inicio,
            end_date=data_iso,
        )

        for receita in receitas:
            if receita["account_id"] != account_id:
                continue

            if receita["expected_date"] <= data_inicio:
                continue

            valor = (
                receita["actual_amount_cents"]
                if receita["status"] == "received"
                and receita["actual_amount_cents"] is not None
                else receita["expected_amount_cents"]
            )

            saldo += valor

        compromissos = self.repository.listar_compromissos_periodo(
            start_date=data_inicio,
            end_date=data_iso,
        )

        for compromisso in compromissos:
            if compromisso["account_id"] != account_id:
                continue

            if compromisso["due_date"] <= data_inicio:
                continue

            valor = (
                compromisso["actual_amount_cents"]
                if compromisso["status"] == "paid"
                and compromisso["actual_amount_cents"] is not None
                else compromisso["expected_amount_cents"]
            )

            saldo -= valor

        return saldo

    def calcular_saldo_inicial_global(
            self,
            cycle_id: int,
    ) -> int:
        saldos_iniciais = self.account_repository.listar_saldos_iniciais_ciclo(cycle_id)

        total_cents = 0

        for saldo in saldos_iniciais:
            if saldo["include_in_global_balance"] != 1:
                continue

            if saldo["is_investment"] == 1:
                continue

            total_cents += saldo["opening_balance_cents"]

        return total_cents

    def _obter_ids_contas_saldo_global(self, cycle_id: int) -> set[int]:
        saldos_iniciais = self.account_repository.listar_saldos_iniciais_ciclo(cycle_id)

        account_ids = set()

        for saldo in saldos_iniciais:
            if saldo["include_in_global_balance"] != 1:
                continue

            if saldo["is_investment"] == 1:
                continue

            account_ids.add(saldo["account_id"])

        return account_ids

    def somar_receitas_recebidas(self, cycle_id: int) -> int:
        account_ids = self._obter_ids_contas_saldo_global(cycle_id)
        total = 0

        for receita in self.repository.listar_receitas_ciclo(cycle_id):
            if receita["account_id"] not in account_ids:
                continue

            if receita["status"] != "received":
                continue

            valor = (
                receita["actual_amount_cents"]
                if receita["actual_amount_cents"] is not None
                else receita["expected_amount_cents"]
            )

            total += valor

        return total

    def somar_receitas_previstas(self, cycle_id: int) -> int:
        account_ids = self._obter_ids_contas_saldo_global(cycle_id)
        total = 0

        for receita in self.repository.listar_receitas_ciclo(cycle_id):
            if receita["account_id"] not in account_ids:
                continue

            if receita["status"] != "expected":
                continue

            total += receita["expected_amount_cents"]

        return total

    def somar_compromissos_pagos(self, cycle_id: int) -> int:
        account_ids = self._obter_ids_contas_saldo_global(cycle_id)
        total = 0

        for compromisso in self.repository.listar_compromissos_ciclo(cycle_id):
            if compromisso["account_id"] not in account_ids:
                continue

            if compromisso["status"] != "paid":
                continue

            valor = (
                compromisso["actual_amount_cents"]
                if compromisso["actual_amount_cents"] is not None
                else compromisso["expected_amount_cents"]
            )

            total += valor

        return total

    def somar_compromissos_previstos(self, cycle_id: int) -> int:
        account_ids = self._obter_ids_contas_saldo_global(cycle_id)
        total = 0

        for compromisso in self.repository.listar_compromissos_ciclo(cycle_id):
            if compromisso["account_id"] not in account_ids:
                continue

            if compromisso["status"] != "expected":
                continue

            total += compromisso["expected_amount_cents"]

        return total

    def obter_resumo_ciclo(
            self,
            cycle_id: int,
    ) -> dict:

        saldo_inicial = self.calcular_saldo_inicial_global(cycle_id)

        receitas_recebidas = self.somar_receitas_recebidas(cycle_id)
        receitas_previstas = self.somar_receitas_previstas(cycle_id)

        compromissos_pagos = self.somar_compromissos_pagos(cycle_id)
        compromissos_previstos = self.somar_compromissos_previstos(cycle_id)

        saldo_atual = (
                saldo_inicial
                + receitas_recebidas
                - compromissos_pagos
        )

        saldo_previsto = (
                saldo_atual
                + receitas_previstas
                - compromissos_previstos
        )

        return {
            "cycle_id": cycle_id,
            "saldo_inicial_cents": saldo_inicial,
            "saldo_inicio_ciclo_cents": saldo_inicial,
            "saldo_final_estimado_cents": saldo_previsto,
            "receitas_recebidas_cents": receitas_recebidas,
            "receitas_previstas_cents": receitas_previstas,
            "compromissos_pagos_cents": compromissos_pagos,
            "compromissos_previstos_cents": compromissos_previstos,
            "saldo_atual_cents": saldo_atual,
            "saldo_previsto_cents": saldo_previsto,
        }

    def criar_receita(
            self,
            cycle_id: int,
            account_id: int,
            description: str,
            expected_amount_cents: int,
            expected_date: str,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> int:
        if account_id is None:
            raise ValueError("A receita precisa estar vinculada a uma conta.")

        conta = self.account_repository.buscar_conta_por_id(account_id)

        if conta is None:
            raise ValueError(f"Conta não encontrada: {account_id}")

        if conta["is_active"] != 1:
            raise ValueError("Não é possível lançar receita em uma conta inativa.")

        return self.repository.criar_receita(
            cycle_id=cycle_id,
            account_id=account_id,
            description=description,
            expected_amount_cents=expected_amount_cents,
            expected_date=expected_date,
            is_recurring=is_recurring,
            notes=notes,
        )

    def receber_receita(
            self,
            receita_id: int,
            valor_real_cents: int,
            received_date: str,
    ) -> None:
        self.repository.confirmar_receita(
            receita_id=receita_id,
            valor_real_cents=valor_real_cents,
            received_date=received_date,
        )

    def reabrir_receita(
            self,
            receita_id: int,
    ) -> None:
        self.repository.reabrir_receita(
            receita_id=receita_id,
        )

    def pagar_compromisso(
            self,
            compromisso_id: int,
            valor_real_cents: int,
            paid_date: str,
    ) -> None:
        self.repository.confirmar_compromisso(
            compromisso_id=compromisso_id,
            valor_real_cents=valor_real_cents,
            paid_date=paid_date,
        )

    def reabrir_compromisso(
            self,
            compromisso_id: int,
    ) -> None:
        self.repository.reabrir_compromisso(
            compromisso_id=compromisso_id,
        )

    def _adicionar_um_mes(
            self,
            data_texto: str,
    ) -> str:
        data = date.fromisoformat(data_texto)
        nova_data = data + relativedelta(months=1)
        return nova_data.isoformat()

    def _calcular_fim_ciclo(
            self,
            data_inicio: date,
    ) -> date:
        if data_inicio.day == 1:
            proximo_mes = data_inicio + relativedelta(months=1)

            return date.fromordinal(
                proximo_mes.replace(day=1).toordinal() - 1
            )

        proximo_mes = data_inicio + relativedelta(months=1)

        ultimo_dia_mes_destino = date.fromordinal(
            (proximo_mes.replace(day=1) + relativedelta(months=1)).toordinal() - 1
        ).day

        dia_fim = min(
            data_inicio.day - 1,
            ultimo_dia_mes_destino,
        )

        return date(
            proximo_mes.year,
            proximo_mes.month,
            dia_fim,
        )

    def calcular_saldo_atual_conta(
            self,
            cycle_id: int,
            account_id: int,
    ) -> int:
        saldos = self.account_repository.listar_saldos_iniciais_ciclo(cycle_id)

        saldo_inicial = 0

        for saldo in saldos:
            if saldo["account_id"] == account_id:
                saldo_inicial = saldo["opening_balance_cents"]
                break

        receitas_recebidas = 0

        for receita in self.repository.listar_receitas_ciclo(cycle_id):
            if receita["account_id"] != account_id:
                continue

            if receita["status"] != "received":
                continue

            valor = (
                receita["actual_amount_cents"]
                if receita["actual_amount_cents"] is not None
                else receita["expected_amount_cents"]
            )

            receitas_recebidas += valor

        compromissos_pagos = 0

        for compromisso in self.repository.listar_compromissos_ciclo(cycle_id):
            if compromisso["account_id"] != account_id:
                continue

            if compromisso["status"] != "paid":
                continue

            valor = (
                compromisso["actual_amount_cents"]
                if compromisso["actual_amount_cents"] is not None
                else compromisso["expected_amount_cents"]
            )

            compromissos_pagos += valor

        return saldo_inicial + receitas_recebidas - compromissos_pagos

    def recalcular_saldos_abertura_ciclos_futuros(
            self,
    ) -> None:
        ciclos = self.repository.listar_ciclos_ativos()

        ciclos_ordenados = sorted(
            ciclos,
            key=lambda ciclo: ciclo["start_date"],
        )

        if len(ciclos_ordenados) <= 1:
            return

        for index in range(1, len(ciclos_ordenados)):
            ciclo_anterior = ciclos_ordenados[index - 1]
            ciclo_atual = ciclos_ordenados[index]

            saldos_anteriores = (
                self.account_repository.listar_saldos_iniciais_ciclo(
                    ciclo_anterior["id"]
                )
            )

            for saldo in saldos_anteriores:
                account_id = saldo["account_id"]

                saldo_previsto_conta = self.calcular_saldo_previsto_conta(
                    cycle_id=ciclo_anterior["id"],
                    account_id=account_id,
                )

                self.account_repository.definir_saldo_inicial_conta(
                    cycle_id=ciclo_atual["id"],
                    account_id=account_id,
                    opening_balance_cents=saldo_previsto_conta,
                )

    def garantir_ciclos_ate_data(
            self,
            data_final_iso: str,
    ) -> None:
        ciclos = self.repository.listar_ciclos_ativos()

        if not ciclos:
            return

        ciclos_ordenados = sorted(
            ciclos,
            key=lambda ciclo: ciclo["start_date"],
        )

        ultimo_ciclo = ciclos_ordenados[-1]

        data_final = date.fromisoformat(
            data_final_iso
        )

        while data_final > date.fromisoformat(ultimo_ciclo["end_date"]):
            novo_cycle_id = self.gerar_proximo_ciclo_real(
                ultimo_ciclo["id"]
            )

            novo_ciclo = self.repository.buscar_ciclo_por_id(
                novo_cycle_id
            )

            if novo_ciclo is None:
                raise ValueError(
                    "O ciclo financeiro foi criado, mas não pôde ser carregado."
                )

            ultimo_ciclo = novo_ciclo

    def gerar_proximo_ciclo_real(
            self,
            cycle_id: int,
    ) -> int:
        ciclo_atual = self.repository.buscar_ciclo_por_id(cycle_id)

        if ciclo_atual is None:
            raise ValueError(f"Ciclo não encontrado: {cycle_id}")

        data_fim_atual = date.fromisoformat(ciclo_atual["end_date"])

        nova_data_inicio = date.fromordinal(
            data_fim_atual.toordinal() + 1
        )

        nova_data_fim = self._calcular_fim_ciclo(
            nova_data_inicio
        )

        novo_nome = (
            f"Ciclo {nova_data_inicio.isoformat()} "
            f"até {nova_data_fim.isoformat()}"
        )

        novo_cycle_id = self.repository.criar_ciclo(
            name=novo_nome,
            start_date=nova_data_inicio.isoformat(),
            end_date=nova_data_fim.isoformat(),
            opening_balance_source="previous_cycle_real",
        )

        saldos_anteriores = self.account_repository.listar_saldos_iniciais_ciclo(cycle_id)

        for saldo in saldos_anteriores:
            account_id = saldo["account_id"]

            saldo_real_conta = self.calcular_saldo_previsto_conta(
                cycle_id=cycle_id,
                account_id=account_id,
            )

            self.account_repository.definir_saldo_inicial_conta(
                cycle_id=novo_cycle_id,
                account_id=account_id,
                opening_balance_cents=saldo_real_conta,
            )

        receitas = self.repository.listar_receitas_ciclo(cycle_id)

        for receita in receitas:
            if receita["is_recurring"] != 1:
                continue

            self.repository.criar_receita(
                cycle_id=novo_cycle_id,
                account_id=receita["account_id"],
                description=receita["description"],
                expected_amount_cents=receita["expected_amount_cents"],
                expected_date=self._adicionar_um_mes(receita["expected_date"]),
                is_recurring=True,
                notes=receita["notes"],
            )

        compromissos = self.repository.listar_compromissos_ciclo(cycle_id)

        for compromisso in compromissos:
            if compromisso["is_recurring"] != 1:
                continue

            self.repository.criar_compromisso(
                cycle_id=novo_cycle_id,
                description=compromisso["description"],
                expected_amount_cents=compromisso["expected_amount_cents"],
                due_date=self._adicionar_um_mes(compromisso["due_date"]),
                payment_type=compromisso["payment_type"],
                account_id=compromisso["account_id"],
                credit_card_id=compromisso["credit_card_id"],
                is_recurring=True,
                notes=compromisso["notes"],
            )

        return novo_cycle_id

    def obter_resumo_dashboard(
            self,
            cycle_id: int,
    ) -> dict:
        resumo = self.obter_resumo_ciclo(cycle_id)

        proximos_vencimentos = 0

        compromissos = self.repository.listar_compromissos_ciclo(cycle_id)

        for compromisso in compromissos:
            if compromisso["status"] != "expected":
                continue

            proximos_vencimentos += 1

        return {
            "cycle_id": cycle_id,

            "saldo_atual_cents": resumo["saldo_atual_cents"],
            "saldo_previsto_cents": resumo["saldo_previsto_cents"],

            "receitas_previstas_cents": resumo["receitas_previstas_cents"],
            "compromissos_previstos_cents": resumo["compromissos_previstos_cents"],

            "proximos_vencimentos": proximos_vencimentos,
        }

    def calcular_saldo_previsto_conta(
            self,
            cycle_id: int,
            account_id: int,
    ) -> int:
        saldo_atual = self.calcular_saldo_atual_conta(
            cycle_id=cycle_id,
            account_id=account_id,
        )

        receitas_previstas = 0

        for receita in self.repository.listar_receitas_ciclo(cycle_id):
            if receita["account_id"] != account_id:
                continue

            if receita["status"] != "expected":
                continue

            receitas_previstas += receita["expected_amount_cents"]

        compromissos_previstos = 0

        for compromisso in self.repository.listar_compromissos_ciclo(cycle_id):
            if compromisso["account_id"] != account_id:
                continue

            if compromisso["status"] != "expected":
                continue

            compromissos_previstos += compromisso["expected_amount_cents"]

        return saldo_atual + receitas_previstas - compromissos_previstos

    def obter_resumo_conta_dashboard(
            self,
            cycle_id: int,
            account_id: int,
    ) -> dict:
        saldo_atual = self.calcular_saldo_atual_conta(
            cycle_id=cycle_id,
            account_id=account_id,
        )

        saldo_previsto = self.calcular_saldo_previsto_conta(
            cycle_id=cycle_id,
            account_id=account_id,
        )

        conta = self.account_repository.buscar_conta_por_id(account_id)

        return {
            "cycle_id": cycle_id,
            "account_id": account_id,
            "account_name": conta["name"] if conta else f"Conta #{account_id}",
            "saldo_atual_cents": saldo_atual,
            "saldo_previsto_cents": saldo_previsto,
        }

    def atualizar_receita(
            self,
            receita_id: int,
            account_id: int,
            description: str,
            expected_amount_cents: int,
            expected_date: str,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> None:

        conta = self.account_repository.buscar_conta_por_id(
            account_id
        )

        if conta is None:
            raise ValueError("Conta não encontrada.")

        if conta["is_active"] != 1:
            raise ValueError("Conta inativa.")

        self.repository.atualizar_receita(
            receita_id=receita_id,
            account_id=account_id,
            description=description,
            expected_amount_cents=expected_amount_cents,
            expected_date=expected_date,
            is_recurring=is_recurring,
            notes=notes,
        )

    def excluir_receita(
            self,
            receita_id: int,
    ) -> None:
        self.repository.excluir_receita(
            receita_id
        )

    def listar_ciclos(self) -> list[dict]:
        return self.repository.listar_ciclos_ativos()

    def obter_ciclo_padrao(self) -> dict | None:
        ciclos = self.listar_ciclos()

        if not ciclos:
            return None

        return ciclos[0]

    def listar_receitas_ciclo(
            self,
            cycle_id: int,
    ) -> list[dict]:
        return self.repository.listar_receitas_ciclo(
            cycle_id
        )

    def listar_compromissos_ciclo(
            self,
            cycle_id: int,
    ) -> list[dict]:
        return self.repository.listar_compromissos_ciclo(
            cycle_id
        )

    def listar_eventos_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> list[dict]:

        receitas = self.repository.listar_receitas_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        compromissos = self.repository.listar_compromissos_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        eventos = []

        for receita in receitas:
            eventos.append(
                {
                    "kind": "income",
                    "date": receita["received_date"] or receita["expected_date"],
                    "description": receita["description"],
                    "amount_cents": (
                        receita["actual_amount_cents"]
                        if receita["status"] == "received"
                        and receita["actual_amount_cents"] is not None
                        else receita["expected_amount_cents"]
                    ),
                    "status": receita["status"],
                    "account_id": receita["account_id"],
                    "projection_type": "real",
                }
            )

        for compromisso in compromissos:
            eventos.append(
                {
                    "kind": "commitment",
                    "date": compromisso["paid_date"] or compromisso["due_date"],
                    "description": compromisso["description"],
                    "amount_cents": (
                        compromisso["actual_amount_cents"]
                        if compromisso["status"] == "paid"
                        and compromisso["actual_amount_cents"] is not None
                        else compromisso["expected_amount_cents"]
                    ),
                    "status": compromisso["status"],
                    "account_id": compromisso["account_id"],
                    "payment_type": compromisso["payment_type"],
                    "projection_type": compromisso.get(
                        "projection_type",
                        "real",
                    ),
                }
            )

        eventos.sort(
            key=lambda evento: (
                evento["date"],
                0 if evento["kind"] == "income" else 1,
                evento["description"].lower(),
            )
        )

        return eventos

    def atualizar_compromisso(
            self,
            compromisso_id: int,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            payment_type: str,
            account_id: int | None,
            credit_card_id: int | None,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> None:

        if payment_type == "bank_account":
            conta = self.account_repository.buscar_conta_por_id(
                account_id
            )

            if conta is None:
                raise ValueError(
                    "Conta não encontrada."
                )

            if conta["is_active"] != 1:
                raise ValueError(
                    "Conta inativa."
                )

        self.repository.atualizar_compromisso(
            compromisso_id=compromisso_id,
            description=description,
            expected_amount_cents=expected_amount_cents,
            due_date=due_date,
            payment_type=payment_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
            is_recurring=is_recurring,
            notes=notes,
        )

    def excluir_compromisso(
            self,
            compromisso_id: int,
    ) -> None:
        self.repository.excluir_compromisso(
            compromisso_id
        )

    def criar_compromisso(
            self,
            cycle_id: int,
            description: str,
            expected_amount_cents: int,
            due_date: str,
            payment_type: str,
            account_id: int | None = None,
            credit_card_id: int | None = None,
            is_recurring: bool = False,
            notes: str | None = None,
    ) -> int:

        if payment_type == "bank_account":
            if account_id is None:
                raise ValueError(
                    "Compromissos bancários precisam de uma conta."
                )

            conta = self.account_repository.buscar_conta_por_id(
                account_id
            )

            if conta is None:
                raise ValueError(
                    "Conta não encontrada."
                )

            if conta["is_active"] != 1:
                raise ValueError(
                    "Conta inativa."
                )

        return self.repository.criar_compromisso(
            cycle_id=cycle_id,
            description=description,
            expected_amount_cents=expected_amount_cents,
            due_date=due_date,
            payment_type=payment_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
            is_recurring=is_recurring,
            notes=notes,
        )

    def criar_ciclo(
            self,
            name: str,
            start_date: str,
            end_date: str,
            opening_balance_source: str = "manual",
    ) -> int:
        return self.repository.criar_ciclo(
            name=name,
            start_date=start_date,
            end_date=end_date,
            opening_balance_source=opening_balance_source,
        )

    def obter_resumo_periodo(
            self,
            start_date: str,
            end_date: str,
    ) -> dict:
        saldo_inicial_periodo = self.calcular_saldo_global_na_data(
            self._obter_dia_anterior(start_date)
        )
        receitas = self.repository.listar_receitas_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        compromissos = self.repository.listar_compromissos_periodo(
            start_date=start_date,
            end_date=end_date,
        )

        receitas_recebidas = 0
        receitas_previstas = 0

        for receita in receitas:
            if receita["status"] == "received":
                receitas_recebidas += (
                    receita["actual_amount_cents"]
                    if receita["actual_amount_cents"] is not None
                    else receita["expected_amount_cents"]
                )
            else:
                receitas_previstas += receita["expected_amount_cents"]

        compromissos_pagos = 0
        compromissos_previstos = 0

        for compromisso in compromissos:
            if compromisso["status"] == "paid":
                compromissos_pagos += (
                    compromisso["actual_amount_cents"]
                    if compromisso["actual_amount_cents"] is not None
                    else compromisso["expected_amount_cents"]
                )
            else:
                compromissos_previstos += compromisso["expected_amount_cents"]

        saldo_movimentado_real = (
                receitas_recebidas
                - compromissos_pagos
        )

        saldo_movimentado_previsto = (
                receitas_previstas
                - compromissos_previstos
        )

        saldo_final_estimado = (
                saldo_inicial_periodo
                + saldo_movimentado_real
                + saldo_movimentado_previsto
        )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "saldo_inicial_periodo_cents": saldo_inicial_periodo,
            "receitas_recebidas_cents": receitas_recebidas,
            "receitas_previstas_cents": receitas_previstas,
            "compromissos_pagos_cents": compromissos_pagos,
            "compromissos_previstos_cents": compromissos_previstos,
            "saldo_movimentado_real_cents": saldo_movimentado_real,
            "saldo_movimentado_previsto_cents": saldo_movimentado_previsto,
            "saldo_final_estimado_cents": saldo_final_estimado,
        }

    def calcular_saldo_global_na_data(
            self,
            data_iso: str,
    ) -> int:
        contas = self.account_repository.listar_contas_ativas()

        total = 0

        for conta in contas:
            if conta["include_in_global_balance"] != 1:
                continue

            if conta["is_investment"] == 1:
                continue

            total += self.calcular_saldo_conta_na_data(
                account_id=conta["id"],
                data_iso=data_iso,
            )

        return total

    def _obter_dia_anterior(
            self,
            data_iso: str,
    ) -> str:
        return (
                date.fromisoformat(data_iso)
                + relativedelta(days=-1)
        ).isoformat()