import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")

# ---------------------------------
# Load data
# ---------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


df = load_data()
filtered = df.copy()


# ---------------------------------
# Sidebar filters
# ---------------------------------
st.sidebar.header("Filters")

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


# ---------------------------------
# Multi-select helper
# ---------------------------------
def multiselect_filter(df, column, label):
    values = sorted(df[column].dropna().unique())

    if len(values) == 0:
        return df

    selected = st.sidebar.multiselect(label, values, default=values)

    if selected:
        df = df[df[column].isin(selected)]

    return df


# RAM
filtered = multiselect_filter(filtered, "RAM", "RAM (GB)")

# STORAGE
filtered = multiselect_filter(filtered, "Storage", "Storage (GB)")

# REFRESH RATE
filtered = multiselect_filter(filtered, "Refresh_Rate", "Refresh Rate (Hz)")


# ---------------------------------
# Sliders (continuous values)
# ---------------------------------
def slider_filter(df, column, label, step=None):
    col = df[column].dropna()
    if len(col) == 0:
        return df

    min_v = int(col.min())
    max_v = int(col.max())

    rng = st.sidebar.slider(label, min_v, max_v, (min_v, max_v), step=step)

    return df[df[column].between(*rng)]


filtered = slider_filter(filtered, "Battery", "Battery (mAh)", step=100)
filtered = slider_filter(filtered, "Price", "Price", step=100000)


# ---------------------------------
# Resolution dropdown
# ---------------------------------
resolutions = ["All"] + sorted(df["Resolution"].dropna().unique())
res_choice = st.sidebar.selectbox("Resolution", resolutions)

if res_choice != "All":
    filtered = filtered[filtered["Resolution"] == res_choice]


# ---------------------------------
# Results
# ---------------------------------
st.subheader(f"Results: {len(filtered)} phones found")

if "Price" in filtered.columns:
    filtered = filtered.sort_values("Price")

st.dataframe(filtered, use_container_width=True)
