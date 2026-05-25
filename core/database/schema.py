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
    preset_key TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO finance_credit_card_assets (
    id,
    bank_name,
    asset_name,
    preset_key
)
VALUES
(
    'generic_black_1',
    'Skyline',
    'Skyline Black',
    'generic_black'
),
(
    'nu_1',
    'Nubank',
    'Nubank Roxinho',
    'nubank_roxinho'
),
(
    'nu_2',
    'Nubank',
    'Ultravioleta',
    'nubank_ultravioleta'
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

CREATE TABLE IF NOT EXISTS finance_credit_card_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    credit_card_id INTEGER NOT NULL,

    invoice_year INTEGER NOT NULL,
    invoice_month INTEGER NOT NULL,

    closing_date TEXT NOT NULL,
    due_date TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'open',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(credit_card_id, invoice_year, invoice_month),

    FOREIGN KEY (credit_card_id)
        REFERENCES finance_credit_cards(id)
);

CREATE TABLE IF NOT EXISTS finance_credit_card_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    credit_card_id INTEGER NOT NULL,
    invoice_id INTEGER,

    category_id INTEGER DEFAULT 1,

    original_description TEXT,
    effective_description TEXT,
    
    original_purchase_date TEXT,
    effective_purchase_date TEXT,
    
    original_amount_cents INTEGER,
    effective_amount_cents INTEGER,
    
    installment_group_id TEXT,
    
    source_type TEXT,
    source_reference TEXT,

    billing_date TEXT NOT NULL,

    installment_number INTEGER NOT NULL DEFAULT 1,
    installment_total INTEGER NOT NULL DEFAULT 1,

    status TEXT NOT NULL DEFAULT 'pending',

    notes TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (credit_card_id)
        REFERENCES finance_credit_cards(id),

    FOREIGN KEY (invoice_id)
        REFERENCES finance_credit_card_invoices(id),

    FOREIGN KEY (category_id)
        REFERENCES finance_categories(id)
);
"""