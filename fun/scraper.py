from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def extract_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    emails = set()

    for li in soup.select("ul.showMore-list li"):
        span = li.find("span", class_="blur")
        if span and span.next_sibling:
            username = span.get_text(strip=True)
            domain = span.next_sibling.strip()
            emails.add(username + domain)

    return sorted(emails)

def scrape_url(url):
    """Scrape a single URL and return emails."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"Scraping: {url}")
        page.goto(url, timeout=60000)

        body_html = page.inner_html("body")
        emails = extract_emails(body_html)

        browser.close()
        return emails
