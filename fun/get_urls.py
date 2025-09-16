import json

def load_state_map(filename="state_map.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_urls(names, city, state_code, state_map):
    state_full = state_map.get(state_code.upper())
    if not state_full:
        raise ValueError(f"Unknown state code: {state_code}")

    state_slug = state_full.lower().replace(" ", "-")
    city_slug = city.lower().replace(" ", "-")

    urls = []
    for name in names:
        name_slug = name.strip().lower().replace(" ", "-")
        url = f"https://www.zabasearch.com/people/{name_slug}/{state_slug}/{city_slug}/"
        urls.append(url)
    return urls
