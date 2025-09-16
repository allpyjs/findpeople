import json
import time
from tkinter import Tk, Label, Entry, Text, Button, END
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import random

# --- Load state map ---
def load_state_map(state_file="state_map.json"):
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)

# --- URL generation ---
def format_for_url(text: str) -> str:
    return text.strip().lower().replace(" ", "-")

def make_url(name, state_code, city, state_map):
    state_full = state_map.get(state_code.upper())
    if not state_full:
        raise ValueError(f"Invalid state code: {state_code}")
    return f"https://www.zabasearch.com/people/{format_for_url(name)}/{format_for_url(state_full)}/{format_for_url(city)}/"

def generate_urls(names_list, city, state_code, state_map):
    urls = [make_url(name, state_code, city, state_map) for name in names_list if name.strip()]
    # Save urls.json
    with open("urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=2)
    return urls

# --- Email scraping ---
def extract_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    emails = set()
    for li in soup.select("ul.showMore-list li"):
        span = li.find("span", class_="blur")
        if span and span.next_sibling:
            emails.add(span.get_text(strip=True) + span.next_sibling.strip())
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and "email" in data:
                if isinstance(data["email"], list):
                    emails.update(data["email"])
                else:
                    emails.add(data["email"])
        except:
            pass
    return emails

import time
import random
import json
from playwright.sync_api import sync_playwright

def scrape_urls(urls, txt_out="all_emails.txt", json_out="all_emails.json",
                headless=False, wait_seconds=3, jitter=True):
    """
    Scrape a list of URLs. Visits each URL, waits for it to load, extracts emails,
    then waits `wait_seconds` (plus optional small jitter) before the next URL.

    Parameters:
      - urls: list of url strings
      - txt_out/json_out: filenames to save emails
      - headless: whether to run browser headless (False recommended when dealing with Cloudflare)
      - wait_seconds: base delay between requests (set to 3 for your request)
      - jitter: whether to add a small random +/- jitter to wait time
    """

    with sync_playwright() as p:
        # Launch non-headless by default to behave more like a real user
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
        )
        page = context.new_page()

        all_emails = set()

        for i, url in enumerate(urls, 1):
            try:
                print(f"[{i}/{len(urls)}] Navigating to: {url}")
                page.goto(url, timeout=30000)  # 30s timeout
                # Wait until network is idle (makes sure page has loaded resources)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)  # 15s
                except Exception:
                    # if it times out, proceed — sometimes networkidle never fires
                    pass

                body_html = page.inner_html("body")
                emails = extract_emails(body_html)  # your existing extractor
                all_emails.update(emails)

                print(f"  → Found {len(emails)} emails on this page")

            except Exception as e:
                print(f"  ! Error scraping {url}: {e}")

            # Delay before next URL
            if i < len(urls):
                base = float(wait_seconds)
                delay = base
                if jitter:
                    # small random jitter so it's not perfectly periodic
                    delay = base + random.uniform(-0.5, 0.5)
                    if delay < 0.5:
                        delay = 0.5
                print(f"  Waiting {delay:.2f}s before next URL...")
                time.sleep(delay)

        browser.close()

    email_list = sorted(all_emails)

    # Save files (overwrite)
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write("\n".join(email_list))
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(email_list, f, indent=2)

    print(f"\nSaved {len(email_list)} unique emails to {txt_out} and {json_out}")
    return email_list


# --- Email checker ---
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
        if len(user) != len(masked_user): continue
        if user[0] != masked_user[0] or user[-1] != masked_user[-1]: continue
        if len(domain_name) != len(masked_domain_name): continue
        if domain_name[0] != masked_domain_name[0] or domain_name[-1] != masked_domain_name[-1]: continue
        if tld != masked_tld: continue
        return email
    return "no email"

# --- GUI ---
def run_scraper():
    city = city_entry.get().strip()
    state = state_entry.get().strip().upper()
    names_text = names_input.get("1.0", END).strip()
    masked_email = masked_input.get().strip()

    if not city or not state or not names_text or not masked_email:
        result_field.delete("1.0", END)
        result_field.insert(END, "Please enter City, State, Names, and Masked Email.")
        return

    names_list = [line.strip() for line in names_text.splitlines() if line.strip()]
    state_map = load_state_map()

    try:
        urls = generate_urls(names_list, city, state, state_map)
    except ValueError as e:
        result_field.delete("1.0", END)
        result_field.insert(END, str(e))
        return

    emails = scrape_urls(urls)
    matched_email = is_possible_email(masked_email, emails)

    result_field.delete("1.0", END)
    result_field.insert(END, matched_email)

# --- Tkinter window ---
root = Tk()
root.title("People Scraper & Email Checker")
root.geometry("600x450")

Label(root, text="City:").pack()
city_entry = Entry(root, width=50)
city_entry.pack()

Label(root, text="State (2-letter code):").pack()
state_entry = Entry(root, width=10)
state_entry.pack()

Label(root, text="Full Names (one per line):").pack()
names_input = Text(root, height=10, width=60)
names_input.pack()

Label(root, text="Masked Email (single line):").pack()
masked_input = Entry(root, width=50)
masked_input.pack()

Button(root, text="Run Scraper & Check Email", command=run_scraper).pack(pady=10)

Label(root, text="Matched Email:").pack()
result_field = Text(root, height=3, width=70)
result_field.pack()

root.mainloop()
