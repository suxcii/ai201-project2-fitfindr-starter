from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_empty_wardrobe

# Failure 1: search returns empty
print('=== Failure 1: impossible search ===')
results = search_listings('designer ballgown', size='XXS', max_price=5)
print(results)

# Failure 2: suggest_outfit with empty wardrobe
print()
print('=== Failure 2: empty wardrobe ===')
results2 = search_listings('vintage graphic tee', size=None, max_price=50)
print(suggest_outfit(results2[0], get_empty_wardrobe()))

# Failure 3: create_fit_card with empty outfit
print()
print('=== Failure 3: empty outfit string ===')
print(create_fit_card('', results2[0]))