import streamlit as st
import numpy_financial as npf
import pandas as pd
from io import BytesIO

st.set_page_config(layout="wide")
st.title("Mortgage Strategy Dashboard")

# 1. Session State Initialization
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

# 2. Sidebar: Configuration & File Management
with st.sidebar:
    st.header("1. Data Management")
    
    uploaded_file = st.file_uploader("Upload saved snapshots (.csv)", type="csv")
    if uploaded_file is not None:
        uploaded_df = pd.read_csv(uploaded_file)
        st.session_state.snapshots = uploaded_df.to_dict('records')

    st.divider()
    st.header("2. Configure Scenario")
    name = st.text_input("Scenario Name", value=f"Option {len(st.session_state.snapshots) + 1}")
    p = st.number_input("Principal ($)", value=400000)
    r = st.slider("Interest Rate (%)", 3.0, 10.0, 6.5, 0.1)
    y = st.selectbox("Original Term (Years)", [15, 30])
    t = st.slider("Target Payoff (Years)", 5, 30, 15)
    
    if st.button("📸 Save to Grid"):
        m_rate = (r / 100) / 12
        std_pmt = npf.pmt(m_rate, y * 12, -p)
        target_pmt = npf.pmt(m_rate, t * 12, -p)
        
        # Math for Savings
        std_total_interest = (std_pmt * y * 12) - p
        actual_total_paid = target_pmt * (t * 12)
        true_total_interest = actual_total_paid - p
        
        new_data = {
            "Name": name,
            "Rate (%)": r,
            "Orig Term": y,
            "Target": t,
            "Base Pmt": round(std_pmt, 2),
            "Extra/Mo": round(target_pmt - std_pmt, 2),
            "Total Pmt": round(target_pmt, 2),
            "Total Int Cost": round(true_total_interest, 2),
            "Savings": round(std_total_interest - true_total_interest, 2)
        }
        st.session_state.snapshots.append(new_data)

# 3. Main Display (Everything inside this IF block)
if st.session_state.snapshots:
    df = pd.DataFrame(st.session_state.snapshots)
    
    st.subheader("Comparison Grid")

    # Corrected Column Configuration to match your dictionary keys
    column_configuration = {
        "Rate (%)": st.column_config.NumberColumn(format="%.1f%%"),
        "Base Pmt": st.column_config.NumberColumn(format="$%.2f"),
        "Extra/Mo": st.column_config.NumberColumn(format="$%.2f"),
        "Total Pmt": st.column_config.NumberColumn(format="$%.2f"),
        "Total Int Cost": st.column_config.NumberColumn(format="$%.2f"),
        "Savings": st.column_config.NumberColumn(format="$%.2f")
    }

    # Display the grid once with the config
    st.dataframe(
        df, 
        column_config=column_configuration, 
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download Comparison as CSV",
        data=csv,
        file_name='mortgage_scenarios.csv',
        mime='text/csv',
    )
    
    st.divider()
    st.subheader("Interest Cost Visualized")
    st.bar_chart(df.set_index("Name")["Total Int Cost"])
    
    if st.button("Clear Grid"):
        st.session_state.snapshots = []
        st.rerun()
else:
    st.info("Configure a scenario in the sidebar and click 'Save to Grid' to begin.")
