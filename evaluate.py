"""Compares three approaches on labeled test messages:
   1) rules only (scanner.py)  2) AI only (analyzer.py)  3) hybrid (both, merged like app.py)
Run from your scam-shield folder:  python evaluate.py
Tip: edit SCAMS and LEGIT to add messages YOU wrote. The AI column makes one API call per message."""
import time
from scanner import quick_scan
from analyzer import analyze_message, FALLBACK
import json, os

 
SCAMS = [
 "USPS: Your package is on hold due to an unpaid $1.99 fee. Pay now at usps-redelivery-help.com or it will be returned.",
 "Hi Grandma, it's me. I'm in trouble and need $800 in gift cards right now. Please don't tell Mom.",
 "ALERT: Unusual activity on your bank account. Verify your identity now at secure-bankverify.net or your account will be frozen.",
 "IRS FINAL NOTICE: You owe back taxes. A warrant will be issued unless you pay within 24 hours by wire transfer.",
 "Congratulations! You've won a $500 Walmart gift card. Claim your prize at walmart-rewards-claim.top before it expires.",
 "Your Medicare card is expiring. Reply with your Social Security number to get your new card mailed.",
 "Microsoft Support: Your computer is infected. Call 1-800-555-0123 immediately and do not turn off your PC.",
 "Hey it's your grandson, I got a new phone number. I was in a car accident and need bail money. Please send it via Zelle and don't tell Dad.",
 "Netfl1x: your payment failed and your account will be suspended. Update billing at netflix-billing-update.com now.",
 "Hello dear, I am a soldier overseas and I have fallen in love with you. I need money for a plane ticket to meet you.",
 "Amazon: Someone tried to sign in to your account. Confirm your password at amazon-security-check.com or it will be locked.",
 "Final warning: your PayPal account is limited. Verify your login details here: bit.ly/3xYzAbC",
 "I can double your investment in 7 days with my crypto trading system. Guaranteed returns, message me to start.",
 "Wrong number? Sorry! You seem like a nice person, let's be friends. I make great money from home, I can show you how.",
 "Your Social Security benefits have been suspended due to suspicious activity. Call this number now to reinstate them.",
 "You have an unclaimed package from FedEx. Schedule redelivery at fedex-delivery-schedule.info and pay a small $2 fee.",
]
LEGIT = [
 "Your dentist appointment is confirmed for Tuesday at 3pm. Reply C to confirm.",
 "Your Google verification code is 482913. Don't share it with anyone.",
 "Reminder: update your zip code at usps.com/zip before your package ships.",
 "Hey are you free for dinner Friday? Mom made lasagna.",
 "Your Amazon order has shipped. Track it at amazon.com/orders.",
 "Your Chase statement is ready. Sign in at chase.com to view it.",
 "CVS Pharmacy: Your prescription is ready for pickup. Reply STOP to opt out.",
 "Your electric bill of $84.20 is due on the 15th. Pay online at your utility's website or by phone.",
 "Mrs. Lopez, this is Dr. Kim's office. Please call us back at 555-0142 about rescheduling your visit.",
 "Thanks for shopping with us! Use your $10 gift card at checkout this weekend only.",
 "Your flight to Denver departs at 6:40am tomorrow. Check in now at united.com.",
 "School closed tomorrow due to weather. Classes resume Thursday.",
 "Your package was delivered to your front door at 2:14pm.",
 "Hi Dad, I'm running late, I'll call you in an hour. Love you!",
]
 
SEVERITY = {"looks_safe": 0, "suspicious": 1, "scam": 2}
 
def merge(local, ai):
    if ai is FALLBACK:
        return local
    final = ai["verdict"]
    if local.get("score", 0) >= 60 and SEVERITY.get(final, 1) < 2:
        final = "scam"                      # strong local evidence overrides
    flags = [] if final == "looks_safe" else list(dict.fromkeys(local["red_flags"] + ai.get("red_flags", [])))
    base = ai if final == ai["verdict"] else local
    return {**base, "verdict": final, "red_flags": flags}
 
def run(messages):
    rows = []
    for m in messages:
        local = quick_scan(m)
        ai = analyze_message(m)
        time.sleep(1.5)                      # be gentle with the free-tier rate limit
        rows.append({"msg": m, "rules": local["verdict"], "ai": ai["verdict"] if ai is not FALLBACK else "ERROR",
                     "hybrid": merge(local, ai)["verdict"]})
    return rows
 
def summarize(name, rows, is_scam):
    print(f"\n{name}")
    for mode in ("rules", "ai", "hybrid"):
        if all(r[mode] == "ERROR" for r in rows):
            continue
        flagged = sum(1 for r in rows if r[mode] in ("suspicious", "scam"))
        pct = 100 * flagged / len(rows)
        label = "caught" if is_scam else "false alarms"
        print(f"  {mode:7s} {label}: {flagged}/{len(rows)} ({pct:.0f}%)")
 
if __name__ == "__main__":
    scam_rows, legit_rows = run(SCAMS), run(LEGIT)
    summarize("SCAM MESSAGES (higher is better)", scam_rows, True)
    summarize("LEGITIMATE MESSAGES (lower is better)", legit_rows, False)
    print("\nDisagreements worth a look:")
    for r in scam_rows + legit_rows:
        if len({r["rules"], r["ai"]}) > 1:
            print(f"  rules={r['rules']:10s} ai={r['ai']:10s} hybrid={r['hybrid']:10s} | {r['msg'][:60]}")