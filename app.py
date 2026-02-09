import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")


# =====================================================
# Load + Clean Data
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    # -------------------------
    # Ensure numeric types
    # -------------------------
    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------
    # BRAND normalization
    # vivo / VIVO / vivo  -> Vivo
    # -------------------------
    df["Brand"] = (
        df["Brand"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.title()
    )

    # -------------------------
    # OS normalization
    # -------------------------
    def normalize_os(x):
        x = str(x).lower()
        if "android" in x:
            return "Android"
        if "ios" in x or "iphone" in x:
            return "iOS"
        return x.title()

    df["OS"] = df["OS"].apply(normalize_os)

    # -------------------------
    # Remove impossible specs
    # -------------------------
    df = df[(df["RAM"].between(4, 64)) | (df["RAM"].isna())]
    df = df[(df["Storage"].between(16, 2048)) | (df["Storage"].isna())]

    return df


df = load_data()
filtered = df.copy()


# =====================================================
# Sidebar Filters
# =====================================================
st.sidebar.header("Filters")


# -------------------------
# Brand dropdown
# -------------------------
brands = ["All"] + sorted(df["Brand"].dropna().unique())
brand = st.sidebar.selectbox("Brand", brands)

if brand != "All":
    filtered = filtered[filtered["Brand"] == brand]


# -------------------------
# OS dropdown
# -------------------------
oses = ["All"] + sorted(df["OS"].dropna().unique())
os_choice = st.sidebar.selectbox("OS", oses)

if os_choice != "All":
    filtered = filtered[filtered["OS"] == os_choice]


# -------------------------
# CPU search
# -------------------------
cpu_keyword = st.sidebar.text_input("CPU contains")

if cpu_keyword:
    filtered = filtered[
        filtered["CPU"].str.contains(cpu_keyword, case=False, na=False)
    ]


# =====================================================
# Checkbox filters (discrete values only)
# =====================================================
def checkbox_filter(df, column, label):
    st.sidebar.markdown(f"### {label}")

    values = sorted(df[column].dropna().unique())

    if len(values) == 0:
        return df

    selected = []

    for v in values:
        if st.sidebar.checkbox(str(int(v)), value=True, key=f"{column}_{v}"):
            selected.append(v)

    if selected:
        df = df[df[column].isin(selected)]

    return df


filtered = checkbox_filter(filtered, "RAM", "RAM (GB)")
filtered = checkbox_filter(filtered, "Storage", "Storage (GB)")
filtered = checkbox_filter(filtered, "Refresh_Rate", "Refresh Rate (Hz)")


# =====================================================
# Slider filters (continuous values)
# =====================================================
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


# -------------------------
# Resolution dropdown
# -------------------------
resolutions = ["All"] + sorted(df["Resolution"].dropna().unique())
res_choice = st.sidebar.selectbox("Resolution", resolutions)

if res_choice != "All":
    filtered = filtered[filtered["Resolution"] == res_choice]


# =====================================================
# Results
# =====================================================
st.subheader(f"Results: {len(filtered)} phones found")

if "Price" in filtered.columns:
    filtered = filtered.sort_values("Price")

st.dataframe(filtered, use_container_width=True)
