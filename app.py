import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinTech Reconciliation", layout="wide")

st.title("💳 FinTech Reconciliation Dashboard")

# -------------------------------
# FILE UPLOAD OPTION
# -------------------------------
st.sidebar.header("Upload Data")

uploaded_tx = st.sidebar.file_uploader("Upload Transactions CSV", type=["csv"])
uploaded_st = st.sidebar.file_uploader("Upload Settlements CSV", type=["csv"])

# File upload section
if uploaded_tx is not None and uploaded_st is not None:
    try:
        transactions = pd.read_csv(uploaded_tx)
        settlements = pd.read_csv(uploaded_st)
        st.success("Files uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading uploaded files: {e}")
        st.stop()

else:
    st.warning("Using default data from repository...")

    try:
        transactions = pd.read_csv("transactions.csv")
        settlements = pd.read_csv("settlements.csv")
    except Exception as e:
        st.error("Default CSV files not found. Please upload files manually.")
        st.stop()

# -------------------------------
# DATA PREVIEW
# -------------------------------
st.subheader("📄 Data Preview")

col1, col2 = st.columns(2)

with col1:
    st.write("Transactions")
    st.dataframe(transactions.head())

with col2:
    st.write("Settlements")
    st.dataframe(settlements.head())

# -------------------------------
# CLEANING
# -------------------------------
transactions['date'] = pd.to_datetime(transactions['date'])
settlements['settlement_date'] = pd.to_datetime(settlements['settlement_date'])

# -------------------------------
# RECONCILIATION LOGIC
# -------------------------------
duplicates = transactions[transactions.duplicated('id', keep=False)]

missing = transactions[~transactions['id'].isin(settlements['id'])]

unknown = settlements[~settlements['id'].isin(transactions['id'])]

merged = pd.merge(transactions, settlements, on='id', how='inner')

late = merged[merged['settlement_date'].dt.month > merged['date'].dt.month]

mismatch = merged[merged['amount_x'] != merged['amount_y']]

# -------------------------------
# METRICS
# -------------------------------
st.subheader("📊 Summary Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Duplicates", len(duplicates))
col2.metric("Missing", len(missing))
col3.metric("Refund Errors", len(unknown))
col4.metric("Late", len(late))
col5.metric("Mismatch", len(mismatch))

# -------------------------------
# CHART
# -------------------------------
st.subheader("📈 Issue Distribution")

labels = ['Duplicates', 'Missing', 'Refunds', 'Late', 'Mismatch']
values = [len(duplicates), len(missing), len(unknown), len(late), len(mismatch)]

fig = plt.figure()
plt.bar(labels, values)
plt.title("Reconciliation Issues")
st.pyplot(fig)

# -------------------------------
# DETAILS SECTION
# -------------------------------
st.subheader("🔍 Detailed Issues")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Duplicates", "Missing", "Refund Errors", "Late", "Mismatch"
])

with tab1:
    st.dataframe(duplicates)

with tab2:
    st.dataframe(missing)

with tab3:
    st.dataframe(unknown)

with tab4:
    st.dataframe(late)

with tab5:
    st.dataframe(mismatch)

# -------------------------------
# SUMMARY REPORT DOWNLOAD
# -------------------------------
summary = pd.DataFrame({
    "Issue": labels,
    "Count": values
})

csv = summary.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Summary Report",
    data=csv,
    file_name='reconciliation_report.csv',
    mime='text/csv'
)

# -------------------------------
# INSIGHTS
# -------------------------------
st.subheader("🧠 Insights")

if len(missing) > 0:
    st.warning("Some transactions are not settled. Possible delay or failure.")

if len(unknown) > 0:
    st.error("Refunds detected without original transactions.")

if len(late) > 0:
    st.info("Some settlements are delayed to next month.")

if len(mismatch) > 0:
    st.warning("Amount mismatch detected (possible rounding issues).")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Built for FinTech Reconciliation Challenge 🚀")
