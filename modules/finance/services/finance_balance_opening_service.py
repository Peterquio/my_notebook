from modules.finance.services.credit_card_balance_sync_service import (
    CreditCardBalanceSyncService,
)

from modules.finance.services.balance_service import BalanceService


class FinanceBalanceOpeningService:
    def __init__(
            self,
            username: str,
    ) -> None:
        self.username = username

        self.credit_card_balance_sync_service = (
            CreditCardBalanceSyncService(
                username
            )
        )

        self.balance_service = BalanceService(
            username
        )

    def preparar_abertura_saldo(
            self,
    ) -> None:
        self.credit_card_balance_sync_service.sincronizar_todos_cartoes_para_saldo()
        self.balance_service.recalcular_saldos_abertura_ciclos_futuros()