import streamlit as st
import pandas as pd
import os

# ==============================
# FILES
# ==============================
INVENTORY_FILE = "inventory.csv"
HISTORY_FILE = "value_history.csv"

# ==============================
# MOCK DATA
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
# 🎨 STYLE
# ==============================
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at top, #1a1f2b 0%, #0e1117 60%);
}

/* Bottom nav */
.nav {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #121826;
    padding: 10px;
    display: flex;
    justify-content: space-around;
    border-top: 1px solid rgba(255,255,255,0.1);
}

/* Card */
.card {
    background: linear-gradient(145deg, #1a1f2b, #232938);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}

/* Big price */
.big-price {
    font-size: 56px;
    font-weight: 900;
    text-align: center;
    color: #FFD700;
    text-shadow: 0 0 20px rgba(255,215,0,0.5);
}

/* Accent */
.small-text {
    color: #9ca3af;
    font-size: 12px;
}

/* Buttons */
button {
    border-radius: 12px !important;
    background: linear-gradient(135deg, #ff00cc, #3333ff) !important;
    color: white !important;
}

/* Fix bottom spacing */
.main {
    padding-bottom: 80px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.image("logo.png", use_container_width=True)

st.markdown("<h3 style='text-align:center;'>Dubz Card Haven</h3>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#00f5ff;'>Track • Analyze • Flip smarter</p>",
    unsafe_allow_html=True
)

# ==============================
# NAVIGATION STATE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "Comp Tool"

# ==============================
# PAGE SWITCH FUNCTION
# ==============================
def set_page(p):
    st.session_state.page = p

# ==============================
# INVENTORY FUNCTIONS
# ==============================
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        return pd.read_csv(INVENTORY_FILE)
    return pd.DataFrame(columns=["Card", "Condition", "Last Price"])

def save_inventory(df):
    df.to_csv(INVENTORY_FILE, index=False)

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
if st.session_state.page == "Comp Tool":

    card = st.text_input("Search Card")
    condition = st.radio("", ["Raw", "PSA 10", "PSA 9"], horizontal=True)

    if st.button("Get Comps"):

        avg, sales = analyze_card(card, condition)

        st.markdown(f"<div class='big-price'>${avg}</div>", unsafe_allow_html=True)

        for title, price in sales:
            st.markdown(f"""
            <div class="card">
                <b>${price}</b><br>
                <span class="small-text">{title}</span>
            </div>
            """, unsafe_allow_html=True)

# ==============================
# 📦 INVENTORY
# ==============================
if st.session_state.page == "Inventory":

    df = load_inventory()

    with st.expander("➕ Add Card"):
        new_card = st.text_input("Card Name")
        new_condition = st.selectbox("Condition", ["Raw", "PSA 10", "PSA 9"])

        if st.button("Add Card"):
            df = pd.concat([df, pd.DataFrame([{
                "Card": new_card,
                "Condition": new_condition,
                "Last Price": 0
            }])])
            save_inventory(df)

    if st.button("🔄 Update Prices"):
        prices = []
        for _, row in df.iterrows():
            avg, _ = analyze_card(row["Card"], row["Condition"])
            prices.append(avg)

        df["Last Price"] = prices
        save_inventory(df)

        total_value = df["Last Price"].sum()
        history_df = load_history()

        history_df = pd.concat([history_df, pd.DataFrame([{
            "Timestamp": pd.Timestamp.now(),
            "Total Value": total_value
        }])])

        save_history(history_df)

    for i, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([4,2,1,1])

        col1.markdown(f"<div class='card'><b>{row['Card']}</b><br><span class='small-text'>{row['Condition']}</span></div>", unsafe_allow_html=True)
        col2.markdown(f"<b style='color:#00f5ff;'>${row['Last Price']}</b>", unsafe_allow_html=True)

        if col3.button("✏️", key=f"edit_{i}"):
            st.session_state[f"edit_{i}"] = True

        if col4.button("🗑️", key=f"del_{i}"):
            df = df.drop(i)
            save_inventory(df)
            st.experimental_rerun()

        if st.session_state.get(f"edit_{i}", False):
            new_name = st.text_input("Edit Name", row["Card"], key=f"name_{i}")
            new_cond = st.selectbox("Condition", ["Raw","PSA 10","PSA 9"], key=f"cond_{i}")

            if st.button("Save", key=f"save_{i}"):
                df.loc[i, "Card"] = new_name
                df.loc[i, "Condition"] = new_cond
                save_inventory(df)
                st.session_state[f"edit_{i}"] = False
                st.experimental_rerun()

# ==============================
# 📊 DASHBOARD
# ==============================
if st.session_state.page == "Dashboard":

    df = load_inventory()

    total_value = df["Last Price"].sum()
    total_cards = len(df)

    st.markdown(f"<div class='card'><h3>Total Value</h3><div class='big-price'>${total_value}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'><h3>Total Cards</h3><div class='big-price'>{total_cards}</div></div>", unsafe_allow_html=True)

    history_df = load_history()

    if not history_df.empty:
        history_df["Timestamp"] = pd.to_datetime(history_df["Timestamp"])
        st.line_chart(history_df.set_index("Timestamp"))

# ==============================
# 📱 BOTTOM NAV
# ==============================
st.markdown("<div class='nav'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

if col1.button("🔍"):
    set_page("Comp Tool")

if col2.button("📦"):
    set_page("Inventory")

if col3.button("📊"):
    set_page("Dashboard")
