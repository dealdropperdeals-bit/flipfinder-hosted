from __future__ import annotations
import re
from typing import Any

FINANCING_PHRASES = [
    "down payment","easy financing","bad credit","no credit","buy here pay here",
    "weekly payment","bi weekly payment","monthly payment","call for price",
    "finance available","financing available","in house financing","guaranteed approval",
]
DEALER_PHRASES = [
    "dealer","dealership","we finance","call today","stock #","stock number",
    "schedule a test drive","visit our website","plus tax","doc fee","motors","auto sales","cars llc",
]
BAIT_MODELS = ["civic","accord","camry","corolla","rav4","cr-v","crv"]
PHONE_RE = re.compile(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}")
VIN_RE = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")

def norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())

def count_hits(text: str, phrases: list[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase in text]

def score_listing(payload: dict[str, Any]) -> tuple[int, str]:
    text = " | ".join([norm(payload.get("title")), norm(payload.get("description")), norm(payload.get("seller_name")), norm(payload.get("location"))])
    price = int(payload.get("price") or 0)
    year = int(payload.get("year") or 0)
    score = 0
    flags: list[str] = []

    if price <= 0:
        score += 80
        flags.append("No price")
    elif price <= 1500:
        score += 35
        flags.append("Placeholder price")

    if count_hits(text, FINANCING_PHRASES):
        score += 45
        flags.append("Financing bait")
    if count_hits(text, DEALER_PHRASES):
        score += 35
        flags.append("Dealer-like")
    if PHONE_RE.search(text):
        score += 10
        flags.append("Phone number")
    if VIN_RE.search(text):
        score += 10
        flags.append("VIN in text")

    if year >= 2018 and 1 <= price < 6000:
        score += 60
        flags.append("Impossible price")
    elif year >= 2015 and 1 <= price < 4500:
        score += 55
        flags.append("Impossible price")
    elif year >= 2012 and 1 <= price < 3000:
        score += 45
        flags.append("Highly suspect price")

    model_text = f"{norm(payload.get('title'))} {norm(payload.get('description'))}"
    if any(model in model_text for model in BAIT_MODELS):
        if year >= 2014 and 1 <= price < 5000:
            score += 25
            flags.append("Common bait model")

    return min(score, 100), ", ".join(dict.fromkeys(flags))

def opportunity_bucket(junk_score: int) -> str:
    if junk_score <= 20:
        return "best"
    if junk_score <= 45:
        return "review"
    return "junk"
