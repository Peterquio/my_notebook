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

CREATE TABLE IF NOT EXISTS finance_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    display_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#94A3B8',

    is_active INTEGER DEFAULT 1,
    is_protected INTEGER DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO finance_categories (
    id,
    display_number,
    name,
    color,
    is_active,
    is_protected
)
VALUES (
    1,
    99,
    'Outros',
    '#94A3B8',
    1,
    1
);

CREATE TABLE IF NOT EXISTS finance_credit_card_assets (
    id TEXT PRIMARY KEY,

    bank_name TEXT NOT NULL,
    asset_name TEXT NOT NULL,

    background_type TEXT NOT NULL DEFAULT 'color',
    background_value TEXT NOT NULL,

    text_color TEXT NOT NULL DEFAULT '#FFFFFF',

    is_active INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO finance_credit_card_assets (
    id,
    bank_name,
    asset_name,
    background_type,
    background_value,
    text_color
)
VALUES
(
    'nu_1',
    'Nubank',
    'Nubank Roxo',
    'color',
    '#7C3AED',
    '#FFFFFF'
),
(
    'bb_1',
    'Banco do Brasil',
    'BB Amarelo',
    'color',
    '#FACC15',
    '#1D4ED8'
),
(
    'generico_1',
    'Genérico',
    'Cartão Azul',
    'color',
    '#2563EB',
    '#FFFFFF'
);

CREATE TABLE IF NOT EXISTS finance_credit_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    dashboard_card_id TEXT NOT NULL UNIQUE,

    name TEXT NOT NULL,
    asset_id TEXT NOT NULL,

    limit_amount_cents INTEGER NOT NULL DEFAULT 0,

    closing_day INTEGER NOT NULL,
    due_day INTEGER NOT NULL,

    last_four_digits TEXT,

    is_active INTEGER DEFAULT 1,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (asset_id)
        REFERENCES finance_credit_card_assets(id)
);

"""