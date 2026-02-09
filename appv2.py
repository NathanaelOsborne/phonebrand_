import streamlit as st
import pandas as pd

# =====================================================
# Page config
# =====================================================
st.set_page_config(page_title="Phone Finder", layout="wide")
st.title("📱 Phone Recommender")


# =====================================================
# Styling (shadow inputs + cleaner UI)
# =====================================================
st.markdown("""
<style>

/* nicer input boxes */
div[data-baseweb="input"] > div {
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    border-radius: 10px;
    border: 1px solid #ddd;
}

/* focus glow */
div[data-baseweb="input"] > div:focus-within {
    box-shadow: 0 0 0 2px #4CAF50, 0 4px 12px rgba(0,0,0,0.25);
}

/* sidebar spacing */
section[data-testid="stSidebar"] .stMarkdown {
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# Load + CLEAN dataset
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("phones.csv")

    # -------------------------
    # Numeric conversion
    # -------------------------
    numeric_cols = ["RAM", "Storage", "Battery", "Refresh_Rate", "Price"]
    for c in numeric_cols:
        if c in df.columns:
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
    # 720 x 1280, 720×1280 → 720x1280
    # -------------------------
    def normalize_resolution(x):
        if pd.isna(x):
            return None

        x = str(x).lower().replace("×", "x").replace(" ", "")

        if "x" not in x:
            return x

        try:
            w, h = x.split("x")
            w, h = int(w), int(h)
            w, h = sorted([w, h])
            return f"{w}x{h}"
        except:
            return x

    df["Resolution"] = df["Resolution"].apply(normalize_resolution)

    # -------------------------
    # Remove impossible specs
    # -------------------------
    df = df[(df["RAM"].between(4, 24)) | (df["RAM"].isna())]
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
cpu_keyword = st.sidebar.text_input(
    "🔍 CPU search",
    placeholder="Snapdragon, Dimensity, A17, Exynos..."
)

if cpu_keyword:
    filtered = filtered[
        filtered["CPU"].str.contains(cpu_keyword, case=False, na=False)
    ]


# =====================================================
# Checkbox filters (discrete specs)
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
# Slider filters (continuous specs)
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

filtered = filtered.sort_values("Price", na_position="last")

st.dataframe(filtered, use_container_width=True)


# =====================================================
# Download CSV button
# =====================================================
if len(filtered) > 0:
    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download filtered phones (CSV)",
        data=csv,
        file_name=f"phones_{len(filtered)}_results.csv",
        mime="text/csv"
    )
