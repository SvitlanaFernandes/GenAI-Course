
from collections import defaultdict


def calculate_total(expenses):
    """Return the total amount spent."""
    return round(sum(float(e["amount"]) for e in expenses), 2)


def calculate_balance(budget, total_spent):
    """Return remaining budget. Negative means overspending."""
    return round(float(budget) - float(total_spent), 2)


def calculate_budget_percentage(total_spent, budget):
    """Return percentage of the budget used."""
    if budget <= 0:
        return 0.0
    return round((total_spent / budget) * 100, 2)


def calculate_category_totals(expenses):
    """Group expense amounts by category."""
    totals = defaultdict(float)

    for expense in expenses:
        totals[expense["category"]] += float(expense["amount"])

    return dict(totals)


def calculate_daily_average(expenses):
    """Average daily spending across days with recorded expenses."""
    if not expenses:
        return 0.0

    daily_totals = defaultdict(float)

    for expense in expenses:
        daily_totals[str(expense["date"])] += float(expense["amount"])

    return round(sum(daily_totals.values()) / len(daily_totals), 2)


def find_highest_category(expenses):
    """Return the highest spending category, or None."""
    totals = calculate_category_totals(expenses)

    if not totals:
        return None

    return max(totals, key=totals.get)
