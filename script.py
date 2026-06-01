from modules.finance.services.credit_card_service import CreditCardService

service = CreditCardService("default")

print("=== CARTÕES ATIVOS ===")

for card in service.listar_cartoes_ativos():
    print(card)