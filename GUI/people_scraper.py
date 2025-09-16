import json
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- Load state map from JSON ---
def load_state_map(state_file="state_map.json"):
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)

# --- URL Generation ---
def format_for_url(text: str) -> str:
    return text.strip().lower().replace(" ", "-")

def make_url(name, state_code, city, state_map):
    state_full = state_map.get(state_code.upper())
    if not state_full:
        raise ValueError(f"Invalid state code: {state_code}")
    return f"https://www.zabasearch.com/people/{format_for_url(name)}/{format_for_url(state_full)}/{format_for_url(city)}/"

def generate_urls(address_file="address.json", names_file="name.txt", state_file="state_map.json", output_file="urls.json"):
    state_map = load_state_map(state_file)

    with open(address_file, "r", encoding="utf-8") as f:
        address = json.load(f)
    city = address["City"]
    state = address["State"]

    with open(names_file, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    urls = [make_url(name, state, city, state_map) for name in names]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)

    print(f"✅ URLs generated in {output_file}")
    return urls

# --- Email Extraction ---
def extract_emails(html):
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

# --- Email Checker ---
def is_possible_email(masked_email, email_list):
    try:
        masked_user, masked_domain = masked_email.split('@')
        masked_domain_name, masked_tld = masked_domain.split('.', 1)
    except ValueError:
        return "invalid format"

    for email in email_list:
        try:
            user, domain = email.split('@')
            domain_name, tld = domain.split('.', 1)
        except ValueError:
            continue

        if len(user) != len(masked_user):
            continue
        if user[0] != masked_user[0] or user[-1] != masked_user[-1]:
            continue
        if len(domain_name) != len(masked_domain_name):
            continue
        if domain_name[0] != masked_domain_name[0] or domain_name[-1] != masked_domain_name[-1]:
            continue
        if tld != masked_tld:
            continue

        return email

    return "no email"

def check_masked_emails(masked_file="masked_emails.txt", emails_list=None, output_file="matched_emails.json"):
    if not os.path.exists(masked_file):
        print(f"❌ {masked_file} not found.")
        return

    with open(masked_file, "r", encoding="utf-8") as f:
        masked_emails = [line.strip() for line in f if line.strip()]

    results = {}
    for m in masked_emails:
        match = is_possible_email(m, emails_list)
        results[m] = match

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Matched masked emails saved in {output_file}")
    return results

# --- Main Workflow ---
if __name__ == "__main__":
    # Step 1: Generate URLs
    urls = generate_urls()

    # Step 2: Scrape emails
    emails = scrape_urls(urls)

    # Step 3: Check masked emails
    check_masked_emails(emails_list=emails)
