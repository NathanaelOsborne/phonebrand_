import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="CSV Phone Merger", layout="wide")
st.title("📂 Robust Phone Dataset Compare & Merge Tool")


st.write("""
Upload 2 CSV files.

This tool will:
✅ auto-detect Brand & Model columns
✅ normalize names
✅ handle different schemas
✅ find missing phones
✅ merge distinct rows safely
""")


# =====================================================
# Helpers
# =====================================================

def clean_columns(df):
    """lowercase + strip column names"""
    df.columns = df.columns.str.strip().str.lower()
    return df


def find_col(df, candidates):
    """find matching column name automatically"""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def normalize_text(x):
    """strong cleaning for matching"""
    x = str(x).lower()
    x = re.sub(r'[^a-z0-9]', '', x)  # remove spaces/symbols
    x = x.replace("5g", "")
    return x


def prepare(df):
    df = clean_columns(df)

    brand_col = find_col(df, ["brand", "brand_name", "manufacturer"])
    model_col = find_col(df, ["model", "model_name", "phone", "device"])

    if not brand_col or not model_col:
        st.error("Could not detect Brand/Model columns automatically.")
        st.stop()

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
# Process
# =====================================================
if file_a and file_b:

    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)

    df_a = prepare(df_a)
    df_b = prepare(df_b)

    keys_a = set(df_a["key"])
    keys_b = set(df_b["key"])

    # -----------------------------------------
    # Compare
    # -----------------------------------------
    missing_in_a = df_b[~df_b["key"].isin(keys_a)]
    missing_in_b = df_a[~df_a["key"].isin(keys_b)]

    # -----------------------------------------
    # Merge safely (handles diff columns)
    # -----------------------------------------
    merged = pd.concat([df_a, df_b], ignore_index=True, sort=False)
    merged_unique = merged.drop_duplicates(subset="key")

    # remove helper cols
    drop_cols = ["key", "brand_clean", "model_clean"]
    merged_unique = merged_unique.drop(columns=drop_cols, errors="ignore")
    missing_in_a = missing_in_a.drop(columns=drop_cols, errors="ignore")
    missing_in_b = missing_in_b.drop(columns=drop_cols, errors="ignore")

    # =================================================
    # Display
    # =================================================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f"Missing in A ({len(missing_in_a)})")
        st.dataframe(missing_in_a)

    with c2:
        st.subheader(f"Missing in B ({len(missing_in_b)})")
        st.dataframe(missing_in_b)

    with c3:
        st.subheader(f"Merged Unique ({len(merged_unique)})")
        st.dataframe(merged_unique)

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
