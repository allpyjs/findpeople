import json

# --- State Map ---
state_map = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming"
}

def format_for_url(text: str) -> str:
    """Convert text to lowercase and hyphen-separated for URL."""
    return text.strip().lower().replace(" ", "-")

def make_url(name, state_code, city):
    state_full = state_map.get(state_code.upper())
    if not state_full:
        raise ValueError(f"Invalid state code: {state_code}")
    
    return f"https://www.zabasearch.com/people/{format_for_url(name)}/{format_for_url(state_full)}/{format_for_url(city)}/"

# --- Load city/state ---
with open("address.json", "r", encoding="utf-8") as f:
    address = json.load(f)

city = address["City"]
state = address["State"]

# --- Load names ---
with open("name.txt", "r", encoding="utf-8") as f:
    names = [line.strip() for line in f if line.strip()]

# --- Generate URLs ---
urls = [make_url(name, state, city) for name in names]

# --- Save to txt ---
with open("urls.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(urls))

# --- Save to json ---
with open("urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=2)

print("✅ URLs generated in urls.txt and urls.json")
