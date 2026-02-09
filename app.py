import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    # ensure numeric columns are numeric
    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


df = load_data()


# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

filtered = df.copy()


# BRAND
brands = ["All"] + sorted(df["Brand"].dropna().unique())
brand = st.sidebar.selectbox("Brand", brands)

if brand != "All":
    filtered = filtered[filtered["Brand"] == brand]


# OS
oses = ["All"] + sorted(df["OS"].dropna().unique())
os_choice = st.sidebar.selectbox("OS", oses)

if os_choice != "All":
    filtered = filtered[filtered["OS"] == os_choice]


# CPU keyword search
cpu_keyword = st.sidebar.text_input("CPU contains")

if cpu_keyword:
    filtered = filtered[
        filtered["CPU"].str.contains(cpu_keyword, case=False, na=False)
    ]


# ---------- numeric sliders helper ----------
def slider_filter(df, column, label):
    col_data = df[column].dropna()
    if len(col_data) == 0:
        return df

    min_v = int(col_data.min())
    max_v = int(col_data.max())

    rng = st.sidebar.slider(label, min_v, max_v, (min_v, max_v))

    return df[df[column].between(*rng)]


# RAM
if "RAM" in df.columns:
    filtered = slider_filter(filtered, "RAM", "RAM (GB)")

# Storage
if "Storage" in df.columns:
    filtered = slider_filter(filtered, "Storage", "Storage (GB)")

# Battery
if "Battery" in df.columns:
    filtered = slider_filter(filtered, "Battery", "Battery (mAh)")

# Refresh rate
if "Refresh_Rate" in df.columns:
    filtered = slider_filter(filtered, "Refresh_Rate", "Refresh Rate (Hz)")

# Price
if "Price" in df.columns:
    filtered = slider_filter(filtered, "Price", "Price")


# Resolution dropdown
resolutions = ["All"] + sorted(df["Resolution"].dropna().unique())
res_choice = st.sidebar.selectbox("Resolution", resolutions)

if res_choice != "All":
    filtered = filtered[filtered["Resolution"] == res_choice]


# -----------------------------
# Results
# -----------------------------
st.subheader(f"Results: {len(filtered)} phones found")

# sort by price if available
if "Price" in filtered.columns:
    filtered = filtered.sort_values("Price")

st.dataframe(filtered, use_container_width=True)
