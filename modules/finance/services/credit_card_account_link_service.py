from modules.finance.repositories.balance_account_repository import (
    BalanceAccountRepository,
)

from modules.finance.repositories.balance_repository import (
    BalanceRepository,
)

from modules.finance.repositories.credit_card_repository import (
    CreditCardRepository,
)


class CreditCardAccountLinkService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.credit_card_repository = CreditCardRepository(username)
        self.balance_account_repository = BalanceAccountRepository(username)
        self.balance_repository = BalanceRepository(username)

    def vincular_cartao_a_conta(
            self,
            credit_card_id: int,
            account_id: int,
            sincronizar_com_saldo: bool = True,
            atualizar_compromissos_existentes: bool = True,
    ) -> None:
        conta = self.balance_account_repository.buscar_conta_por_id(
            account_id
        )

        if conta is None:
            raise ValueError(
                f"Conta financeira não encontrada: {account_id}"
            )

        self.credit_card_repository.vincular_conta_saldo(
            credit_card_id=credit_card_id,
            account_id=account_id,
            sync_with_balance=sincronizar_com_saldo,
        )

        if atualizar_compromissos_existentes:
            self.balance_repository.atualizar_conta_compromissos_cartao_sincronizados(
                credit_card_id=credit_card_id,
                account_id=account_id,
            )

    def desvincular_cartao_da_conta(
            self,
            credit_card_id: int,
    ) -> None:
        self.credit_card_repository.vincular_conta_saldo(
            credit_card_id=credit_card_id,
            account_id=None,
            sync_with_balance=False,
        )