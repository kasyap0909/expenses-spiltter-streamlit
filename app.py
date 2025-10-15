import streamlit as st
import pandas as pd

# ----------------- Streamlit Setup -----------------
st.set_page_config(page_title="Expense Splitter", page_icon="💸", layout="centered")

st.title("💸 Expense Splitter")

# Initialize session state to store expenses
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ----------------- Functions -----------------
def add_expense(description, amount, paid_by, participants):
    st.session_state.expenses.append({
        "description": description,
        "amount": amount,
        "paidBy": paid_by,
        "participants": participants
    })

def calculate_balances(expenses):
    balances = {}
    for exp in expenses:
        split = exp["amount"] / len(exp["participants"])
        for p in exp["participants"]:
            balances[p] = balances.get(p, 0) - split
        balances[exp["paidBy"]] = balances.get(exp["paidBy"], 0) + exp["amount"]
    return balances

def calculate_settlements(balances):
    creditors = []
    debtors = []
    for person, bal in balances.items():
        if bal > 0:
            creditors.append({"name": person, "amount": bal})
        elif bal < 0:
            debtors.append({"name": person, "amount": -bal})

    settlements = []
    while creditors and debtors:
        creditors.sort(key=lambda x: x["amount"], reverse=True)
        debtors.sort(key=lambda x: x["amount"], reverse=True)

        creditor = creditors[0]
        debtor = debtors[0]
        amount = min(creditor["amount"], debtor["amount"])

        settlements.append(f"💰 {debtor['name']} pays ₹{amount:.2f} to {creditor['name']}")

        creditor["amount"] -= amount
        debtor["amount"] -= amount

        if creditor["amount"] == 0: creditors.pop(0)
        if debtor["amount"] == 0: debtors.pop(0)

    return settlements

# ----------------- UI -----------------
st.subheader("➕ Add New Expense")

with st.form("expense_form"):
    desc = st.text_input("Description")
    amount = st.number_input("Amount", min_value=1.0)
    paid_by = st.text_input("Paid By")
    participants = st.text_input("Participants (comma separated)")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if desc and amount and paid_by and participants:
            parts = [p.strip() for p in participants.split(",") if p.strip()]
            add_expense(desc, amount, paid_by, parts)
            st.success("Expense added successfully ✅")
        else:
            st.error("Please fill all fields!")

# ----------------- Show Expenses -----------------
st.subheader("📋 Expenses")
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    # Format participants as string
    df["participants"] = df["participants"].apply(lambda x: ", ".join(x))
    # Format amount with ₹
    df["amount"] = df["amount"].apply(lambda x: f"₹{x:.2f}")
    st.table(df)
else:
    st.info("No expenses yet.")

# ----------------- Summary -----------------
st.subheader("📊 Summary")
balances = calculate_balances(st.session_state.expenses)

if balances:
    for person, bal in balances.items():
        if bal > 0:
            st.markdown(f"✅ **{person} should receive ₹{bal:.2f}**")
        elif bal < 0:
            st.markdown(f"🔴 **{person} owes ₹{abs(bal):.2f}**")
        else:
            st.markdown(f"⚪ **{person} is settled up**")
else:
    st.info("No balances to calculate yet.")

# ----------------- Settlements -----------------
st.subheader("🤝 Settlements")
settlements = calculate_settlements(balances)

if settlements:
    for s in settlements:
        st.write(s)
else:
    st.success("🎉 Everyone is settled up!")

