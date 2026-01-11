# logic.py
from dataclasses import dataclass
from typing import List, Dict

CCR_QUARTERLY_CAP = 2500.0

@dataclass
class Card:
    id: str
    name: str
    rate: float           # decimal, e.g., 0.0525 for 5.25%
    capped: bool = False
    notes: str = ""

@dataclass
class Recommendation:
    card: Card
    cashback: float
    reason: str

# Central card definitions
CARDS: Dict[str, Card] = {
    "CCR": Card(id="CCR", name="BofA Customized Cash Rewards", rate=0.0525, capped=True,
                notes="5.25% category cap quarterly"),
    "Elite": Card(id="Elite", name="BofA Premium Rewards Elite", rate=0.02625,
                  notes="Good fallback for many purchases"),
    "Amazon": Card(id="Amazon", name="Amazon Prime Visa", rate=0.05, notes="Uncapped on Amazon"),
    "Costco": Card(id="Costco", name="Costco Anywhere Visa", rate=0.04, notes="Gas purchases"),
}

def compute_cashback_for_card(card: Card, amount: float, ccr_remaining: float) -> float:
    amount = max(0.0, float(amount))
    ccr_remaining = max(0.0, float(ccr_remaining))
    if amount == 0:
        return 0.0
    if card.capped:
        applicable = min(amount, ccr_remaining)
        return applicable * card.rate
    return amount * card.rate

def get_recommendations(category: str, amount: float, ccr_remaining: float) -> List[Recommendation]:
    """Return sorted recommendations (best first) with estimated cashback and reason."""
    amount = max(0.0, float(amount))
    ccr_remaining = max(0.0, float(ccr_remaining))
    candidates: List[Recommendation] = []

    if "Amazon" in category:
        candidates.append(Recommendation(CARDS["Amazon"], compute_cashback_for_card(CARDS["Amazon"], amount, ccr_remaining),
                                         "Amazon merchant uncapped rate"))
        candidates.append(Recommendation(CARDS["CCR"], compute_cashback_for_card(CARDS["CCR"], amount, ccr_remaining),
                                         "If purchase qualifies for CCR category"))
    elif "Gas" in category:
        candidates.append(Recommendation(CARDS["Costco"], compute_cashback_for_card(CARDS["Costco"], amount, ccr_remaining),
                                         "Dedicated gas rate"))
        candidates.append(Recommendation(CARDS["Elite"], compute_cashback_for_card(CARDS["Elite"], amount, ccr_remaining),
                                         "Fallback Elite"))
    elif "Online" in category:
        # Combined split recommendation: use CCR up to remaining cap, remainder on Elite
        ccr_cash = compute_cashback_for_card(CARDS["CCR"], amount, ccr_remaining)
        remainder = max(0.0, amount - ccr_remaining)
        elite_cash_on_remainder = compute_cashback_for_card(CARDS["Elite"], remainder, 0.0)
        combined_total = ccr_cash + elite_cash_on_remainder
        combined_card = Card(id="CCR+Elite", name="Split: CCR then Elite", rate=0.0,
                             notes="Use CCR for up to remaining cap, remainder on Elite")
        candidates.append(Recommendation(combined_card, combined_total,
                                         f"Split: up to ${ccr_remaining:.0f} at 5.25%, remainder on Elite"))
        candidates.append(Recommendation(CARDS["CCR"], ccr_cash, "All on CCR (subject to cap)"))
        candidates.append(Recommendation(CARDS["Elite"], compute_cashback_for_card(CARDS["Elite"], amount, 0.0),
                                         "All on Elite"))
    else:
        # Generic fallback
        candidates.append(Recommendation(CARDS["Elite"], compute_cashback_for_card(CARDS["Elite"], amount, ccr_remaining),
                                         "General fallback"))
        candidates.append(Recommendation(CARDS["CCR"], compute_cashback_for_card(CARDS["CCR"], amount, ccr_remaining),
                                         "If category applies to CCR"))

    candidates.sort(key=lambda r: r.cashback, reverse=True)
    return candidates
