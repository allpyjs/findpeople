import json
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
    return text.strip().lower().replace(" ", "-")

def make_url(name, state_code, city):
    state_full = state_map.get(state_code.upper())
    if not state_full:
        raise ValueError(f"Invalid state code: {state_code}")
    return f"https://www.zabasearch.com/people/{format_for_url(name)}/{format_for_url(state_full)}/{format_for_url(city)}/"

def generate_urls(address_file="address.json", names_file="name.txt", output_file="urls.json"):
    # Load city/state
    with open(address_file, "r", encoding="utf-8") as f:
        address = json.load(f)
    city = address["City"]
    state = address["State"]

    # Load names
    with open(names_file, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    urls = [make_url(name, state, city) for name in names]

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)

    print(f"✅ URLs generated in {output_file}")
    return urls


def extract_emails(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    emails = set()

    # From blur spans
    for li in soup.select("ul.showMore-list li"):
        span = li.find("span", class_="blur")
        if span and span.next_sibling:
            username = span.get_text(strip=True)
            domain = span.next_sibling.strip()
            emails.add(username + domain)

    # From JSON-LD
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "email" in data:
                if isinstance(data["email"], list):
                    emails.update(data["email"])
                else:
                    emails.add(data["email"])
        except Exception:
            pass

    return emails


def scrape_urls(urls, txt_out="all_emails.txt", json_out="all_emails.json"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        all_emails = set()

        for url in urls:
            print(f"\nScraping: {url}")
            page.goto(url)

            body_html = page.inner_html("body")
            emails = extract_emails(body_html)
            all_emails.update(emails)

            print("Emails found:")
            for e in emails:
                print("  " + e)

        browser.close()

        email_list = sorted(all_emails)

        # Save TXT
        with open(txt_out, "w", encoding="utf-8") as f:
            f.write("\n".join(email_list))

        # Save JSON
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(email_list, f, indent=2)

        print(f"\n✅ Emails saved in {txt_out} and {json_out}")
        return email_list


if __name__ == "__main__":
    # Step 1: Generate URLs
    urls = generate_urls()

    # Step 2: Scrape emails
    scrape_urls(urls)
