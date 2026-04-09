import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# custom styling

st.markdown("""
<style>
<div style='
    text-align:center;
    font-size:20px;
    font-weight:bold;
    color:#4CAF50;
    animation: fadeIn 1s ease-in;
'>
✨ Welcome to your Dashboard ✨
</div>

<style>
@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}
/*till here is headings */
            
/* background */
body {
    background-color: #0e1117;
}

/* main container */
.block-container {
    padding-top: 2rem;
}

/* titles */
h1, h2, h3 {
    color: #ffffff;
}

/* metrics */
[data-testid="stMetricValue"] {
    color: #00ffcc;
    font-size: 28px;
}

/* sidebar*/ 
section[data-testid="stSidebar"] {
    background-color:#e6fffa;
    padding: 15px;
    border-radius: 10px;
}


/* buttons 
button {
    background-color: #2563eb !important;
    color: white !important;
    border-radius: 8px;
}
*/
            
/* dataframe */
[data-testid="stDataFrame"] {
    background-color: #1f2937;
}
</style>
""", unsafe_allow_html=True)


# title
st.title("💡Smart Budget Planning & Expense Prediction System💸")


# confetti effect (runs once)
#if "confetti" not in st.session_state:
 #   st.balloons()
  #  st.session_state.confetti = True

st.toast("✨ Welcome!", icon="🎉")


# =========================
# WELCOME POPUP (option 2)
# =========================
if "shown" not in st.session_state:
    st.info("✨ Welcome to your Smart Budget Dashboard!")
    st.session_state.shown = True

# =========================
# GENERAL ALERT (option 3)
# =========================
st.warning("📌 Tip: Set budgets to avoid overspending!")


# =========================
# LOAD FULL DATA (income + expense)
# =========================
try:
    df_full = pd.read_excel("expenses_income_summary.csv.xlsx")
    df_full.columns = df_full.columns.str.strip().str.lower()
    df_full['date'] = pd.to_datetime(df_full['date'])
except:
    df_full = pd.DataFrame()

# =========================
# INCOME SUMMARY
# =========================
st.header("💰Income Summary")

if not df_full.empty:
    income = df_full[df_full['type'].str.lower() == 'income']['amount'].sum()
    expense_full = df_full[df_full['type'].str.lower() == 'expense']['amount'].sum()

    st.metric("Income", income)
    st.metric("Expense", expense_full)
    st.metric("Savings", income - expense_full)

    # monthly income graph
    st.subheader("📈Monthly Income Trend")
    monthly_income = df_full[df_full['type'].str.lower() == 'income'] \
        .groupby(df_full['date'].dt.to_period('M'))['amount'].sum()

    fig, ax = plt.subplots()
    monthly_income.plot(ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("Income")
    ax.set_title("Monthly Income Trend")

    st.pyplot(fig)


else:
    st.warning("Full dataset not found for income analysis")

# =========================
# FILE UPLOAD (EXPENSES)
# =========================
uploaded_file = st.file_uploader("Upload your expense file", type=["csv"])

# load expense data
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("cleaned_expenses.csv")
# =========================
# SMART INSIGHTS
# =========================

# highest expense
if not df.empty:
    top_expense = df.loc[df['amount'].idxmax()]
    st.error(f"🎯 Highest Expense: {top_expense['category']} - {round(top_expense['amount'],2)}")

# most spending category
if not df.empty:
    top_category = df.groupby('category')['amount'].sum().idxmax()
    st.info(f"🪞 Insight: Most of your spending is in {top_category}")

# load predictions and anomalies
try:
    pred_df = pd.read_csv("category_predictions.csv")
except:
    pred_df = pd.DataFrame()

try:
    anomaly_df = pd.read_csv("anomaly_results.csv")
except:
    anomaly_df = pd.DataFrame()

# convert date
df['date'] = pd.to_datetime(df['date'])

# =========================
# FILTERS
# =========================
st.sidebar.markdown("✨*Customize your data view here*✨")

st.sidebar.header("🔍Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    df['category'].unique(),
    default=df['category'].unique()
)

start_date = st.sidebar.date_input("Start Date", df['date'].min())
end_date = st.sidebar.date_input("End Date", df['date'].max())

df = df[
    (df['category'].isin(selected_category)) &
    (df['date'] >= pd.to_datetime(start_date)) &
    (df['date'] <= pd.to_datetime(end_date))
]

# =========================
# MONTHLY TREND
# =========================
st.header("📈Monthly Spending Trend")

monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
monthly = monthly.reset_index()
monthly['date'] = monthly['date'].astype(str)


fig, ax = plt.subplots()
ax.plot(monthly['date'], monthly['amount'])
ax.set_xlabel("Month")
ax.set_ylabel("Total Spending")
ax.set_title("Monthly Spending Trend")

# rotate labels
plt.xticks(rotation=45)

# show fewer labels (optional but recommended)
ax.set_xticks(ax.get_xticks()[::2])

plt.tight_layout()

st.pyplot(fig)


# =========================
# CATEGORY BREAKDOWN
# =========================
st.header("📊Category-wise Spending")

category = df.groupby('category')['amount'].sum()
fig, ax = plt.subplots()
category.plot(kind='bar', ax=ax)
ax.set_xlabel("Category")
ax.set_ylabel("Total Spending")
ax.set_title("Category-wise Spending")

st.pyplot(fig)


# =========================
# BUDGET SETTING
# =========================
st.header("⚙️Budget Management")

budgets = {}
for cat in df['category'].unique():
    budgets[cat] = st.number_input(f"Set budget for {cat}", min_value=0.0, value=1000.0)

# =========================
# BUDGET ALERTS
# =========================
st.subheader("🚨Budget Alerts")

for cat in budgets:
    spent = df[df['category'] == cat]['amount'].sum()
    if spent > budgets[cat]:
        st.warning(f"⚠️ Budget exceeded for {cat}: {spent} > {budgets[cat]}")

# =========================
# PREDICTIONS
# =========================
st.header("🔮Predicted Next Month Spending")

st.dataframe(pred_df)

# prediction alerts
st.subheader("Prediction Alerts")

for i, row in pred_df.iterrows():
    cat = row['category']
    pred = row['predicted_amount']
    if cat in budgets and pred > budgets[cat]:
        st.error(f"⚠️ Future overspending risk in {cat}: {round(pred,2)}")

# =========================
# ANOMALY DETECTION
# =========================
st.header("🧩Anomaly Detection")

if not anomaly_df.empty:
    normal = anomaly_df[anomaly_df['anomaly'] == 0]
    st.subheader("➡️Normal Range (Typical Spending)")
    st.dataframe(normal[['date', 'amount', 'category', 'title']].head(10))

    anomalies = anomaly_df[anomaly_df['anomaly'] == 1]
    st.subheader("➡️Detected Anomalies")
    st.dataframe(anomalies[['date', 'amount', 'category', 'title']])
else:
    st.warning("No anomaly data found")
def highlight_anomaly(row):
    if row['anomaly'] == 1:
        return ['background-color: #ff4d4d'] * len(row)  # red
    else:
        return ['background-color: #2ecc71'] * len(row)  # green

st.dataframe(
    anomaly_df.style.apply(highlight_anomaly, axis=1)
)

# =========================
# RAW DATA
# =========================
st.header("📂Full Expense Data")

st.dataframe(df)

st.markdown("---")
st.markdown("<p style='text-align: center;'> ✨You’ve reached the end — time to save more, spend smarter!✨</p>", unsafe_allow_html=True)
