
import streamlit as st
import pandas as pd
from datetime import date

from database import add_expense, get_expenses, delete_expense
from calculations import (
    calculate_total,
    calculate_balance,
    calculate_budget_percentage,
    calculate_category_totals,
    calculate_daily_average,
    find_highest_category,
)
from chatbot import ask_expense_bot
from summarizer import summarize_expenses

st.set_page_config(
    page_title="Student Expense Tracker",
    page_icon="💰",
    layout="wide",
)

# Load CSS
try:
    with open("style.css", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )
except FileNotFoundError:
    pass

# Header
st.title("💰 Student Expense Tracker")
st.caption("Track spending. Understand habits. Save smarter.")

# Budget settings
if "budget" not in st.session_state:
    st.session_state.budget = 5000.0

with st.sidebar:
    st.header("⚙️ Budget Settings")
    st.number_input(
        "Monthly budget (₹)",
        min_value=0.0,
        step=100.0,
        key="budget",
    )
    st.caption("Expenses are stored in a local SQLite database.")

budget = st.session_state.budget

# Load expenses
all_expenses = get_expenses()

today = date.today()
month_start = today.replace(day=1)

expenses = get_expenses(
    start_date=month_start,
    end_date=today,
)

total = calculate_total(expenses)
balance = calculate_balance(budget, total)
percentage = calculate_budget_percentage(total, budget)

# Financial overview
st.subheader("📊 Financial Overview")

c1, c2, c3 = st.columns(3)

c1.metric("Total Spent This Month", f"₹{total:,.2f}")
c2.metric("Budget Remaining", f"₹{balance:,.2f}")
c3.metric("Transactions This Month", len(expenses))

if budget > 0:
    st.write(f"Budget used: {percentage:.1f}%")
    st.progress(min(percentage / 100, 1.0))

if balance < 0:
    st.error("You have exceeded your budget!")
elif budget > 0 and balance <= budget * 0.2:
    st.warning("Less than 20% of your budget remains.")

# Add expense
st.divider()
st.subheader("➕ Add an Expense")

with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0,
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Education",
            "Shopping",
            "Entertainment",
            "Health",
            "Other",
        ],
    )

    description = st.text_input("Description")
    expense_date = st.date_input("Expense date", value=today)

    submitted = st.form_submit_button(
        "Add Expense",
        use_container_width=True,
    )

    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than zero.")
        elif not description.strip():
            st.error("Enter an expense description.")
        else:
            add_expense(
                expense_date,
                description.strip(),
                category,
                amount,
            )
            st.success("Expense saved!")
            st.rerun()

# Expense history
st.divider()
st.subheader("🧾 Expense History")

if expenses:
    df = pd.DataFrame(expenses)

    display_df = df.rename(
        columns={
            "date": "Date",
            "description": "Description",
            "category": "Category",
            "amount": "Amount (₹)",
        }
    )

    st.dataframe(
        display_df.drop(columns=["id"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
    )

    # Delete expense
    with st.expander("Delete an expense"):
        options = {
            f'#{e["id"]} | {e["date"]} | '
            f'{e["description"]} | ₹{e["amount"]:.2f}': e["id"]
            for e in expenses
        }

        selected = st.selectbox(
            "Select an expense",
            options=list(options.keys()),
        )

        if st.button("Delete selected expense"):
            delete_expense(options[selected])
            st.rerun()

    # Spending by category
    st.subheader("📈 Spending by Category")
    category_totals = calculate_category_totals(expenses)

    if category_totals:
        chart_data = pd.Series(
            category_totals,
            name="Amount (₹)",
        )
        st.bar_chart(chart_data)

    # Extra statistics
    left, right = st.columns(2)

    left.metric(
        "Average per recorded day",
        f'₹{calculate_daily_average(expenses):,.2f}',
    )

    highest = find_highest_category(expenses)

    right.metric(
        "Highest Spending Category",
        highest or "None yet",
    )

else:
    st.info("No expenses this month. Add your first expense!")

# AI expense summary
st.divider()
st.subheader("📝 AI Expense Summary")

if st.button("Generate Summary"):
    with st.spinner("Preparing your summary..."):
        st.session_state.summary = summarize_expenses(
            expenses,
            budget,
        )

if "summary" in st.session_state:
    st.markdown(st.session_state.summary)

# Expense chatbot
st.divider()
st.subheader("🤖 Expense Assistant")

question = st.chat_input("Ask about your expenses...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_expense_bot(
                question,
                expenses,
                budget,
            )
        st.markdown(answer)

# Monthly balance sheet
st.divider()
st.subheader("📄 Monthly Balance Sheet")

balance_data = pd.DataFrame(
    [
        {"Item": "Monthly Budget", "Amount (₹)": budget},
        {"Item": "Total Expenses", "Amount (₹)": total},
        {"Item": "Remaining Balance", "Amount (₹)": balance},
    ]
)

st.dataframe(
    balance_data,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Student Expense Tracker | Python • Streamlit • SQLite • Gemini"
)
