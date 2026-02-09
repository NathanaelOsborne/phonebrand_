import streamlit as st
import pandas as pd
import re

# =====================================================
# Page
# =====================================================
st.set_page_config(page_title="CSV Phone Merger", layout="wide")
st.title("📂 Robust Phone Dataset Compare & Merge Tool")

st.write("""
Upload 2 CSV files.

This tool will:
✅ auto-detect Brand & Model  
✅ allow manual column selection if needed  
✅ normalize names  
✅ handle different schemas  
✅ find missing phones  
✅ merge distinct rows safely  
""")


# =====================================================
# Helpers
# =====================================================

def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower()
    return df


def find_col(df, keywords):
    for col in df.columns:
        for k in keywords:
            if k in col:
                return col
    return None


def normalize_text(x):
    """strong cleaning for matching"""
    x = str(x).lower()
    x = re.sub(r'[^a-z0-9]', '', x)  # remove spaces/symbols
    x = x.replace("5g", "")
    return x


# =====================================================
# Prepare dataframe (auto + manual fallback)
# =====================================================
def prepare(df, label):
    df = clean_columns(df)

    brand_candidates = ["brand", "manufacturer", "company"]
    model_candidates = ["model", "phone", "device", "name", "product"]

    brand_col = find_col(df, brand_candidates)
    model_col = find_col(df, model_candidates)

    # -------------------------
    # Manual fallback
    # -------------------------
    if not brand_col or not model_col:
        st.warning(f"⚠️ Could not auto-detect Brand/Model for {label}. Please select manually.")

        cols = list(df.columns)

        brand_col = st.selectbox(f"{label} → Select Brand column", cols, key=f"brand_{label}")
        model_col = st.selectbox(f"{label} → Select Model column", cols, key=f"model_{label}")

    # -------------------------
    # Create clean keys
    # -------------------------
    df["brand_clean"] = df[brand_col].astype(str).str.strip().str.title()
    df["model_clean"] = df[model_col].apply(normalize_text)

    df["key"] = df["brand_clean"] + "_" + df["model_clean"]

    return df


# =====================================================
# Upload
# =====================================================
file_a = st.file_uploader("Upload CSV A", type=["csv"])
file_b = st.file_uploader("Upload CSV B", type=["csv"])


# =====================================================
# Main logic
# =====================================================
if file_a and file_b:

    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)

    st.success("Files loaded successfully")

    df_a = prepare(df_a, "CSV A")
    df_b = prepare(df_b, "CSV B")

    keys_a = set(df_a["key"])
    keys_b = set(df_b["key"])

    # -----------------------------------------
    # Compare
    # -----------------------------------------
    missing_in_a = df_b[~df_b["key"].isin(keys_a)]
    missing_in_b = df_a[~df_a["key"].isin(keys_b)]

    # -----------------------------------------
    # Safe merge (handles diff columns)
    # -----------------------------------------
    merged = pd.concat([df_a, df_b], ignore_index=True, sort=False)
    merged_unique = merged.drop_duplicates(subset="key")

    # remove helper columns
    drop_cols = ["key", "brand_clean", "model_clean"]
    missing_in_a = missing_in_a.drop(columns=drop_cols, errors="ignore")
    missing_in_b = missing_in_b.drop(columns=drop_cols, errors="ignore")
    merged_unique = merged_unique.drop(columns=drop_cols, errors="ignore")

    # =================================================
    # Summary
    # =================================================
    st.markdown("### 📊 Summary")
    st.write(f"CSV A rows: {len(df_a)}")
    st.write(f"CSV B rows: {len(df_b)}")
    st.write(f"Unique merged rows: {len(merged_unique)}")

    # =================================================
    # Display
    # =================================================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f"Missing in A ({len(missing_in_a)})")
        st.dataframe(missing_in_a, use_container_width=True)

    with c2:
        st.subheader(f"Missing in B ({len(missing_in_b)})")
        st.dataframe(missing_in_b, use_container_width=True)

    with c3:
        st.subheader(f"Merged Unique ({len(merged_unique)})")
        st.dataframe(merged_unique, use_container_width=True)

    # =================================================
    # Download
    # =================================================
    st.download_button(
        "📥 Download merged_unique.csv",
        merged_unique.to_csv(index=False).encode("utf-8"),
        file_name="merged_unique_phones.csv",
        mime="text/csv"
    )


else:
    st.info("Upload both CSV files to begin.")
