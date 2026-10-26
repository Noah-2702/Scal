import re
from difflib import SequenceMatcher
CANNED = {
    "scam": (
        "Scal found several strong warning signs that match common scams.",
        ["Do not reply, click links, or send money",
         "Check with a family member or call the company using a number you already know"],
    ),
    "suspicious": (
        "A few things about this message look off, so it's best to be careful.",
        ["Don't click links or share personal information",
         "Check with someone you trust before doing anything"],
    ),
    "looks_safe": (
        "Scal didn't spot obvious warning signs, but it's always smart to stay careful.",
        ["If you weren't expecting this message, contact the sender using a number you already know"],
    ),
}


def build_result(verdict, flags, score):
    explanation, steps = CANNED[verdict]
    return {
        "verdict": verdict,
        "red_flags": [] if verdict == "looks_safe" else flags,
        "explanation": explanation,
        "next_steps": steps,
        "score": score,
    }


# Each rule takes the message text and returns (points, "warning sign") or None.
def rule_payment_method(text):
    if re.search(r"\bgift\s*cards?\b|wire\s+transfer|\bbitcoin\b|\bcrypto(currency)?\b|\bzelle\b|\bcash\s*app\b|\bwestern\s+union\b|\bmoneygram\b|\bprepaid\b", text, re.I):
        return 40, "Asks for payment in gift cards, wire transfer, or crypto"

def rule_urgency(text):
    if re.search(r"act\s+now|final\s+notice|within\s+\d+\s+hours|\burgent(ly)?\b|\bimmediately\b|\bright\s+now\b|\bpay\s+now\b|\blast\s+chance\b|\bexpires?\b|\basap\b|\bverify\b.{0,30}\bnow\b", text, re.I):
        return 30, "Urgent language pushing you to act fast"

def rule_threat(text):
    if re.search(r"\b(frozen|suspended|locked|returned|arrest(ed)?|warrant|lawsuit|legal\s+action|deactivated)\b", text, re.I):
        return 30, "Threatens a bad outcome if you don't act"

def rule_short_link(text):
    if re.search(r"\b(bit\.ly|tinyurl\.com|ow\.ly|t\.co|goo\.gl|is\.gd|cutt\.ly|rb\.gy)\b", text, re.I):
        return 20, "Contains a shortened link that hides where it goes"

def rule_secrecy(text):
    if re.search(r"don['’]?t\s+tell|do\s+not\s+tell|keep\s+(this|it)\s+(a\s+secret|between\s+us|quiet)|our\s+secret", text, re.I):
        return 25, "Asks you to keep this secret"

def rule_sensitive_request(text):
    if re.search(r"\b(send|share|give|tell|provide|enter|confirm|verify|reply\s+with|read\s+(me|back))\b.{0,25}\b(password|ssn|social\s+security|account\s+number|pin|verification\s+code|one[- ]time\s+code|card\s+number)\b", text, re.I):
        return 35, "Asks for passwords, codes, or personal numbers"

BRANDS = {"usps": "usps.com", "irs": "irs.gov", "amazon": "amazon.com", "paypal": "paypal.com",
          "chase": "chase.com", "wellsfargo": "wellsfargo.com", "bankofamerica": "bankofamerica.com",
          "apple": "apple.com", "netflix": "netflix.com", "fedex": "fedex.com", "ups": "ups.com",
          "medicare": "medicare.gov"}
DOMAIN_RE = re.compile(r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})(?:[/\s?]|$)", re.I)
LEET = str.maketrans("0135@", "oiesa")   # amaz0n -> amazon

def rule_lookalike_domain(text):
    for host in DOMAIN_RE.findall(text):
        host = host.lower()
        parts = host.split(".")
        registered = ".".join(parts[-2:])
        if registered in BRANDS.values():      # a real, official site: never flag it
            continue
        label = parts[-2].translate(LEET)
        pieces = label.split("-")
        for brand in BRANDS:
            close = any(len(p) > 3 and SequenceMatcher(None, p, brand).ratio() >= 0.8 for p in pieces)
            if brand in label.replace("-", "") or close:
                return 45, "Link pretends to be " + brand.upper() + " but isn't the real site"

def rule_odd_link(text):
    for host in DOMAIN_RE.findall(text):
        h = host.lower()
        if h.endswith((".xyz", ".top", ".click", ".info", ".live", ".icu")) or \
           ("-" in h and re.search(r"verify|secure|login|update|account|redeliver|claim", h)):
            return 25, "Link looks unusual or built to imitate a real site"

RULES = [rule_payment_method, rule_urgency, rule_threat, rule_short_link, rule_secrecy,
         rule_sensitive_request, rule_lookalike_domain, rule_odd_link]


# Quick scanner
def quick_scan(text):
    score, flags = 0, []
    for rule in RULES:
        hit = rule(text)
        if hit:
            pts, flag = hit
            score += pts
            flags.append(flag)
    score = min(score, 100)
    verdict = "scam" if score >= 60 else "suspicious" if score >= 25 else "looks_safe"
    return build_result(verdict, flags, score)


if __name__ == "__main__":
    for t in ["I need $800 in gift cards now", "Your dentist appointment is Tuesday at 3pm",]:
        print(t, "->", quick_scan(t)["verdict"])