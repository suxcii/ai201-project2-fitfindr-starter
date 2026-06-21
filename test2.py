from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe

# Tool 1
results = search_listings('vintage graphic tee', size='M', max_price=30)
top_item = results[0]
print('Item:', top_item['title'])
print()

# Tool 2
outfit = suggest_outfit(top_item, get_example_wardrobe())
print('=== Outfit ===')
print(outfit)
print()

# Tool 3
fit_card = create_fit_card(outfit, top_item)
print('=== Fit Card ===')
print(fit_card)