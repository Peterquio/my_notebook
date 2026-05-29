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
            include_in_global_balance: bool = True,
            is_investment: bool = False,
    ) -> int:
        return self.repository.criar_conta(
            name=name,
            account_type=account_type,
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