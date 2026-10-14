"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # 1. Load every listing with load_listings().
    listings = load_listings()
    matching_items = []
    for item in listings:
        # item is a dictionary
        # 2. Filter by max_price and by size, when each is provided.
        if max_price is not None and size is not None:
            item_price = item["price"]
            item_size = item["size"].upper()
            if item_price <= max_price and item_size == size:
                matching_items.append(item)
                continue
        elif max_price is not None:
            item_price = item["price"]
            if item_price <= max_price:
                matching_items.append(item)
                continue
        elif size is not None:
            item_size = item["size"]
            if item_size == size:
                matching_items.append(item)
                continue
        else:
            matching_items = listings
            break
    #   3. Score what's left by keyword overlap with `description`.
    description = description.lower()
    words_description = description.split()
    words_set = set(words_description)

    scored_item = []
    scored_item_scores = []
    for item in matching_items:
        item_description = item["description"].lower()
        item_split = item_description.split()
        item_set = set(item_split)
    #         4. Drop anything scoring zero.       
        if len(item_set & words_set) == 0: #no common key words
            continue
        else:
            #Using auxilary array to keep track of scores for the clothing items. The position of the array is key.
            scored_item_scores.append(len(item_set & words_set))
            scored_item.append(item)

    #         5. Sort by score, highest first, and return the listing dicts —
    #            at most config.SEARCH_RESULT_LIMIT of them.
    organized_items = []
    while len(scored_item) > 0:
        #find highest score first
        highest = scored_item_scores.index(max(scored_item_scores))
        #Grab the dictionary in the primary array at the index
        highest_item = scored_item[highest]
        organized_items.append(highest_item)
        #remove the highest item from the dictionary
        del scored_item[highest]
        del scored_item_scores[highest]
    return organized_items


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.


    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    # TODO:
    #1. Check whether wardrobe['items'] is empty.
    system_instructions = "You are an expert stylist with over 10 years in the fashion industry. Given a dictionary that contains attribute about a new clothing item, your role is to take an existing wardrobe to create different clothing combinations with the new item and existing wardrobe. If the wardrobe is empty, give general styling advice. Input: item (dictionary), wardrobe (array of dictionaries). Output: suggestions (string) "
    prompt = ""
    if wardrobe["items"] is None:
    #   2. If it is, ask the model for general styling ideas for this item.
        prompt = f"Using the provided clothing item as a base, provide general styling ideas that suit this item. Here is the item: {new_item}."
    else:
    #   3. If it isn't, format the wardrobe items into the prompt and ask for
    #            specific combinations naming pieces the user already owns.
        prompt = f"Using the provided clothing item, create different outfit combinations with items that also exist in the wadrobe. Here is the item: {new_item}. Here is my wardrobe: {wardrobe["items"]}"
    #4. Return the model's response.
    return generate(prompt, system_instructions)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    #  TODO:
    # 1. Guard against an empty or whitespace-only `outfit`.
    if outfit == "" or outfit == " ":
        return "No outfit suggestion found."
    # 2. Build a prompt with the item details and the outfit.
    prompt = "Given a outfit and a new clothing item, create a two-to-four sentence caption that will draw people's attention. Here are the inputs: {outfit} (string), {new_item} (dictionary). Here is the expected output: A two-to-four sentence caption (string)"
    system_instructions = "You are an expert social media manager with over 10 years of experience. You excel in capturing an audience's attention with captivating descriptions. Your role is to create captions for social media postsabout the outfit and new clothing item of the user. Constraints: 1. The caption should read like a real post rather than a product description 2. Mention the item once 3. Mention the item's price once 4. Mention the item's platform once 5. Be specific about the outfit's vibe"
    # 3. Call generate() and return the response.
    return generate(prompt, system_instructions)

