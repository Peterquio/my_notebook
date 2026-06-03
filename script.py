from modules.finance.services.finance_category_settings_service import (
    FinanceCategorySettingsService,
)

service = FinanceCategorySettingsService("default")

resultado = service.importar_categorias(
    "categorias_financeiras.json",
    substituir=False,
)

print(resultado)