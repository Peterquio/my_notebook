from modules.finance.services.monthly_template_service import (
    MonthlyTemplateService,
)

service = MonthlyTemplateService("default")

template_id = service.criar_template(
    template_type="income",
    description="Salário teste",
    estimated_amount_cents=350000,
    day_of_month=5,
    account_id=1,
)

print("Criado:", template_id)
print(service.buscar_por_id(template_id))