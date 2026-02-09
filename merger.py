import streamlit as st
import pandas as pd
import re

# =====================================================
# Page
# =====================================================
st.set_page_config(page_title="Phone Brand/Model Merger", layout="wide")
st.title("📂 Phone Brand + Model Compare & Merge Tool")

st.write("""
Upload 2 CSV files.

This simplified tool:
✅ auto-detect delimiter (, ; tab)
✅ lets you select Brand & Model columns
✅ ignores all other columns
✅ compares only Brand + Model
✅ shows missing phones
✅ merges distinct phones
""")


# =====================================================
# Helpers
# =====================================================

def smart_read(file):
    """auto-detect separator"""
    return pd.read_csv(file, sep=None, engine="python")


def normalize_model(x):
    """remove spaces/symbols for matching"""
    x = str(x).lower()
    x = re.sub(r'[^a-z0-9]', '', x)
    x = x.replace("5g", "")
    return x


def prepare(df, label):
    df.columns = df.columns.str.strip().str.lower()

    cols = list(df.columns)

    st.subheader(f"{label} column selection")

    brand_col = st.selectbox(f"{label} → Brand column", cols, key=f"brand_{label}")
    model_col = st.selectbox(f"{label} → Model column", cols, key=f"model_{label}")

    out = pd.DataFrame()

    out["Brand"] = df[brand_col].astype(str).str.strip().str.title()
    out["Model"] = df[model_col].astype(str).str.strip()

    out["key"] = out["Brand"] + "_" + out["Model"].apply(normalize_model)

    return out


# =====================================================
# Upload
# =====================================================
file_a = st.file_uploader("Upload CSV A", type=["csv"])
file_b = st.file_uploader("Upload CSV B", type=["csv"])


# =====================================================
# Main logic
# =====================================================
if file_a and file_b:

    df_a_raw = smart_read(file_a)
    df_b_raw = smart_read(file_b)

    st.success("Files loaded successfully")

    df_a = prepare(df_a_raw, "CSV A")
    df_b = prepare(df_b_raw, "CSV B")

    keys_a = set(df_a["key"])
    keys_b = set(df_b["key"])

    # -----------------------------------------
    # Compare sets
    # -----------------------------------------
    only_a = df_a[~df_a["key"].isin(keys_b)]
    only_b = df_b[~df_b["key"].isin(keys_a)]

    merged = pd.concat([df_a, df_b], ignore_index=True)
    merged_unique = merged.drop_duplicates(subset="key")

    # remove helper key
    only_a = only_a.drop(columns="key")
    only_b = only_b.drop(columns="key")
    merged_unique = merged_unique.drop(columns="key")

    # =================================================
    # Summary
    # =================================================
    st.markdown("## 📊 Summary")
    st.write(f"CSV A phones: {len(df_a)}")
    st.write(f"CSV B phones: {len(df_b)}")
    st.write(f"Only in A: {len(only_a)}")
    st.write(f"Only in B: {len(only_b)}")
    st.write(f"Merged unique: {len(merged_unique)}")

    # sanity check
    expected = len(keys_a | keys_b)
    st.caption(f"Union check (should match merged): {expected}")

    # =================================================
    # Display
    # =================================================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader(f"Only in A ({len(only_a)})")
        st.dataframe(only_a, use_container_width=True)

    with c2:
        st.subheader(f"Only in B ({len(only_b)})")
        st.dataframe(only_b, use_container_width=True)

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
    st.info("Upload both CSV files to start.")
