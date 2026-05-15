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

CREATE TABLE IF NOT EXISTS dashboard_layouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    module_name TEXT NOT NULL,

    card_id TEXT NOT NULL,
    card_type TEXT NOT NULL,
    config_json TEXT DEFAULT '{}',

    row INTEGER NOT NULL,
    column INTEGER NOT NULL,

    width_units INTEGER NOT NULL,
    height_units INTEGER NOT NULL,

    sort_order INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(module_name, card_id)
);

CREATE TABLE IF NOT EXISTS dashboard_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    card_id TEXT NOT NULL UNIQUE,
    module_name TEXT NOT NULL,

    card_type TEXT NOT NULL,

    title TEXT,
    size TEXT,

    config_json TEXT DEFAULT '{}',

    is_active INTEGER DEFAULT 1,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

"""