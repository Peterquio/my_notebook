from modules.finance.repositories.balance_account_repository import (
    BalanceAccountRepository,
)


class BalanceAccountService:
    def __init__(self, username: str) -> None:
        self.repository = BalanceAccountRepository(username)

    def criar_conta(
            self,
            name: str,
            account_type: str = "bank",
            institution_name: str | None = None,
            bank_preset_key: str | None = None,
            agency: str | None = None,
            account_number: str | None = None,
            account_kind: str | None = None,
            include_in_global_balance: bool = True,
            is_investment: bool = False,
    ) -> int:
        return self.repository.criar_conta(
            name=name,
            account_type=account_type,
            institution_name=institution_name,
            bank_preset_key=bank_preset_key,
            agency=agency,
            account_number=account_number,
            account_kind=account_kind,
            include_in_global_balance=include_in_global_balance,
            is_investment=is_investment,
        )

    def listar_contas(self) -> list[dict]:
        return self.repository.listar_contas_ativas()

    def buscar_conta(
            self,
            account_id: int,
    ) -> dict | None:
        return self.repository.buscar_conta_por_id(account_id)

    def atualizar_conta(
            self,
            account_id: int,
            name: str,
            account_type: str,
            institution_name: str | None,
            bank_preset_key: str | None,
            agency: str | None,
            account_number: str | None,
            account_kind: str | None,
            include_in_global_balance: bool,
            is_investment: bool,
    ) -> None:
        self.repository.atualizar_conta(
            account_id=account_id,
            name=name,
            account_type=account_type,
            institution_name=institution_name,
            bank_preset_key=bank_preset_key,
            agency=agency,
            account_number=account_number,
            account_kind=account_kind,
            include_in_global_balance=include_in_global_balance,
            is_investment=is_investment,
        )

    def definir_saldo_inicial_conta(
            self,
            cycle_id: int,
            account_id: int,
            opening_balance_cents: int,
    ) -> None:
        self.repository.definir_saldo_inicial_conta(
            cycle_id=cycle_id,
            account_id=account_id,
            opening_balance_cents=opening_balance_cents,
        )

    def buscar_saldo_inicial_conta(
            self,
            cycle_id: int,
            account_id: int,
    ) -> int:
        saldos = self.repository.listar_saldos_iniciais_ciclo(
            cycle_id
        )

        for saldo in saldos:
            if saldo["account_id"] == account_id:
                return saldo["opening_balance_cents"]

        return 0

    def desativar_conta(
            self,
            account_id: int,
    ) -> None:
        self.repository.desativar_conta(
            account_id=account_id,
        )