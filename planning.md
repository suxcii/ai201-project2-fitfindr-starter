# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
Searches the mock listings dataset for items that match what the user
is looking for. Filters by size and price if provided, then scores
each listing by how many keywords from the description appear in its
title, description, or style tags.

**Input parameters:**
- `description` (str): Keywords describing what the user wants
  (e.g. "vintage graphic tee", "cottagecore midi skirt")
- `size` (str | None): Size to filter by. Optional — if the user
  doesn't mention a size, this is None and size filtering is skipped.
- `max_price` (float | None): Maximum price the user will pay.
  Optional — if not mentioned, all prices are included.

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of listing dicts sorted by relevance (highest keyword overlap
first). Each dict has: id, title, description, category, style_tags,
size, condition, price, colors, brand, platform.
Returns an empty list if nothing matches.

**What happens if it fails or returns nothing:**
Returns an empty list — never raises an exception. The agent checks
for an empty result and stops early with a helpful message to the user
instead of proceeding to suggest_outfit with no item.

---

### Tool 2: suggest_outfit

**What it does:**
Takes the thrifted item found by search_listings and the user's 
existing wardrobe, then asks the LLM to suggest 1-2 complete outfits. 
If the wardrobe is empty, it gives general styling advice instead.

**Input parameters:**
- `new_item` (dict): The listing dict selected from search_listings 
  results — the item the user is considering buying.
- `wardrobe` (dict): The user's existing wardrobe with an 'items' key 
  containing a list of clothing items. Can be empty.

**What it returns:**
A non-empty string with outfit suggestions — either specific 
combinations using named wardrobe pieces, or general styling advice 
if the wardrobe is empty.

**What happens if it fails or returns nothing:**
If wardrobe is empty, skip personal recommendations and ask the LLM 
for general styling ideas instead. Never raise an exception or return 
an empty string

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes the outfit suggestion from suggest_outfit and the thrifted item 
details, then asks the LLM to write a 2-4 sentence Instagram/TikTok 
caption that sounds casual and authentic like a real OOTD post.

**Input parameters:**
- `outfit` (str): The outfit suggestion string returned by 
  suggest_outfit — describes the full look.
- `new_item` (dict): The listing dict from search_listings — 
  used to pull item name, price, and platform for the caption.


**What it returns:**
<!-- Describe the return value -->
A 2-4 sentence string that reads like a real social media caption. 
Mentions the item name, price, and platform once each. Sounds 
different each time due to higher LLM temperature.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit is empty or whitespace-only, return a descriptive error 
message string like "Could not generate fit card — no outfit 
suggestion was provided." Never raise an exception.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
The agent follows a fixed order — search_listings first, then 
suggest_outfit, then create_fit_card. The order is fixed because 
each tool builds on the previous one — you can't suggest an outfit 
without an item, and you can't write a caption without an outfit.
The only decision the agent makes is after search_listings — if it 
returns empty, the agent stops early and sets session["error"] 
instead of continuing.
---

## State Management

**How does information from one tool get passed to the next?**
The session dict acts as a notepad that holds all inputs and outputs 
in one place across the full run. Each tool writes its result to the 
session, and the next tool reads from it. At the end, run_agent() 
returns the whole session so app.py can unpack the item, outfit, 
fit card, and any error all at once into the three output panels.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |
## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Return empty list, 
|                 |                            | agent sets session["error"] 
|                 |                            | and stops early — never 
|                 |                            | proceeds to suggest_outfit |
| suggest_outfit  | Wardrobe is empty          | Don't crash — skip personal 
|                 |                            | recommendations and give 
|                 |                            | general styling advice 
|                 |                            | for the item instead |
| create_fit_card | Outfit input is missing    | Return a descriptive error 
|                 | or empty                   | string like "Could not 
|                 |                            | generate fit card — no 
|                 |                            | outfit was provided." 
|                 |                            | Never raise an exception |

---

## Architecture

## Architecture

User Input (natural language query + wardrobe choice)
         │
         ▼
