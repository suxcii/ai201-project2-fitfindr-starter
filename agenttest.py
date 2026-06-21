from agent import run_agent
from utils.data_loader import get_example_wardrobe

print('=== Happy path ===')
session = run_agent(
    query="vintage graphic tee under $30 size M",
    wardrobe=get_example_wardrobe(),
)
if session["error"]:
    print('Error:', session["error"])
else:
    print('Item:', session["selected_item"]["title"])
    print('Outfit:', session["outfit_suggestion"])
    print('Fit card:', session["fit_card"])

print()
print('=== No results path ===')
session2 = run_agent(
    query="designer ballgown size XXS under $5",
    wardrobe=get_example_wardrobe(),
)
print('Error:', session2["error"])