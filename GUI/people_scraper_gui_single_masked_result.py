import json
import time
from tkinter import Tk, Label, Entry, Text, Button, END
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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

def scrape_urls(urls):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        all_emails = set()
        for url in urls:
            try:
                page.goto(url)
                time.sleep(3)  # wait for content to load
                body_html = page.inner_html("body")
                emails = extract_emails(body_html)
                all_emails.update(emails)
            except:
                pass
        browser.close()
    return sorted(all_emails)

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
root.geometry("600x400")

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
