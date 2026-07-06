import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def coluna_existe(
        cursor,
        table_name: str,
        column_name: str,
) -> bool:

    cursor.execute(f"PRAGMA table_info({table_name})")

    return any(
        row[1] == column_name
        for row in cursor.fetchall()
    )


def executar() -> None:
    conexao = sqlite3.connect(DB_PATH)

    try:
        cursor = conexao.cursor()

        if not coluna_existe(
            cursor,
            "finance_calculator_simulations",
            "sort_order",
        ):
            cursor.execute(
                """
                ALTER TABLE finance_calculator_simulations
                ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0
                """
            )

        cursor.execute(
            """
            SELECT id
            FROM finance_calculator_simulations
            WHERE is_active = 1
            ORDER BY id ASC
            """
        )

        simulation_ids = [
            row[0]
            for row in cursor.fetchall()
        ]

        for index, simulation_id in enumerate(simulation_ids):
            cursor.execute(
                """
                UPDATE finance_calculator_simulations
                SET sort_order = ?
                WHERE id = ?
                """,
                (
                    index,
                    simulation_id,
                ),
            )

        conexao.commit()

        print("Migração de sort_order da Calculadora concluída.")

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    executar()