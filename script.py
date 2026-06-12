from modules.finance.services.balance_service import BalanceService

service = BalanceService("default")

ciclo = service.listar_ciclos()[0]
cycle_id = ciclo["id"]

account_id = 1

print("Usando ciclo:", ciclo)

receita_id = service.criar_receita(
    cycle_id=cycle_id,
    account_id=account_id,
    description="Salário Teste",
    expected_amount_cents=500000,
    expected_date="2026-06-15",
)

service.receber_receita(
    receita_id=receita_id,
    valor_real_cents=500000,
    received_date="2026-06-15",
)

service.criar_receita(
    cycle_id=cycle_id,
    account_id=account_id,
    description="Freelance Previsto",
    expected_amount_cents=150000,
    expected_date="2026-06-20",
)

compromisso_id = service.criar_compromisso(
    cycle_id=cycle_id,
    description="Aluguel Pago",
    expected_amount_cents=180000,
    due_date="2026-06-16",
    payment_type="bank_account",
    account_id=account_id,
)

service.pagar_compromisso(
    compromisso_id=compromisso_id,
    valor_real_cents=180000,
    paid_date="2026-06-16",
)

service.criar_compromisso(
    cycle_id=cycle_id,
    description="Internet Prevista",
    expected_amount_cents=12000,
    due_date="2026-06-25",
    payment_type="bank_account",
    account_id=account_id,
)

eventos = service.listar_eventos_periodo(
    start_date="2026-06-11",
    end_date="2026-07-10",
)

print("EVENTOS:", len(eventos))

for evento in eventos:
    print(evento)