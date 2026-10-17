
import os
from pathlib import Path

from google import genai
from dotenv import load_dotenv

from calculations import (
    calculate_total,
    calculate_balance,
    calculate_category_totals,
    find_highest_category,
)

# Load the .env file from this project's folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)


def summarize_expenses(expenses, budget):
    if not expenses:
        return "No expenses recorded yet. Add some expenses to get a summary."

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "GEMINI_API_KEY was not found. "
            "Check that your .env file is in the project folder "
            "and the variable name matches exactly."
        )

    total = calculate_total(expenses)
    balance = calculate_balance(budget, total)
    categories = calculate_category_totals(expenses)
    highest = find_highest_category(expenses)

    category_text = "\n".join(
        f"{category}: ₹{amount:.2f}"
        for category, amount in categories.items()
    )

    prompt = f"""
Create a concise student expense report.

Total spent: ₹{total:.2f}
Budget: ₹{budget:.2f}
Remaining balance: ₹{balance:.2f}
Highest spending category: {highest or "None"}

Spending by category:
{category_text}

Include:
1. A brief overview.
2. The highest spending category.
3. Two practical saving suggestions.

Use only the supplied figures. Do not invent transactions.
Explain that a negative balance means the budget was exceeded.
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash"),
            contents=prompt,
        )

        if response.text:
            return response.text

        return "The AI returned an empty summary."

    except Exception as error:
        print(
            f"Summarizer error: {type(error).__name__}: {error}",
            flush=True,
        )
        return (
            f"Summary generation failed: {type(error).__name__}: {error}"
        )
