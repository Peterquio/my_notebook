from modules.finance.services.balance_account_service import (
    BalanceAccountService
)

service = BalanceAccountService("default")

print(service.listar_contas())