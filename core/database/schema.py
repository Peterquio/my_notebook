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
('nubank_gold', 'Nubank', 'Nubank Gold', 'nubank_gold'),
('nubank_platinum', 'Nubank', 'Nubank Platinum', 'nubank_platinum'),
('nubank_ultravioleta', 'Nubank', 'Ultravioleta', 'nubank_ultravioleta'),

('inter_gold', 'Banco Inter', 'Inter Gold', 'inter_gold'),
('inter_platinum', 'Banco Inter', 'Inter Platinum', 'inter_platinum'),
('inter_black', 'Banco Inter', 'Inter Black', 'inter_black'),

('c6_standard', 'C6 Bank', 'C6', 'c6_standard'),
('c6_platinum', 'C6 Bank', 'C6 Platinum', 'c6_platinum'),
('c6_carbon', 'C6 Bank', 'C6 Carbon', 'c6_carbon'),

('bb_ourocard_facil', 'Banco do Brasil', 'Ourocard Fácil', 'bb_ourocard_facil'),
('bb_ourocard_platinum', 'Banco do Brasil', 'Ourocard Platinum', 'bb_ourocard_platinum'),
('bb_altus', 'Banco do Brasil', 'Altus', 'bb_altus'),

('itau_click', 'Itaú Unibanco', 'Click', 'itau_click'),
('itau_pao_de_acucar', 'Itaú Unibanco', 'Pão de Açúcar', 'itau_pao_de_acucar'),
('itau_personnalite_black', 'Itaú Unibanco', 'Personnalité Black', 'itau_personnalite_black'),

('bradesco_neo', 'Bradesco', 'Neo', 'bradesco_neo'),
('bradesco_elo_nanquim', 'Bradesco', 'Elo Nanquim', 'bradesco_elo_nanquim'),
('bradesco_aeternum', 'Bradesco', 'Aeternum', 'bradesco_aeternum'),

('santander_sx', 'Santander Brasil', 'SX', 'santander_sx'),
('santander_unique', 'Santander Brasil', 'Unique', 'santander_unique'),
('santander_unlimited', 'Santander Brasil', 'Unlimited', 'santander_unlimited'),

('caixa_sim', 'Caixa Econômica Federal', 'SIM', 'caixa_sim'),
('caixa_elo_grafite', 'Caixa Econômica Federal', 'Elo Grafite', 'caixa_elo_grafite'),

('btg_black', 'BTG Pactual', 'BTG Black', 'btg_black'),
('xp_visa_infinite', 'XP Inc.', 'XP Visa Infinite', 'xp_visa_infinite'),
('picpay_card', 'PicPay', 'PicPay Card', 'picpay_card'),
('pagbank_visa', 'PagBank', 'PagBank Visa', 'pagbank_visa'),
('mercado_pago_visa', 'Mercado Pago', 'Mercado Pago Visa', 'mercado_pago_visa'),
('will_bank', 'Will Bank', 'Will', 'will_bank'),
('neon_visa', 'Neon', 'Neon Visa', 'neon_visa'),
('sicoob_merit', 'Sicoob', 'Merit', 'sicoob_merit'),
('sicredi_visa_infinite', 'Sicredi', 'Visa Infinite', 'sicredi_visa_infinite'),

('generic_black', 'Skyline', 'Cartão Genérico', 'generic_black');

CREATE TABLE IF NOT EXISTS finance_credit_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    dashboard_card_id TEXT NOT NULL UNIQUE,

    name TEXT NOT NULL,
    asset_id TEXT NOT NULL,

    limit_amount_cents INTEGER NOT NULL DEFAULT 0,

    closing_day INTEGER NOT NULL,
    due_day INTEGER NOT NULL,

    last_four_digits TEXT,
    
    account_id INTEGER,
    sync_with_balance INTEGER NOT NULL DEFAULT 0,

    is_active INTEGER DEFAULT 1,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (asset_id)
        REFERENCES finance_credit_card_assets(id),

    FOREIGN KEY (account_id)
        REFERENCES finance_balance_accounts(id)
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

CREATE TABLE IF NOT EXISTS finance_credit_card_invoice_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    credit_card_id INTEGER NOT NULL,
    invoice_id INTEGER,

    adjustment_type TEXT NOT NULL,
    description TEXT NOT NULL,

    adjustment_date TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,

    source_type TEXT,
    source_reference TEXT,

    notes TEXT,

    status TEXT NOT NULL DEFAULT 'active',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (credit_card_id)
        REFERENCES finance_credit_cards(id),

    FOREIGN KEY (invoice_id)
        REFERENCES finance_credit_card_invoices(id)
);

CREATE TABLE IF NOT EXISTS finance_balance_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    account_type TEXT NOT NULL DEFAULT 'bank',

    institution_name TEXT,
    bank_preset_key TEXT,
    agency TEXT,
    account_number TEXT,
    account_kind TEXT,

    include_in_global_balance INTEGER NOT NULL DEFAULT 1,
    is_investment INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finance_balance_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,

    opening_balance_source TEXT NOT NULL DEFAULT 'manual',

    is_active INTEGER NOT NULL DEFAULT 1,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finance_balance_cycle_account_openings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    cycle_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,

    opening_balance_cents INTEGER NOT NULL DEFAULT 0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(cycle_id, account_id),

    FOREIGN KEY (cycle_id)
        REFERENCES finance_balance_cycles(id),

    FOREIGN KEY (account_id)
        REFERENCES finance_balance_accounts(id)
);

CREATE TABLE IF NOT EXISTS finance_balance_income_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    cycle_id INTEGER NOT NULL,
    account_id INTEGER,

    description TEXT NOT NULL,

    expected_amount_cents INTEGER NOT NULL DEFAULT 0,
    actual_amount_cents INTEGER,

    expected_date TEXT NOT NULL,
    received_date TEXT,

    status TEXT NOT NULL DEFAULT 'expected',

    is_recurring INTEGER NOT NULL DEFAULT 0,
    notes TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cycle_id)
        REFERENCES finance_balance_cycles(id),

    FOREIGN KEY (account_id)
        REFERENCES finance_balance_accounts(id)
);

CREATE TABLE IF NOT EXISTS finance_balance_commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    cycle_id INTEGER NOT NULL,

    description TEXT NOT NULL,

    expected_amount_cents INTEGER NOT NULL DEFAULT 0,
    actual_amount_cents INTEGER,

    due_date TEXT NOT NULL,
    paid_date TEXT,

    payment_type TEXT NOT NULL DEFAULT 'bank_account',

    account_id INTEGER,
    credit_card_id INTEGER,

    status TEXT NOT NULL DEFAULT 'expected',

    is_recurring INTEGER NOT NULL DEFAULT 0,
    notes TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cycle_id)
        REFERENCES finance_balance_cycles(id),

    FOREIGN KEY (account_id)
        REFERENCES finance_balance_accounts(id),

    FOREIGN KEY (credit_card_id)
        REFERENCES finance_credit_cards(id)
);
"""