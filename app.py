import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")


# ---------------------------------------
# Load data
# ---------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


df = load_data()
filtered = df.copy()


# ---------------------------------------
# Sidebar
# ---------------------------------------
st.sidebar.header("Filters")


# ---------- BRAND ----------
brands = ["All"] + sorted(df["Brand"].dropna().unique())
brand = st.sidebar.selectbox("Brand", brands)

if brand != "All":
    filtered = filtered[filtered["Brand"] == brand]


# ---------- OS ----------
oses = ["All"] + sorted(df["OS"].dropna().unique())
os_choice = st.sidebar.selectbox("OS", oses)

if os_choice != "All":
    filtered = filtered[filtered["OS"] == os_choice]


# ---------- CPU keyword ----------
cpu_keyword = st.sidebar.text_input("CPU contains")
if cpu_keyword:
    filtered = filtered[
        filtered["CPU"].str.contains(cpu_keyword, case=False, na=False)
    ]


# ---------------------------------------
# Checkbox filter helper
# ---------------------------------------
def checkbox_filter(df, column, label):
    st.sidebar.markdown(f"### {label}")

    values = sorted(df[column].dropna().unique())

    selected = []

    for v in values:
        if st.sidebar.checkbox(str(int(v)), value=True, key=f"{column}_{v}"):
            selected.append(v)

    if selected:
        df = df[df[column].isin(selected)]

    return df


# ---------- RAM ----------
filtered = checkbox_filter(filtered, "RAM", "RAM (GB)")

# ---------- STORAGE ----------
filtered = checkbox_filter(filtered, "Storage", "Storage (GB)")

# ---------- REFRESH RATE ----------
filtered = checkbox_filter(filtered, "Refresh_Rate", "Refresh Rate (Hz)")


# ---------------------------------------
# Sliders for continuous values
# ---------------------------------------
def slider_filter(df, column, label, step):
    col = df[column].dropna()
    if len(col) == 0:
        return df

    min_v = int(col.min())
    max_v = int(col.max())

    rng = st.sidebar.slider(label, min_v, max_v, (min_v, max_v), step=step)

    return df[df[column].between(*rng)]


filtered = slider_filter(filtered, "Battery", "Battery (mAh)", 100)
filtered = slider_filter(filtered, "Price", "Price", 100000)


# ---------- Resolution dropdown ----------
resolutions = ["All"] + sorted(df["Resolution"].dropna().unique())
res_choice = st.sidebar.selectbox("Resolution", resolutions)

if res_choice != "All":
    filtered = filtered[filtered["Resolution"] == res_choice]


# ---------------------------------------
# Results
# ---------------------------------------
st.subheader(f"Results: {len(filtered)} phones found")

if "Price" in filtered.columns:
    filtered = filtered.sort_values("Price")

st.dataframe(filtered, use_container_width=True)
