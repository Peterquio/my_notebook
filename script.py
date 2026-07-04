import sqlite3
from pathlib import Path


DB_PATH = Path(
    r"C:\dev\Outros\my_notebook\user_data\users\default.db"
)


def executar() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado: {DB_PATH}"
        )

    conexao = sqlite3.connect(DB_PATH)

    try:
        cursor = conexao.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS finance_calculator_simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                simulation_type TEXT NOT NULL DEFAULT 'statement',
                period_mode TEXT NOT NULL DEFAULT 'one_month',

                start_date TEXT,
                end_date TEXT,

                is_saved INTEGER NOT NULL DEFAULT 1,
                is_active INTEGER NOT NULL DEFAULT 1,

                notes TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS finance_calculator_simulation_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                simulation_id INTEGER NOT NULL,

                title TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'neutral',

                item_date TEXT,
                amount_cents INTEGER NOT NULL DEFAULT 0,

                sort_order INTEGER NOT NULL DEFAULT 0,

                notes TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (simulation_id)
                    REFERENCES finance_calculator_simulations(id)
            );
            """
        )

        conexao.commit()

        print("Migração da Calculadora concluída com sucesso.")

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    executar()