┌─────────────────────────────────────────────────────┐
│                    run_agent()                       │
│                   (agent.py)                         │
│                                                      │
│  Step 1: Initialize session dict                     │
│          {query, parsed, search_results,             │
│           selected_item, wardrobe,                   │
│           outfit_suggestion, fit_card, error}        │
│                                                      │
│  Step 2: Parse query with regex                      │
│          → extract description, size, max_price      │
│                                                      │
│  Step 3: search_listings(description, size, price)   │
│          │                                           │
│          ├─ No results → set session["error"]        │
│          │               return session EARLY        │
│          │                                           │
│          └─ Results found → session["selected_item"] │
│                    │                                 │
│                    ▼                                 │
│  Step 4: suggest_outfit(selected_item, wardrobe)     │
│          │                                           │
│          ├─ Empty wardrobe → general styling advice  │
│          └─ Has wardrobe → specific outfit combos    │
│                    │                                 │
│                    ▼                                 │
│  Step 5: create_fit_card(outfit, selected_item)      │
│          │                                           │
│          ├─ Empty outfit → return error string       │
│          └─ Has outfit → Instagram caption           │
│                    │                                 │
│                    ▼                                 │
│         return completed session                     │
└─────────────────────────────────────────────────────┘
         │
         ▼
   handle_query() in app.py
         │
         ▼
┌────────────────────────────────────────────┐
│              Gradio UI                      │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ 🛍️ Top  │ │ 👗 Outfit│ │ ✨ Fit     │ │
│  │ listing  │ │  idea    │ │   card     │ │
│  └──────────┘ └──────────┘ └────────────┘ │
└────────────────────────────────────────────┘
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:


**Milestone 3 — Individual tool implementations:**


I used Claude to implement each tool individually. For Tool 1, I gave
Claude the spec from planning.md (inputs, return value, failure mode)
and asked it to implement search_listings() using load_listings() from
the data loader. I verified it by running test.py against 3 queries:
a vintage tee search, a size-filtered search, and an impossible search
that should return empty. For Tools 2 and 3, I gave Claude the tool
spec and wardrobe schema, then verified the LLM responses were
non-empty strings and handled edge cases (empty wardrobe, empty outfit).

**Milestone 4 — Planning loop and state management:**

I gave Claude the architecture diagram and planning loop section from
planning.md and asked it to implement run_agent() in agent.py using
regex to parse size and price from the query. I verified it by running
two test cases: a happy path query that found results and generated a
fit card, and a no-results query that returned a helpful error message
without crashing.

---

## A Complete Interaction (Step by Step)


**Example user query:** "vintage graphic tee under $30 size M"

**Step 1:**
run_agent() initializes the session dict and parses the query using
regex. It extracts: description="vintage graphic tee", max_price=30.0,
size="M". These are stored in session["parsed"].

**Step 2:**
search_listings("vintage graphic tee", size="M", max_price=30) is
called. It loads all 40 listings, filters to 9 items under $30 in
size M or S/M, scores each by keyword overlap with "vintage graphic
tee", and returns a sorted list. Top result: Y2K Baby Tee —
Butterfly Print at $18. Stored in session["search_results"] and
session["selected_item"].

**Step 3:**
suggest_outfit() is called with the Y2K Baby Tee and the example
wardrobe. The LLM receives the item details and the user's wardrobe
items and suggests two specific outfits — one with baggy straight-leg
jeans and chunky white sneakers, another with wide-leg khaki trousers
and black combat boots. Result stored in session["outfit_suggestion"].

**Step 4:**
create_fit_card() is called with the outfit suggestion and the Y2K
Baby Tee listing. The LLM generates a casual Instagram caption
mentioning the item name, $18 price, and Depop platform naturally.
Result stored in session["fit_card"].

**Final output to user:**
The Gradio UI displays three panels simultaneously:
- Top listing: Y2K Baby Tee, $18, Depop, Size S/M
- Outfit idea: two specific combinations using wardrobe pieces
- Fit card: "Just scored this adorable Y2K Baby Tee with a butterfly
  print on Depop for $18 and I'm obsessed!"