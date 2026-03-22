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

# ==============================
# 🎨 PREMIUM STYLE
# ==============================
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0e1117, #121826);
}

/* Big price */
.big-price {
    font-size: 56px;
    font-weight: 900;
    text-align: center;
    color: #FFD700;
    text-shadow: 0 0 15px rgba(255,215,0,0.4);
    margin-bottom: 15px;
}

/* Card UI */
.card {
    background: linear-gradient(145deg, #1a1f2b, #232938);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* Accent */
.accent {
    color: #00f5ff;
}

/* Small text */
.small-text {
    color: #9ca3af;
    font-size: 12px;
}

/* Buttons */
button {
    border-radius: 12px !important;
    border: none !important;
    background: linear-gradient(135deg, #ff00cc, #3333ff) !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Layout spacing */
.block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.image("logo.png", use_container_width=True)

st.markdown("<h3 style='text-align:center;'>Dubz Card Haven</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#00f5ff;'>Live Card Pricing • Inventory • Analytics</p>",
    unsafe_allow_html=True
)

# ==============================
# NAV
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
            st.markdown(f"""
            <div class="card">
                <div style='color:#FFD700; font-weight:700;'>${price}</div>
                <div class="small-text">{title}</div>
            </div>
            """, unsafe_allow_html=True)


# ==============================
# 📦 INVENTORY
# ==============================
if page == "Inventory":

    st.title("📦 Inventory")

    df = load_inventory()

    # ADD CARD
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

    # UPDATE PRICES + TRACK VALUE
    if st.button("🔄 Update Prices"):
        prices = []

        with st.spinner("Updating prices..."):
            for _, row in df.iterrows():
                avg, _ = analyze_card(row["Card"], row["Condition"])
                prices.append(avg)

        df["Last Price"] = prices
        save_inventory(df)

        total_value = df["Last Price"].sum()
        history_df = load_history()

        new_entry = pd.DataFrame([{
            "Timestamp": pd.Timestamp.now(),
            "Total Value": total_value
        }])

        history_df = pd.concat([history_df, new_entry], ignore_index=True)
        save_history(history_df)

        st.success("Prices updated!")

    st.divider()

    # SORT
    sort_option = st.selectbox("Sort By", ["Highest Value", "Lowest Value", "A-Z"])

    if sort_option == "Highest Value":
        df = df.sort_values(by="Last Price", ascending=False)
    elif sort_option == "Lowest Value":
        df = df.sort_values(by="Last Price", ascending=True)
    else:
        df = df.sort_values(by="Card")

    # DISPLAY + INLINE EDIT
    for i, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])

        with col1:
            st.markdown(f"""
            <div class="card">
                <b>{row['Card']}</b><br>
                <span class="small-text">{row['Condition']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div style='color:#00f5ff; font-weight:700;'>${row['Last Price']}</div>", unsafe_allow_html=True)

        with col3:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state[f"editing_{i}"] = True

        with col4:
            if st.button("🗑️", key=f"delete_{i}"):
                df = df.drop(i)
                save_inventory(df)
                st.experimental_rerun()

        if st.session_state.get(f"editing_{i}", False):

            new_name = st.text_input("Card Name", row["Card"], key=f"name_{i}")

            new_condition = st.selectbox(
                "Condition",
                ["Raw", "PSA 10", "PSA 9"],
                index=["Raw", "PSA 10", "PSA 9"].index(row["Condition"]),
                key=f"cond_{i}"
            )

            col_save, col_cancel = st.columns(2)

            if col_save.button("Save", key=f"save_{i}"):
                df.loc[i, "Card"] = new_name
                df.loc[i, "Condition"] = new_condition
                save_inventory(df)

                st.session_state[f"editing_{i}"] = False
                st.experimental_rerun()

            if col_cancel.button("Cancel", key=f"cancel_{i}"):
                st.session_state[f"editing_{i}"] = False
                st.experimental_rerun()

        st.divider()


# ==============================
# 📊 DASHBOARD
# ==============================
if page == "Dashboard":

    st.title("📊 Dashboard")

    df = load_inventory()

    total_value = df["Last Price"].sum()
    total_cards = len(df)

    st.markdown(f"""
    <div class="card">
        <h3>Total Value</h3>
        <div class="big-price">${round(total_value,2)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <h3>Total Cards</h3>
        <div class="big-price">{total_cards}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Top Cards")

    df_sorted = df.sort_values(by="Last Price", ascending=False)

    for _, row in df_sorted.head(5).iterrows():
        st.write(f"{row['Card']} - ${row['Last Price']}")

    st.divider()

    # VALUE GRAPH
    st.subheader("📈 Inventory Value Over Time")

    history_df = load_history()

    if not history_df.empty:
        history_df["Timestamp"] = pd.to_datetime(history_df["Timestamp"])
        history_df = history_df.sort_values("Timestamp")

        st.line_chart(history_df.set_index("Timestamp"))
    else:
        st.info("Update prices to start tracking value history.")
