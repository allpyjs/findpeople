from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os


def extract_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    emails = set()

    # Method 1: From <li><span class="blur">username</span>@domain
    for li in soup.select("ul.showMore-list li"):
        span = li.find("span", class_="blur")
        if span and span.next_sibling:
            username = span.get_text(strip=True)
            domain = span.next_sibling.strip()
            emails.add(username + domain)

    # Method 2: From JSON-LD structured data
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


def scrape_urls(urls):
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

        # Convert to sorted list
        email_list = sorted(all_emails)

        # Save TXT (one per line)
        with open("all_emails.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(email_list))

        # Save JSON (array only)
        with open("all_emails.json", "w", encoding="utf-8") as f:
            json.dump(email_list, f, indent=2)

        return email_list


if __name__ == "__main__":
    # Load URLs from urls.json
    if not os.path.exists("urls.json"):
        print("❌ urls.json not found. Please run your URL generator first.")
        exit(1)

    with open("urls.json", "r", encoding="utf-8") as f:
        urls = json.load(f)

    results = scrape_urls(urls)
    print("\n✅ Done. Emails saved in all_emails.txt and all_emails.json")
