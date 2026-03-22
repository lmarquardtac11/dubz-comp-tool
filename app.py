import streamlit as st
import pandas as pd
import os

# ==============================
# FILES
# ==============================
INVENTORY_FILE = "inventory.csv"
HISTORY_FILE = "value_history.csv"

# ==============================
# MOCK DATA (works without API)
# ==============================
def get_ebay_sales(query):
    return [
        ("Sample Sale 1", 45.0),
        ("Sample Sale 2", 50.0),
        ("Sample Sale 3", 55.0),
    ]

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Dubz Card Haven", layout="centered")

st.markdown("""
<style>
.big-price {font-size: 48px; font-weight: bold; text-align:center; color:#FFD700;}
.card-box {padding:12px; border-radius:12px; background:#1c1f26; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

st.image("logo.png", use_container_width=True)

# ==============================
# NAVIGATION
# ==============================
page = st.sidebar.selectbox("Menu", ["Comp Tool", "Inventory", "Dashboard"])

# ==============================
# INVENTORY FUNCTIONS
# ==============================
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    return pd.DataFrame(columns=["Card", "Condition", "Last Price"])

def save_inventory(df):
    df.to_csv(INVENTORY_FILE, index=False)

# ==============================
# HISTORY FUNCTIONS
# ==============================
def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame(columns=["Timestamp", "Total Value"])

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

# ==============================
# ANALYZE
# ==============================
def analyze_card(card, condition):
    sales = get_ebay_sales(card)

    prices = [p for _, p in sales]
    avg = sum(prices) / len(prices)

    return round(avg, 2), sales


# ==============================
# 🔍 COMP TOOL
# ==============================
if page == "Comp Tool":

    card = st.text_input("Search Card")
    condition = st.radio("", ["Raw", "PSA 10", "PSA 9"], horizontal=True)

    if st.button("Get Comps"):

        avg, sales = analyze_card(card, condition)

        st.markdown(f"<div class='big-price'>${avg}</div>", unsafe_allow_html=True)

        for title, price in sales:
            st.write(f"${price} - {title}")


# ==============================
# 📦 INVENTORY
# ==============================
if page == "Inventory":

    st.title("📦 Inventory")

    df = load_inventory()

    # ➕ ADD CARD
    with st.expander("➕ Add Card"):
        new_card = st.text_input("Card Name")
        new_condition = st.selectbox("Condition", ["Raw", "PSA 10", "PSA 9"])

        if st.button("Add Card"):
            if new_card:
                new_row = pd.DataFrame([{
                    "Card": new_card,
                    "Condition": new_condition,
                    "Last Price": 0
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_inventory(df)
                st.success("Card added!")

    st.divider()

    # 🔄 UPDATE PRICES + TRACK VALUE
    if st.button("🔄 Update Prices"):
        prices = []

        with st.spinner("Updating prices..."):
            for _, row in df.iterrows():
                avg, _ = analyze_card(row["Card"], row["Condition"])
                prices.append(avg)

        df["Last Price"] = prices
        save_inventory(df)

        # 📈 TRACK TOTAL VALUE
        total_value = df["Last Price"].sum()
        history_df = load_history()

        new_entry = pd.DataFrame([{
            "Timestamp": pd.Timestamp.now(),
            "Total Value": total_value
        }])

        history_df = pd.concat([history_df, new_entry], ignore_index=True)
        save_history(history_df)

        st.success("Prices updated + value tracked!")

    st.divider()

    # 📊 SORT
    sort_option = st.selectbox("Sort By", ["Highest Value", "Lowest Value", "A-Z"])

    if sort_option == "Highest Value":
        df = df.sort_values(by="Last Price", ascending=False)
    elif sort_option == "Lowest Value":
        df = df.sort_values(by="Last Price", ascending=True)
    else:
        df = df.sort_values(by="Card")

    # 📋 DISPLAY
    for i, row in df.iterrows():

        col1, col2, col3 = st.columns([4, 2, 2])

        with col1:
            st.markdown(f"**{row['Card']}**")
            st.caption(row["Condition"])

        with col2:
            st.write(f"${row['Last Price']}")

        with col3:
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state["edit_index"] = i

        if st.button("Delete", key=f"delete_{i}"):
            df = df.drop(i)
            save_inventory(df)
            st.experimental_rerun()

    st.divider()

    # ✏️ EDIT
    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]

        st.subheader("Edit Card")

        edit_card = st.text_input("Card Name", df.loc[idx, "Card"])
        edit_condition = st.selectbox(
            "Condition",
            ["Raw", "PSA 10", "PSA 9"],
            index=["Raw", "PSA 10", "PSA 9"].index(df.loc[idx, "Condition"])
        )

        if st.button("Save Changes"):
            df.loc[idx, "Card"] = edit_card
            df.loc[idx, "Condition"] = edit_condition
            save_inventory(df)

            del st.session_state["edit_index"]
            st.success("Updated!")
            st.experimental_rerun()


# ==============================
# 📊 DASHBOARD
# ==============================
if page == "Dashboard":

    st.title("📊 Dashboard")

    df = load_inventory()

    total_value = df["Last Price"].sum()
    total_cards = len(df)

    st.metric("Total Value", f"${round(total_value,2)}")
    st.metric("Total Cards", total_cards)

    st.divider()

    st.subheader("Top Cards")

    df_sorted = df.sort_values(by="Last Price", ascending=False)

    for _, row in df_sorted.head(5).iterrows():
        st.write(f"{row['Card']} - ${row['Last Price']}")

    st.divider()

    # 📈 VALUE GRAPH
    st.subheader("📈 Inventory Value Over Time")

    history_df = load_history()

    if not history_df.empty:
        history_df["Timestamp"] = pd.to_datetime(history_df["Timestamp"])
        history_df = history_df.sort_values("Timestamp")

        st.line_chart(history_df.set_index("Timestamp"))
    else:
        st.info("Update prices to start tracking value history.")
