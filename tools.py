"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform
    """
    listings = load_listings()

    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.lower() not in listing["size"].lower():
            continue
        filtered.append(listing)

    keywords = description.lower().split()

    scored = []
    for listing in filtered:
        searchable = (
            listing["title"].lower() + " " +
            listing["description"].lower() + " " +
            " ".join(listing["style_tags"]).lower()
        )
        score = sum(1 for word in keywords if word in searchable)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [listing for score, listing in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:

    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Replace this with your implementation
    client = _get_groq_client()
    
    # Format the new item details for the prompt
    item_info = f"""
Item: {new_item['title']}
Category: {new_item['category']}
Style tags: {', '.join(new_item['style_tags'])}
Colors: {', '.join(new_item['colors'])}
Description: {new_item['description']}
"""

    # Step 1: Check if wardrobe is empty
    if not wardrobe['items']:
        # Step 2: Empty wardrobe — give general styling advice
        prompt = f"""You are a fashion stylist specializing in thrifted and secondhand fashion.
A user is considering buying this item:
{item_info}
Give them 1-2 outfit ideas using general wardrobe staples. 
Suggest what kinds of bottoms, shoes, and accessories would pair well with it.
Keep it casual and specific — mention actual clothing types and colors."""

    else:
        # Step 3: Wardrobe has items — suggest specific combinations
        wardrobe_list = "\n".join([
            f"- {item['name']} ({item['category']})"
            for item in wardrobe['items']
        ])
        prompt = f"""You are a fashion stylist specializing in thrifted and secondhand fashion.
A user is considering buying this item:
{item_info}
They already own these pieces:
{wardrobe_list}
Suggest 1-2 specific outfit combinations using the new item paired with 
pieces from their wardrobe. Name the exact pieces you are pairing together.
Keep it casual and specific."""

    # Step 4: Call the LLM and return response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
    


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Replace this with your implementation
    # Step 1: Guard against empty outfit string
    if not outfit or not outfit.strip():
        return "Could not generate fit card — no outfit suggestion was provided."

    client = _get_groq_client()

    # Step 2: Build the prompt
    prompt = f"""You are a fun, authentic social media fashion creator.
Write a 2-4 sentence Instagram/TikTok caption for this thrifted outfit.

Item found: {new_item['title']}
Price: ${new_item['price']}
Platform: {new_item['platform']}
Outfit: {outfit}

Rules:
- Sound like a real person posting an OOTD, not a product description
- Mention the item name, price, and platform once each naturally
- Capture the vibe in specific terms
- Keep it casual, fun, and authentic"""

    # Step 3: Call LLM with higher temperature for variety
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.9,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
