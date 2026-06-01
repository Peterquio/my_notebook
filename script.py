from modules.finance.services.credit_card_balance_sync_service import (
    CreditCardBalanceSyncService,
)

service = CreditCardBalanceSyncService("default")

commitment_id = service.sincronizar_fatura_com_saldo(
    credit_card_id=2,
    invoice_year=2026,
    invoice_month=6,
)

print("Compromisso sincronizado:", commitment_id)