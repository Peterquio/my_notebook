import sqlite3

DB_PATH = r"C:\dev\Outros\my_notebook\user_data\users\default.db"

conexao = sqlite3.connect(DB_PATH)
cursor = conexao.cursor()

cursor.execute("PRAGMA table_info(finance_balance_accounts)")
colunas = [linha[1] for linha in cursor.fetchall()]

if "dashboard_card_id" not in colunas:
    cursor.execute(
        """
        ALTER TABLE finance_balance_accounts
        ADD COLUMN dashboard_card_id TEXT
        """
    )
    print("Coluna dashboard_card_id criada.")
else:
    print("Coluna dashboard_card_id já existe.")

conexao.commit()
conexao.close()

print("Migração concluída.")