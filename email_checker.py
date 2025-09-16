import json

def is_possible_email(masked_email, email_list):
    # Split masked email
    masked_user, masked_domain = masked_email.split('@')
    masked_domain_name, masked_tld = masked_domain.split('.', 1)  # before and after first dot
    
    for email in email_list:
        try:
            user, domain = email.split('@')
            domain_name, tld = domain.split('.', 1)
        except ValueError:
            continue  # skip invalid email format

        # Check username rules
        if len(user) != len(masked_user):
            continue
        if user[0] != masked_user[0] or user[-1] != masked_user[-1]:
            continue

        # Check domain rules (only the name part, not TLD)
        if len(domain_name) != len(masked_domain_name):
            continue
        if domain_name[0] != masked_domain_name[0] or domain_name[-1] != masked_domain_name[-1]:
            continue

        # TLD must also match (like .com)
        if tld != masked_tld:
            continue

        return email  # Found match

    return "no email"


if __name__ == "__main__":
    # Load emails from all_emails.json
    with open("all_emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    # Example masked email
    masked = "e*******8@g***l.com"

    match = is_possible_email(masked, emails)
    print("Matched:", match)
