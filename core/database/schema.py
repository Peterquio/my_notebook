#Esse arquivo define a estrutura do banco de dados. Ou seja:
#tabelas
#colunas
#tipos
#relacionamentos
#valores padrão

GLOBAL_SCHEMA = """

CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    theme TEXT DEFAULT 'default',
    theme_mode TEXT DEFAULT 'dark',
    language TEXT DEFAULT 'pt-BR',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO app_settings (
    id,
    theme,
    theme_mode,
    language
)
VALUES (
    1,
    'default',
    'dark',
    'pt-BR'
);

"""