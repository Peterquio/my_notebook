from modules.finance.services.balance_service import BalanceService
from modules.finance.services.balance_account_service import BalanceAccountService

username = "default"

balance_service = BalanceService(username)
account_service = BalanceAccountService(username)

account_id = account_service.criar_conta(
    name="Conta Teste Compromisso",
    account_type="bank",
    include_in_global_balance=True,
    is_investment=False,
)

cycle_id = balance_service.repository.criar_ciclo(
    name="Teste Compromisso",
    start_date="2026-06-11",
    end_date="2026-07-10",
)

compromisso_id = balance_service.repository.criar_compromisso(
    cycle_id=cycle_id,
    description="Aluguel",
    expected_amount_cents=120000,
    due_date="2026-06-15",
    payment_type="bank_account",
    account_id=account_id,
)

print("Compromisso criado:", compromisso_id)

balance_service.atualizar_compromisso(
    compromisso_id=compromisso_id,
    description="Aluguel Atualizado",
    expected_amount_cents=130000,
    due_date="2026-06-15",
    payment_type="bank_account",
    account_id=account_id,
    credit_card_id=None,
)

print("Compromisso atualizado.")

balance_service.pagar_compromisso(
    compromisso_id=compromisso_id,
    valor_real_cents=130000,
    paid_date="2026-06-15",
)

print("Compromisso pago.")

balance_service.reabrir_compromisso(
    compromisso_id=compromisso_id,
)

print("Compromisso reaberto.")

balance_service.excluir_compromisso(
    compromisso_id=compromisso_id,
)

print("Compromisso excluído.")