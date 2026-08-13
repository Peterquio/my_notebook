from datetime import date
from dateutil.relativedelta import relativedelta
from modules.finance.repositories.balance_repository import BalanceRepository
from modules.finance.repositories.balance_account_repository import BalanceAccountRepository
from modules.finance.repositories.balance_account_snapshot_repository import BalanceAccountSnapshotRepository
from modules.finance.services.subscription_service import SubscriptionService

class BalanceService:
    def __init__(self, username: str) -> None:
        self.repository = BalanceRepository(username)
        self.account_repository = BalanceAccountRepository(username)
        self.snapshot_repository = BalanceAccountSnapshotRepository(username)
        self.subscription_service = SubscriptionService(username)

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

    def calcular_saldo_conta_estimado_reverso(
            self,
            account_id: int,
            data_iso: str,
            snapshot: dict,
    ) -> int:
        snapshot_date = snapshot["snapshot_date"]

        saldo = snapshot["balance_cents"]

        receitas = self.repository.listar_receitas_periodo(
            start_date=data_iso,
            end_date=snapshot_date,
        )

        for receita in receitas:
            if receita["account_id"] != account_id:
                continue

            data_evento = (
                receita["received_date"]
                or receita["expected_date"]
            )

            if data_evento >= snapshot_date:
                continue

            valor = (
                receita["actual_amount_cents"]
                if receita["status"] == "received"
                and receita["actual_amount_cents"] is not None
                else receita["expected_amount_cents"]
            )

            saldo -= valor

        compromissos = self.repository.listar_compromissos_periodo(
            start_date=data_iso,
            end_date=snapshot_date,
        )

        for compromisso in compromissos:
            if compromisso["account_id"] != account_id:
                continue

            data_evento = (
                compromisso["paid_date"]
                or compromisso["due_date"]
            )

            if data_evento >= snapshot_date:
                continue

            valor = (
                compromisso["actual_amount_cents"]
                if compromisso["status"] == "paid"
                and compromisso["actual_amount_cents"] is not None
                else compromisso["expected_amount_cents"]
            )

            saldo += valor

        return saldo

    def obter_saldo_inicial_timeline(
            self,
            data_iso: str,
    ) -> dict:
        contas = self.account_repository.listar_contas_ativas()

        total = 0
        possui_estimativa = False
        contas_estimadas = []
        primeiro_snapshot_futuro_date = None

        for conta in contas:
            if conta["include_in_global_balance"] != 1:
                continue

            if conta["is_investment"] == 1:
                continue

            snapshot_anterior = (
                self.snapshot_repository.buscar_snapshot_mais_recente_ate_data(
                    account_id=conta["id"],
                    data_iso=data_iso,
                )
            )

            if snapshot_anterior is not None:
                total += self.calcular_saldo_conta_na_data(
                    account_id=conta["id"],
                    data_iso=data_iso,
                )
                continue

            snapshot_futuro = (
                self.snapshot_repository.buscar_primeiro_snapshot_apos_data(
                    account_id=conta["id"],
                    data_iso=data_iso,
                )
            )

            if snapshot_futuro is None:
                possui_estimativa = True
                continue

            saldo_estimado = self.calcular_saldo_conta_estimado_reverso(
                account_id=conta["id"],
                data_iso=data_iso,
                snapshot=snapshot_futuro,
            )

            total += saldo_estimado
            possui_estimativa = True

            contas_estimadas.append(
                {
                    "account_id": conta["id"],
                    "account_name": conta["name"],
                    "balance_cents": saldo_estimado,
                    "source_snapshot_id": snapshot_futuro["id"],
                    "source_snapshot_date": snapshot_futuro["snapshot_date"],
                }
            )

            if primeiro_snapshot_futuro_date is None:
                primeiro_snapshot_futuro_date = snapshot_futuro["snapshot_date"]
            elif snapshot_futuro["snapshot_date"] < primeiro_snapshot_futuro_date:
                primeiro_snapshot_futuro_date = snapshot_futuro["snapshot_date"]

        return {
            "balance_cents": total,
            "is_estimated": possui_estimativa,
            "estimated_accounts": contas_estimadas,
            "first_future_snapshot_date": primeiro_snapshot_futuro_date,
        }

    def obter_saldo_inicial_conta_timeline(
            self,
            account_id: int,
            data_iso: str,
    ) -> dict:
        snapshot_anterior = (
            self.snapshot_repository.buscar_snapshot_mais_recente_ate_data(
                account_id=account_id,
                data_iso=data_iso,
            )
        )

        if snapshot_anterior is not None:
            return {
                "balance_cents": self.calcular_saldo_conta_na_data(
                    account_id=account_id,
                    data_iso=data_iso,
                ),
                "is_estimated": False,
                "estimated_accounts": [],
                "first_future_snapshot_date": None,
            }

        snapshot_futuro = (
            self.snapshot_repository.buscar_primeiro_snapshot_apos_data(
                account_id=account_id,
                data_iso=data_iso,
            )
        )

        if snapshot_futuro is None:
            return {
                "balance_cents": 0,
                "is_estimated": True,
                "estimated_accounts": [],
                "first_future_snapshot_date": None,
            }

        saldo_estimado = self.calcular_saldo_conta_estimado_reverso(
            account_id=account_id,
            data_iso=data_iso,
            snapshot=snapshot_futuro,
        )

        conta = self.account_repository.buscar_conta_por_id(
            account_id
        )

        return {
            "balance_cents": saldo_estimado,
            "is_estimated": True,
            "estimated_accounts": [
                {
                    "account_id": account_id,
                    "account_name": (
                        conta["name"]
                        if conta
                        else f"Conta #{account_id}"
                    ),
                    "balance_cents": saldo_estimado,
                    "source_snapshot_id": snapshot_futuro["id"],
                    "source_snapshot_date": snapshot_futuro["snapshot_date"],
                }
            ],
            "first_future_snapshot_date": snapshot_futuro["snapshot_date"],
        }

    def fixar_saldo_estimado_na_data(
            self,
            data_iso: str,
    ) -> list[int]:
        saldo_timeline = self.obter_saldo_inicial_timeline(
            data_iso
        )

        snapshot_ids = []

        for conta_estimativa in saldo_timeline["estimated_accounts"]:
            snapshot_id = self.snapshot_repository.criar_snapshot(
                account_id=conta_estimativa["account_id"],
                snapshot_date=data_iso,
                balance_cents=conta_estimativa["balance_cents"],
                snapshot_type="anchored",
                notes=(
                    "Snapshot criado a partir de estimativa reversa "
                    "confirmada pelo usuário."
                ),
            )

            snapshot_ids.append(snapshot_id)

        return snapshot_ids


    def criar_receita(
            self,
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


    def listar_eventos_periodo(
            self,
            start_date: str,
            end_date: str,
            account_id: int | None = None,
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
            if (
                    account_id is not None
                    and receita["account_id"] != account_id
            ):
                continue

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
            if (
                    account_id is not None
                    and compromisso["account_id"] != account_id
            ):
                continue
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

        eventos.extend(
            self.subscription_service.listar_projecoes_periodo(
                start_date=start_date,
                end_date=end_date,
                account_id=account_id,
            )
        )

        eventos.sort(
            key=lambda evento: (
                evento["date"],
                self._obter_prioridade_evento_timeline(evento),
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
            description=description,
            expected_amount_cents=expected_amount_cents,
            due_date=due_date,
            payment_type=payment_type,
            account_id=account_id,
            credit_card_id=credit_card_id,
            is_recurring=is_recurring,
            notes=notes,
        )

    def obter_resumo_periodo(
            self,
            start_date: str,
            end_date: str,
            account_id: int | None = None,
    ) -> dict:
        if account_id is None:
            saldo_timeline = self.obter_saldo_inicial_timeline(
                start_date
            )
        else:
            saldo_timeline = self.obter_saldo_inicial_conta_timeline(
                account_id=account_id,
                data_iso=start_date,
            )
        saldo_inicial_periodo = saldo_timeline["balance_cents"]

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
            if (
                    account_id is not None
                    and receita["account_id"] != account_id
            ):
                continue
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
            if (
                    account_id is not None
                    and compromisso["account_id"] != account_id
            ):
                continue
            if compromisso["status"] == "paid":
                compromissos_pagos += (
                    compromisso["actual_amount_cents"]
                    if compromisso["actual_amount_cents"] is not None
                    else compromisso["expected_amount_cents"]
                )
            else:
                compromissos_previstos += compromisso["expected_amount_cents"]

        projecoes_assinaturas = (
            self.subscription_service.listar_projecoes_periodo(
                start_date=start_date,
                end_date=end_date,
                account_id=account_id,
            )
        )

        assinaturas_previstas = 0

        for projecao in projecoes_assinaturas:
            assinaturas_previstas += int(
                projecao["amount_cents"] or 0
            )

        compromissos_previstos += assinaturas_previstas

        saldo_movimentado_real = (
                receitas_recebidas
                - compromissos_pagos
        )

        saldo_movimentado_previsto = (
                receitas_previstas
                - compromissos_previstos
        )

        if account_id is None:
            saldo_final_estimado = (
                    self.calcular_saldo_global_na_data(end_date)
                    - assinaturas_previstas
            )
        else:
            saldo_final_estimado = (
                    self.calcular_saldo_conta_na_data(
                        account_id=account_id,
                        data_iso=end_date,
                    )
                    - assinaturas_previstas
            )

        return {
            "start_date": start_date,
            "end_date": end_date,
            "saldo_inicial_periodo_cents": saldo_inicial_periodo,
            "saldo_inicial_estimado": saldo_timeline["is_estimated"],
            "saldo_inicial_contas_estimadas": saldo_timeline["estimated_accounts"],
            "primeiro_snapshot_futuro_date": saldo_timeline["first_future_snapshot_date"],
            "receitas_recebidas_cents": receitas_recebidas,
            "receitas_previstas_cents": receitas_previstas,
            "compromissos_pagos_cents": compromissos_pagos,
            "compromissos_previstos_cents": compromissos_previstos,
            "assinaturas_previstas_cents": assinaturas_previstas,
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

    def _obter_prioridade_evento_timeline(
            self,
            evento: dict,
    ) -> int:

        if evento["kind"] == "income":
            return 0

        if evento.get("commitment_origin") in {
            "credit_card_open",
            "credit_card_projected",
            "credit_card_closed",
        }:
            return 1

        if evento.get("commitment_origin") == "subscription_projection":
            return 2

        return 3