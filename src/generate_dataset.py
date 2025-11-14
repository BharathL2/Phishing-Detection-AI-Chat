"""
Generate a synthetic phishing/clean dataset for demos.
Writes CSV to data/sample_dataset.csv with columns: text,label
Usage:
  python src/generate_dataset.py --n 1500 --seed 42
"""
import os
import csv
import random
import argparse

PHISH_URGENCY = [
    "URGENT", "IMMEDIATELY", "ACTION REQUIRED", "LAST WARNING", "FINAL NOTICE",
    "ACCOUNT ALERT", "SECURITY ALERT", "YOUR ACCOUNT EXPIRES", "VERIFY NOW",
]
PHISH_ACTION = [
    "Click here", "Verify your account", "Reset your password", "Update billing info",
    "Confirm your identity", "Login to continue", "Submit your details",
]
PHISH_REWARD = [
    "You won $5000", "Claim your free reward", "Crypto giveaway", "Exclusive offer",
    "Limited time prize", "Cashback available", "Refund available",
]
PHISH_THREAT = [
    "Your account will be suspended", "Your subscription will be cancelled",
    "Unusual login detected", "Payment declined", "Overcharged invoice",
    "Package on hold due to customs",
]
PHISH_SERVICES = [
    "PayPal", "Bank of America", "Netflix", "Amazon", "DHL", "FedEx", "Microsoft",
    "Google", "Apple", "IRS", "HMRC",
]
PHISH_LINKS = [
    "http://secure-login.example", "http://verify-payments.example", "http://192.168.1.1/login",
    "http://account-update.example", "http://billing-secure.example", "http://dhl-payments.example",
    "http://paypal-secure-login.example", "http://bank-update.example",
]

CLEAN_TOPICS = [
    "Team meeting scheduled", "Lunch plans", "Project update", "Vacation request",
    "Weekly report", "Birthday wishes", "Invoice paid", "Server maintenance",
    "Onsite schedule", "Training session",
]
CLEAN_CONTENT = [
    "Let's meet tomorrow at 2 PM.", "Please review the attached notes.",
    "Thanks for the presentation yesterday.", "The server will be updated on Sunday.",
    "Reminder to submit timesheets by Friday.", "Looking forward to our 1:1 next week.",
    "Great work on the release.", "Can we reschedule to Wednesday?",
]
CLEAN_ENDINGS = [
    "Thanks!", "Regards,", "Cheers", "Best regards", "See you soon", "Have a nice day",
]

PHISH_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq"]


def make_phishing(r: random.Random) -> str:
    service = r.choice(PHISH_SERVICES)
    u = r.choice(PHISH_URGENCY)
    a = r.choice(PHISH_ACTION)
    t = r.choice(PHISH_THREAT)
    rw = r.choice(PHISH_REWARD) if r.random() < 0.35 else ""
    link = r.choice(PHISH_LINKS)
    # Occasionally inject suspicious TLD by hyphenating a domain-like token
    if r.random() < 0.4:
        base = service.lower().replace(" ", "")
        link = f"http://{base}-secure{r.choice(PHISH_TLDS)}/login"
    parts = [
        f"{service} {u}! {t}.",
        f"{a} to continue.",
        f"{rw}" if rw else "",
        f"{link}",
    ]
    return " ".join(p for p in parts if p)


def make_clean(r: random.Random) -> str:
    topic = r.choice(CLEAN_TOPICS)
    body = r.choice(CLEAN_CONTENT)
    end = r.choice(CLEAN_ENDINGS)
    # Sometimes add time/date info
    extra = "" if r.random() < 0.5 else r.choice([
        "Meeting room A at 3 PM.",
        "Schedule shared on the calendar.",
        "See the doc in the shared drive.",
    ])
    parts = [topic + ":", body, extra, end]
    return " ".join(p for p in parts if p)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1500, help="Total number of samples to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default=os.path.join("data", "sample_dataset.csv"))
    args = parser.parse_args()

    r = random.Random(args.seed)
    n = args.n
    n_phish = n // 2
    n_clean = n - n_phish

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        for _ in range(n_phish):
            writer.writerow([make_phishing(r), "phishing"])
        for _ in range(n_clean):
            writer.writerow([make_clean(r), "clean"])

    print(f"Wrote {n} rows to {args.out} (phishing={n_phish}, clean={n_clean})")


if __name__ == "__main__":
    main()
