from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

def extract_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    emails = set()

    # Extract from <li><span class="blur">username</span>@domain
    for li in soup.select("ul.showMore-list li"):
        span = li.find("span", class_="blur")
        if span and span.next_sibling:
            username = span.get_text(strip=True)
            domain = span.next_sibling.strip()
            emails.add(username + domain)

    return sorted(emails)

def scrape_urls(urls, save=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        all_emails = []

        for url in urls:
            print(f"\nScraping: {url}")
            page.goto(url, timeout=60000)

            body_html = page.inner_html("body")
            emails = extract_emails(body_html)
            all_emails.extend(emails)

        browser.close()

        if save:
            with open("all_emails.json", "w", encoding="utf-8") as f:
                json.dump(all_emails, f, indent=4)

            with open("all_emails.txt", "w", encoding="utf-8") as f:
                for e in all_emails:
                    f.write(e + "\n")

        return all_emails
