import sqlite3

from modules.finance.services.balance_service import BalanceService

DB_PATH = r"D:\Dev\my_notebook\user_data\users\default.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== CICLOS ===")
cursor.execute("""
    SELECT id, name, start_date, end_date
    FROM finance_balance_cycles
    WHERE is_active = 1
    ORDER BY start_date DESC
""")
ciclos = [dict(row) for row in cursor.fetchall()]

for ciclo in ciclos:
    print(ciclo)

if not ciclos:
    print("Nenhum ciclo.")
    raise SystemExit

cycle_id = ciclos[0]["id"]

print("\n=== CONTAS ===")
cursor.execute("""
    SELECT *
    FROM finance_balance_accounts
    WHERE is_active = 1
    ORDER BY id
""")
for row in cursor.fetchall():
    print(dict(row))

print("\n=== SALDOS INICIAIS DO CICLO ===")
cursor.execute("""
    SELECT
        o.*,
        a.name AS account_name
    FROM finance_balance_cycle_account_openings o
    JOIN finance_balance_accounts a
        ON a.id = o.account_id
    WHERE o.cycle_id = ?
""", (cycle_id,))
for row in cursor.fetchall():
    print(dict(row))

conn.close()

print("\n=== RESUMO PELO BALANCE SERVICE ===")
service = BalanceService("default")
resumo = service.obter_resumo_ciclo(cycle_id)

for chave, valor in resumo.items():
    print(chave, valor)