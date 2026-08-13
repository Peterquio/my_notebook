from datetime import date
from modules.finance.repositories.balance_account_repository import (
    BalanceAccountRepository,
)

from modules.finance.repositories.balance_account_snapshot_repository import (
    BalanceAccountSnapshotRepository,
)

class BalanceAccountService:
    def __init__(self, username: str) -> None:
        self.repository = BalanceAccountRepository(username)
        self.snapshot_repository = BalanceAccountSnapshotRepository(username)

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
            opening_balance_cents: int = 0,
            snapshot_date: str | None = None,
            dashboard_card_id: str | None = None,
    ) -> int:
        account_id = self.repository.criar_conta(
            name=name,
            account_type=account_type,
            institution_name=institution_name,
            bank_preset_key=bank_preset_key,
            agency=agency,
            account_number=account_number,
            account_kind=account_kind,
            include_in_global_balance=include_in_global_balance,
            is_investment=is_investment,
            dashboard_card_id=dashboard_card_id,
        )

        self.snapshot_repository.criar_snapshot(
            account_id=account_id,
            snapshot_date=snapshot_date or date.today().isoformat(),
            balance_cents=opening_balance_cents,
            snapshot_type="initial",
            notes="Snapshot inicial criado no cadastro da conta.",
        )

        return account_id

    def listar_contas(self) -> list[dict]:
        return self.repository.listar_contas_ativas()

    def buscar_conta(
            self,
            account_id: int,
    ) -> dict | None:
        return self.repository.buscar_conta_por_id(account_id)

    def buscar_por_dashboard_card_id(
            self,
            dashboard_card_id: str,
    ) -> dict | None:
        return self.repository.buscar_conta_por_dashboard_card_id(
            dashboard_card_id
        )

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

    def desativar_conta(
            self,
            account_id: int,
    ) -> None:
        self.repository.desativar_conta(
            account_id=account_id,
        )