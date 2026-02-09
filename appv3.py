import streamlit as st
import pandas as pd

st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")


# =====================================================
# Styling
# =====================================================
st.markdown("""
<style>
div[data-baseweb="input"] > div {
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    border-radius: 10px;
}
div[data-baseweb="input"] > div:focus-within {
    box-shadow: 0 0 0 2px #4CAF50;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# Load + Clean + Score
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------
    # Brand normalization
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
    # Resolution normalization
    # -------------------------
    df["Resolution"] = (
        df["Resolution"]
        .astype(str)
        .str.lower()
        .str.replace("×", "x")
        .str.replace(" ", "")
    )

    # -------------------------
    # Remove unrealistic specs
    # -------------------------
    df = df[(df["RAM"].between(4, 24)) | df["RAM"].isna()]
    df = df[(df["Storage"].between(16, 2048)) | df["Storage"].isna()]

    # =================================================
    # 🔥 SPEC-BASED TIER SCORING (NEW)
    # =================================================

    def norm(series):
        """normalize 0-1"""
        return (series - series.min()) / (series.max() - series.min())

    df["score"] = (
        norm(df["RAM"]) * 0.35 +
        norm(df["Storage"]) * 0.20 +
        norm(df["Refresh_Rate"].fillna(60)) * 0.15 +
        norm(df["Battery"].fillna(df["Battery"].median())) * 0.10 +
        norm(df["Price"]) * 0.20
    ) * 100

    def tier(score):
        if score < 25:
            return "Entry-level"
        elif score < 50:
            return "Mid-range"
        elif score < 75:
            return "Premium"
        else:
            return "Flagship"

    df["Tier"] = df["score"].apply(tier)

    return df


df = load_data()
filtered = df.copy()


# =====================================================
# Sidebar Filters
# =====================================================
st.sidebar.header("Filters")


# Brand
brands = ["All"] + sorted(df["Brand"].dropna().unique())
brand = st.sidebar.selectbox("Brand", brands)
if brand != "All":
    filtered = filtered[filtered["Brand"] == brand]


# OS
oses = ["All"] + sorted(df["OS"].dropna().unique())
os_choice = st.sidebar.selectbox("OS", oses)
if os_choice != "All":
    filtered = filtered[filtered["OS"] == os_choice]


# 🔥 Tier (now spec-based)
tiers = ["All", "Entry-level", "Mid-range", "Premium", "Flagship"]
tier_choice = st.sidebar.selectbox("Performance Tier", tiers)

if tier_choice != "All":
    filtered = filtered[filtered["Tier"] == tier_choice]


# CPU search
cpu_keyword = st.sidebar.text_input("🔍 CPU search",
                                    placeholder="Snapdragon, Dimensity, A17...")

if cpu_keyword:
    filtered = filtered[
        filtered["CPU"].str.contains(cpu_keyword, case=False, na=False)
    ]


# =====================================================
# Checkbox filters
# =====================================================
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


filtered = checkbox_filter(filtered, "RAM", "RAM (GB)")
filtered = checkbox_filter(filtered, "Storage", "Storage (GB)")
filtered = checkbox_filter(filtered, "Refresh_Rate", "Refresh Rate (Hz)")


# =====================================================
# Sliders
# =====================================================
def slider_filter(df, column, label, step):
    col = df[column].dropna()
    if len(col) == 0:
        return df

    min_v, max_v = int(col.min()), int(col.max())
    rng = st.sidebar.slider(label, min_v, max_v, (min_v, max_v), step=step)

    return df[df[column].between(*rng)]


filtered = slider_filter(filtered, "Battery", "Battery (mAh)", 100)
filtered = slider_filter(filtered, "Price", "Price", 100000)


# =====================================================
# Results
# =====================================================
st.subheader(f"Results: {len(filtered)} phones found")
filtered = filtered.sort_values("score", ascending=False)

st.dataframe(filtered, use_container_width=True)


# =====================================================
# Download
# =====================================================
if len(filtered) > 0:
    st.download_button(
        "📥 Download filtered phones (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"phones_{len(filtered)}_results.csv",
        mime="text/csv"
    )
