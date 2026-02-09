import streamlit as st
import pandas as pd
import re

# ---------------------------
# Load dataset (cached)
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_csv("phones.csv")

df = load_data()


# ---------------------------
# Parse user text → preferences
# ---------------------------
def parse_query(text):
    text = text.lower()
    prefs = {}

    # brand
    brands = df["brand"].astype(str).str.lower().unique()
    for b in brands:
        if b in text:
            prefs["brand"] = b

    # RAM (e.g., 8GB)
    ram = re.search(r'(\d+)\s*gb', text)
    if ram:
        prefs["ram"] = int(ram.group(1))

    # Storage (128GB etc)
    storage = re.search(r'(\d+)\s*(gb|tb)\s*(storage)?', text)
    if storage:
        val = int(storage.group(1))
        if storage.group(2) == "tb":
            val *= 1024
        prefs["storage"] = val

    # Battery
    battery = re.search(r'(\d+)\s*mah', text)
    if battery:
        prefs["battery"] = int(battery.group(1))

    # Price under X juta/million
    price = re.search(r'(under|below|<)\s*(\d+)', text)
    if price:
        prefs["max_price"] = int(price.group(2)) * 1_000_000

    return prefs


# ---------------------------
# Filter dataset
# ---------------------------
def filter_phones(df, prefs):
    result = df.copy()

    if "brand" in prefs:
        result = result[result["brand"].str.lower() == prefs["brand"]]

    if "ram" in prefs:
        result = result[result["ram"] >= prefs["ram"]]

    if "storage" in prefs:
        result = result[result["storage"] >= prefs["storage"]]

    if "battery" in prefs:
        result = result[result["battery"] >= prefs["battery"]]

    if "max_price" in prefs:
        result = result[result["price"] <= prefs["max_price"]]

    return result


# ---------------------------
# UI
# ---------------------------
st.title("📱 Phone Finder AI")

st.write("Example:")
st.caption("Samsung 8GB RAM under 5 juta battery 5000mah")

query = st.text_input("Describe your ideal phone")

if st.button("Search"):
    prefs = parse_query(query)

    st.write("Detected preferences:", prefs)

    result = filter_phones(df, prefs)

    if len(result) == 0:
        st.warning("No phones match 😢")
    else:
        st.success(f"{len(result)} phones found")
        st.dataframe(result)
