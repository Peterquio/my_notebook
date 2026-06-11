from modules.finance.repositories.finance_settings_repository import (
    FinanceSettingsRepository,
)

repo = FinanceSettingsRepository("default")

print(
    "Reference Day:",
    repo.obter_reference_day()
)