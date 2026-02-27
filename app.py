import streamlit as st
import numpy_financial as npf
import pandas as pd
import plotly.figure_factory as ff

# Set page layout
st.set_page_config(layout="wide")
st.title("Hodges Mortgage Strategy Dashboard")

# 1. Session State Initialization
if 'snapshots' not in st.session_state:
    st.session_state.snapshots = []

# 2. Sidebar Configuration
with st.sidebar:
    st.header("1. Data Management")
    
    # Upload previous work
    uploaded_file = st.file_uploader("Upload saved snapshots (.csv)", type="csv")
    if uploaded_file is not None:
        uploaded_df = pd.read_csv(uploaded_file)
        st.session_state.snapshots = uploaded_df.to_dict('records')

    # Delete Feature
    if st.session_state.snapshots:
        st.divider()
        st.subheader("🗑️ Remove Scenarios")
        options_to_delete = st.multiselect(
            "Select scenarios to delete:",
            options=[s["Name"] for s in st.session_state.snapshots]
        )
        if st.button("Delete Selected"):
            st.session_state.snapshots = [s for s in st.session_state.snapshots if s["Name"] not in options_to_delete]
            st.rerun()

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
        
        # Calculate interest costs based on the ACTUAL payoff time
        std_total_interest = (std_pmt * y * 12) - p
        actual_total_paid = target_pmt * (t * 12)
        true_total_interest = actual_total_paid - p
        savings = std_total_interest - true_total_interest
        
        new_data = {
            "Name": name,
            "Rate (%)": r,
            "Orig Term": y,
            "Target": t,
            "Base Pmt": round(std_pmt, 2),
            "Extra/Mo": round(target_pmt - std_pmt, 2),
            "Total Pmt": round(target_pmt, 2),
            "Total Int Cost": round(true_total_interest, 2),
            "Savings": round(savings, 2)
        }
        st.session_state.snapshots.append(new_data)

# 3. Main Display Area
if st.session_state.snapshots:
    df = pd.DataFrame(st.session_state.snapshots)
    
    st.subheader("Comparison Grid")

    # Formatting columns for the interactive grid
    column_configuration = {
        "Rate (%)": st.column_config.NumberColumn(format="%.1f%%"),
        "Base Pmt": st.column_config.NumberColumn(format="$%,.2f"),
        "Extra/Mo": st.column_config.NumberColumn(format="$%,.2f"),
        "Total Pmt": st.column_config.NumberColumn(format="$%,.2f"),
        "Total Int Cost": st.column_config.NumberColumn(format="$%,.2f"),
        "Savings": st.column_config.NumberColumn(format="$%,.2f")
    }

    st.dataframe(
        df, 
        column_config=column_configuration, 
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.subheader("Exportable Image View")
    st.info("Hover over the table and click the 📷 icon to download as an image.")
    
    # Format a copy for the Plotly table export
    img_df = df.copy()
    money_cols = ["Base Pmt", "Extra/Mo", "Total Pmt", "Total Int Cost", "Savings"]
    for col in money_cols:
        img_df[col] = img_df[col].apply(lambda x: f"${x:,.2f}")
    
    fig = ff.create_table(img_df)
    st.plotly_chart(fig, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download CSV",
        data=csv,
        file_name='mortgage_scenarios.csv',
        mime='text/csv',
    )
    
    if st.button("Clear All Data"):
        st.session_state.snapshots = []
        st.rerun()
else:
    st.info("Set your mortgage details in the sidebar and click 'Save to Grid' to start comparing.")
