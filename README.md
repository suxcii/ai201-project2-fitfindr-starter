# FitFindr — Starter Kit
FitFindr is a multi-tool AI agent that helps users find secondhand 
clothing and figure out how to style it. Given a natural language 
query, it searches a mock listings dataset, suggests outfit 
combinations using the user's existing wardrobe, and generates a 
shareable Instagram caption — all in one flow.
## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

Run the app:
```bash
python app.py
```

---

## Tool Inventory

### `search_listings(description, size, max_price)`
**Purpose:** Searches the mock listings dataset for items matching 
the user's description, with optional size and price filters.

**Inputs:**
- `description` (str): Keywords describing what the user wants
  e.g. "vintage graphic tee"
- `size` (str | None): Size to filter by, case-insensitive.
  None skips size filtering.
- `max_price` (float | None): Maximum price inclusive.
  None skips price filtering.

**Output:** A list of matching listing dicts sorted by keyword 
relevance, highest first. Each dict contains: id, title, 
description, category, style_tags, size, condition, price, 
colors, brand, platform. Returns an empty list if nothing matches.

---

### `suggest_outfit(new_item, wardrobe)`
**Purpose:** Given a thrifted item and the user's wardrobe, asks 
the LLM to suggest 1-2 complete outfit combinations. Falls back 
to general styling advice if the wardrobe is empty.

**Inputs:**
- `new_item` (dict): A listing dict from search_listings — the 
  item the user is considering buying.
- `wardrobe` (dict): A wardrobe dict with an 'items' key 
  containing a list of wardrobe item dicts. May be empty.

**Output:** A non-empty string with outfit suggestions.

---

### `create_fit_card(outfit, new_item)`
**Purpose:** Generates a 2-4 sentence Instagram/TikTok caption 
for the thrifted find. Uses higher LLM temperature so the output 
sounds different each time.

**Inputs:**
- `outfit` (str): The outfit suggestion string from suggest_outfit.
- `new_item` (dict): The listing dict for the thrifted item, used 
  to pull title, price, and platform for the caption.

**Output:** A casual, authentic caption string mentioning the item 
name, price, and platform once each. Returns a descriptive error 
message string if outfit is empty — never raises an exception.

---

## How the Planning Loop Works

The agent follows a fixed sequence but branches based on what each 
tool returns. Here is the conditional logic:

1. Initialize the session dict to track all inputs and outputs.
2. Parse the query using regex to extract description, size, and 
   max_price. Store in session["parsed"].
3. Call search_listings() with the parsed parameters. Store results 
   in session["search_results"].
   - If results is empty: set session["error"] to a helpful message 
     and return the session immediately. suggest_outfit and 
     create_fit_card are never called.
   - If results is not empty: set session["selected_item"] = 
     results[0] and continue.
4. Call suggest_outfit() with session["selected_item"] and the 
   wardrobe. Store in session["outfit_suggestion"].
5. Call create_fit_card() with session["outfit_suggestion"] and 
   session["selected_item"]. Store in session["fit_card"].
6. Return the completed session.

The key decision point is after step 3 — the agent's behavior 
differs based on whether search_listings found anything.

---

## State Management

All state is stored in a single session dict initialized at the 
start of each run_agent() call. Each tool writes its output to 
the session, and the next tool reads from it.

What is stored and when:
- session["parsed"] — set after regex parsing, before any tool call
- session["search_results"] — set after search_listings() returns
- session["selected_item"] — set to results[0] if search succeeded
- session["outfit_suggestion"] — set after suggest_outfit() returns
- session["fit_card"] — set after create_fit_card() returns
- session["error"] — set if any step fails, triggers early return

No tool receives hardcoded values — every input comes from the 
session. At the end, app.py unpacks the session into three Gradio 
output panels simultaneously.

