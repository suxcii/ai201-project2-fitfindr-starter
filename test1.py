from tools import search_listings, suggest_outfit
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

results = search_listings('vintage graphic tee', size='M', max_price=30)
top_item = results[0]
print('Item:', top_item['title'])
print()

# Test with example wardrobe
outfit1 = suggest_outfit(top_item, get_example_wardrobe())
print('=== With wardrobe ===')
print(outfit1)
print()

# Test with empty wardrobe
outfit2 = suggest_outfit(top_item, get_empty_wardrobe())
print('=== Empty wardrobe ===')
print(outfit2)