import json

def is_possible_email(masked_email, email_list):
    masked_user, masked_domain = masked_email.split('@')
    masked_domain_name, masked_tld = masked_domain.split('.', 1)

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

def save_matched(masked_email, matched_email, filename="matched_emails.json"):
    if matched_email == "no email":
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append({"masked": masked_email, "matched": matched_email})

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
