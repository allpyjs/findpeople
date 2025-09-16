from get_urls import load_state_map, generate_urls
from scraper import scrape_url
from email_checker import is_possible_email, save_matched
import tkinter as tk
from tkinter import scrolledtext, messagebox

def run_gui():
    def run_scraper():
        city = entry_city.get().strip()
        state = entry_state.get().strip()
        names = text_names.get("1.0", tk.END).strip().splitlines()
        masked_email = entry_masked.get().strip()

        if not city or not state or not names or not masked_email:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            state_map = load_state_map()
            urls = generate_urls(names, city, state, state_map)

            print(f"Generated {len(urls)} urls, starting scraping one by one...")

            matched_emails = []

            for url in urls:
                emails = scrape_url(url)
                if not emails:
                    continue

                matched_email = is_possible_email(masked_email, emails)
                if matched_email != "no email":
                    save_matched(masked_email, matched_email)
                    matched_emails.append(matched_email)

            # Show results in GUI
            result_text.delete("1.0", tk.END)
            if matched_emails:
                result_text.insert(tk.END, "\n".join(matched_emails))
            else:
                result_text.insert(tk.END, "No match found")

        except Exception as e:
            messagebox.showerror("Error", str(e))


    root = tk.Tk()
    root.title("Email Scraper & Checker")

    tk.Label(root, text="City:").grid(row=0, column=0, sticky="w")
    entry_city = tk.Entry(root, width=30)
    entry_city.grid(row=0, column=1)

    tk.Label(root, text="State:").grid(row=1, column=0, sticky="w")
    entry_state = tk.Entry(root, width=30)
    entry_state.grid(row=1, column=1)

    tk.Label(root, text="Full Names (one per line):").grid(row=2, column=0, sticky="nw")
    text_names = scrolledtext.ScrolledText(root, width=40, height=5)
    text_names.grid(row=2, column=1)

    tk.Label(root, text="Masked Email:").grid(row=3, column=0, sticky="w")
    entry_masked = tk.Entry(root, width=40)
    entry_masked.grid(row=3, column=1)

    tk.Button(root, text="Run Scraper", command=run_scraper).grid(row=4, column=0, columnspan=2, pady=10)

    tk.Label(root, text="Matched Email:").grid(row=5, column=0, sticky="nw")
    result_text = scrolledtext.ScrolledText(root, width=40, height=5)
    result_text.grid(row=5, column=1)

    root.mainloop()