---

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No listings match query | Returns empty list. Agent sets session["error"] to "No listings found for '[query]'. Try different keywords, a different size, or a higher budget." Returns session immediately without calling suggest_outfit or create_fit_card. |
| `suggest_outfit` | Wardrobe is empty | Does not crash. Detects empty wardrobe['items'] and sends a different prompt asking the LLM for general styling advice instead of wardrobe-specific combinations. Always returns a non-empty string. |
| `create_fit_card` | Outfit string is empty or whitespace | Returns "Could not generate fit card — no outfit suggestion was provided." without calling the LLM. Never raises an exception. |

**Concrete example from testing:**
Running `search_listings("designer ballgown", size="XXS", max_price=5)` 
returned `[]`. The agent set session["error"] to the helpful message 
above and returned immediately — session["fit_card"] remained None 
and neither suggest_outfit nor create_fit_card were called.

---

## Interaction Walkthrough

**User query:** "vintage graphic tee under $30 size M"

**Step 1 — Tool called:**
- Tool: `search_listings`
- Input: `description="vintage graphic tee", size="M", max_price=30.0`
- Why this tool: The agent always starts here — it needs an item 
  before it can suggest an outfit or write a caption.
- Output: List of 8 matching listings sorted by relevance. Top 
  result: Y2K Baby Tee — Butterfly Print, $18, Depop, size S/M.
  Stored in session["selected_item"].

**Step 2 — Tool called:**
- Tool: `suggest_outfit`
- Input: `new_item=session["selected_item"], wardrobe=get_example_wardrobe()`
- Why this tool: Item was found — the agent now passes it directly 
  into suggest_outfit along with the user's wardrobe. No re-entry.
- Output: "Pair the Y2K Baby Tee with the baggy straight-leg jeans 
  and chunky white sneakers for a relaxed look. Or combine with 
  wide-leg khaki trousers and black combat boots for an edgier vibe."
  Stored in session["outfit_suggestion"].

**Step 3 — Tool called:**
- Tool: `create_fit_card`
- Input: `outfit=session["outfit_suggestion"], new_item=session["selected_item"]`
- Why this tool: Outfit suggestion exists — agent passes it into 
  create_fit_card to generate a shareable caption.
- Output: "Just scored this Y2K Baby Tee with a butterfly print on 
  Depop for $18 and I'm obsessed. Paired with baggy jeans and chunky 
  sneakers — the contrast is everything."
  Stored in session["fit_card"].

**Final output to user:**
Three panels appear simultaneously in the Gradio UI:
- Left: item title, price, platform, size, condition, style tags
- Middle: the two outfit suggestions from the LLM
- Right: the Instagram caption

---

## Spec Reflection

**One way planning.md helped during implementation:**
Writing out the error handling table before coding forced a concrete 
decision about what each failure mode should actually do. For example, 
deciding that suggest_outfit should give general styling advice instead 
of crashing when the wardrobe is empty meant the LLM prompt had to 
branch — without the spec, that edge case would have been easy to 
miss until testing broke it.

**One divergence from your spec, and why:**
The spec described the planning loop as potentially deciding which 
tools to call dynamically. In practice the order is always fixed — 
search_listings → suggest_outfit → create_fit_card — because each 
tool requires the output of the previous one. The only real decision 
is whether to stop early after search_listings returns empty. This 
is simpler than the spec implied but correct for this use case.

---

## AI Usage

**Instance 1 — search_listings implementation:**
I gave Claude the Tool 1 spec block from planning.md (inputs, return 
value, failure mode) and asked it to implement search_listings() using 
load_listings() from the data loader. I reviewed the generated code 
before running it to confirm it filtered by all three parameters and 
handled the empty-results case. I then tested it with 3 queries — a 
keyword match, a size-filtered search, and an impossible search — 
before trusting it. I had to debug an indentation issue where the old 
return [] stub was still present above the new code.

**Instance 2 — planning loop implementation:**
I gave Claude the architecture diagram and Planning Loop + State 
Management sections from planning.md and asked it to implement 
run_agent() in agent.py. I verified the generated code branched 
correctly on empty search results and stored each tool output in 
the session dict. I added the regex query parsing myself after 
deciding it was cleaner than an LLM call for extracting size and 
price from the query string.