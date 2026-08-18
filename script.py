import sqlite3
from pathlib import Path


DATABASE_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def coluna_existe(
        conexao: sqlite3.Connection,
        tabela: str,
        coluna: str,
) -> bool:

    cursor = conexao.execute(
        f"PRAGMA table_info({tabela})"
    )

    return any(
        row[1] == coluna
        for row in cursor.fetchall()
    )


def main() -> None:

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado: {DATABASE_PATH}"
        )

    conexao = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        if not coluna_existe(
                conexao,
                "finance_subscriptions",
                "category_id",
        ):

            conexao.execute(
                """
                ALTER TABLE finance_subscriptions
                ADD COLUMN category_id INTEGER
                REFERENCES finance_categories(id)
                """
            )

            print(
                "Coluna category_id criada."
            )

        # Categoria 1 = Outros
        # Serve para assinaturas antigas.

        conexao.execute(
            """
            UPDATE finance_subscriptions
            SET category_id = 1
            WHERE category_id IS NULL
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_finance_subscriptions_category
            ON finance_subscriptions(category_id)
            """
        )

        conexao.commit()

        print(
            "Migração concluída."
        )

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    main()