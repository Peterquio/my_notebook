from core.database.database_manager import DatabaseManager


USERNAME = "default"


def recriar_tabela_pix():
    database = DatabaseManager(USERNAME)
    conexao = database.get_connection()
    cursor = conexao.cursor()

    print("Verificando tabela PIX...")

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'finance_pix_transactions'
        """
    )

    tabela_existe = cursor.fetchone() is not None

    if not tabela_existe:
        print("Tabela finance_pix_transactions não existe.")
        print("Nada precisa ser removido.")
        return

    cursor.execute(
        """
        PRAGMA table_info(finance_pix_transactions)
        """
    )

    colunas = [
        row["name"]
        for row in cursor.fetchall()
    ]

    print(f"Colunas atuais: {colunas}")

    cursor.execute(
        """
        DROP TABLE finance_pix_transactions
        """
    )

    conexao.commit()

    print()
    print("Tabela finance_pix_transactions removida com sucesso.")
    print("Abra o My Notebook novamente.")
    print("O GLOBAL_SCHEMA criará a nova versão da tabela PIX.")


if __name__ == "__main__":
    recriar_tabela_pix()