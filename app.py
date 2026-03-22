import streamlit as st
import pandas as pd
import os

# TEMP DATA (works without eBay API)
def get_ebay_sales(query):
    return [
        ("Sample Sale 1", 45.0),
        ("Sample Sale 2", 50.0),
        ("Sample Sale 3", 55.0),
    ]

# FILE
INVENTORY_FILE = "inventory.csv"

# PAGE CONFIG
st.set_page_config(page_title="Dubz Card Haven", layout="centered")

# STYLE
st.markdown("""
<style>
.big-price {font-size: 48px; font-weight: bold; text-align:center; color:#FFD700;}
.card-box {padding:12px; border-radius:12px; background:#1c1f26; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# LOGO
st.image("logo.png", use_container_width=True)

# NAV
page = st.sidebar.selectbox("Menu", ["Comp Tool", "Inventory", "Dashboard"])

# INVENTORY FUNCTIONS
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    return pd.DataFrame(columns=["Card", "Condition", "Last Price"])

def save_inventory(df):
    df.to_csv(INVENTORY_FILE, index=False)

# ANALYZE
def analyze_card(card, condition):
    sales = get_ebay_sales(card)

    prices = [p for _, p in sales]
    avg = sum(prices) / len(prices)

    return round(avg, 2), sales


# COMP TOOL
if page == "Comp Tool":

    card = st.text_input("Search Card")
    condition = st.radio("", ["Raw", "PSA 10", "PSA 9"], horizontal=True)

    if st.button("Get Comps"):

        avg, sales = analyze_card(card, condition)

        st.markdown(f"<div class='big-price'>${avg}</div>", unsafe_allow_html=True)

        for title, price in sales:
            st.write(f"${price} - {title}")


# INVENTORY
if page == "Inventory":

    st.title("📦 Inventory")

    df = load_inventory()

    new_card = st.text_input("Card Name")
    new_condition = st.selectbox("Condition", ["Raw", "PSA 10", "PSA 9"])

    if st.button("Add Card"):
        new_row = pd.DataFrame([{
            "Card": new_card,
            "Condition": new_condition,
            "Last Price": 0
        }])
        df = pd.concat([df, new_row])
        save_inventory(df)

    if st.button("Update Prices"):
        prices = []

        for _, row in df.iterrows():
            avg, _ = analyze_card(row["Card"], row["Condition"])
            prices.append(avg)

        df["Last Price"] = prices
        save_inventory(df)

    for _, row in df.iterrows():
        st.write(f"{row['Card']} - ${row['Last Price']}")


# DASHBOARD
if page == "Dashboard":

    st.title("📊 Dashboard")

    df = load_inventory()

    total_value = df["Last Price"].sum()
    total_cards = len(df)

    st.metric("Total Value", f"${round(total_value,2)}")
    st.metric("Total Cards", total_cards)
