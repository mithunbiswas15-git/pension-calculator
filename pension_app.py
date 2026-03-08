import streamlit as st
from datetime import datetime, date
import pandas as pd
import math

# Commutation Table Data
commutation_data = {
    "Age": [i for i in range(20, 82)],
    "Factor": [
        9.188, 9.187, 9.186, 9.185, 9.184, 9.183, 9.182, 9.180, 9.178, 9.176,
        9.173, 9.169, 9.164, 9.159, 9.152, 9.145, 9.136, 9.126, 9.116, 9.103,
        9.090, 9.075, 9.059, 9.040, 9.019, 8.996, 8.971, 8.943, 8.913, 8.881,
        8.846, 8.808, 8.768, 8.724, 8.678, 8.627, 8.572, 8.512, 8.446, 8.371,
        8.287, 8.194, 8.093, 7.982, 7.862, 7.731, 7.591, 7.431, 7.262, 7.083,
        6.897, 6.701, 6.499, 6.289, 6.075, 5.857, 5.638, 5.421, 5.205, 4.993, 4.784, 4.581
    ]
}
commutation_df = pd.DataFrame(commutation_data)

st.set_page_config(page_title="Pension Benefits Pro", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .header-subtext {
        color: #555;
        font-size: 1.1rem;
        font-style: italic;
        margin-top: -15px;
        margin-bottom: 25px;
    }
    .highlight-box {
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2e7d32;
        background-color: #e8f5e9;
        margin-bottom: 10px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .family-box {
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #1565c0;
        background-color: #e3f2fd;
        margin-bottom: 10px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #555;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #ddd;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Pensionary Benefits Calculator")
st.markdown('<p class="header-subtext">Created by: Mithun Biswas, Executive Assistant, Pension Cell, CGST & C.Ex. Mumbai Central</p>', unsafe_allow_html=True)

MIN_DATE = date(1950, 1, 1)

# Sidebar for Input
with st.sidebar:
    st.header("📋 Employee Details")
    name = st.text_input("Full Name", value="")
    designation = st.text_input("Designation", value="")
    st.divider()
    st.header("💰 Financials")
    basic_pay = st.number_input("Basic Pay (Rs.)", value=0, step=500)
    da_percent = st.number_input("Current DA/DR (%)", value=0.0)
    comm_percent = st.slider("Commutation Opted (%)", 0, 40, 0)
    st.divider()
    st.header("📅 Service Dates")
    dob = st.date_input("Date of Birth", value=date(1965, 1, 1), min_value=MIN_DATE)
    doj = st.date_input("Date of Entry", value=date(1995, 1, 1), min_value=MIN_DATE)
    dor = st.date_input("Date of Retirement", value=date.today(), min_value=MIN_DATE)
    govt_acc = st.selectbox("Govt. Accommodation?", ["No", "Yes"])
    
    calculate = st.button("Generate Report", type="primary", use_container_width=True)

if calculate:
    if basic_pay <= 0:
        st.error("Please enter a valid Basic Pay amount.")
    elif dor < doj:
        st.error("Retirement date cannot be before Entry date.")
    else:
        # Service Calculation
        delta = dor - doj
        total_days = delta.days
        years_service = total_days // 365
        remaining_days = total_days % 365
        months_service = remaining_days // 30
        days_service = remaining_days % 30
        
        # Periods Calculation
        periods = (years_service * 2)
        if months_service >= 9: periods += 3
        elif months_service >= 3: periods += 1
        six_monthly_periods = min(66, periods)
        
        # Financials
        emoluments = float(basic_pay) + (float(basic_pay) * float(da_percent) / 100)
        monthly_pension_before = float(basic_pay) / 2
        comm_amt = (monthly_pension_before * float(comm_percent)) / 100
        residuary = monthly_pension_before - comm_amt
        
        # Commutation
        age_next = (dor.year - dob.year) + 1
        factor_list = commutation_df[commutation_df['Age'] == age_next]['Factor'].values
        factor = factor_list[0] if len(factor_list) > 0 else 0
        lump_sum = math.ceil(comm_amt * 12 * factor)
        
        # Gratuity with Rounding logic
        total_gratuity_admissible = min(2500000.0, (emoluments / 4) * six_monthly_periods)
        
        # Rounding Up Withheld Amount to nearest full integer
        raw_withheld = (total_gratuity_admissible * 0.10) if govt_acc == "Yes" else 0.0
        withheld_gratuity = math.ceil(raw_withheld)
        
        payable_gratuity = total_gratuity_admissible - withheld_gratuity
        
        # Family Pension
        enhanced_fp = monthly_pension_before
        ordinary_fp = max(9000.0, float(basic_pay) * 0.30)

        # --- Display Results ---
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📊 Summary Statistics")
            st.metric("Basic Pay", f"₹{basic_pay:,}")
            st.write(f"**Qualifying Service:** {years_service} Years, {months_service} Months, {days_service} Days")
            st.write(f"**Six-Monthly Periods:** {six_monthly_periods}")

        with col_b:
            st.subheader("📅 Retirement Info")
            st.write(f"**Retiree Name:** {name if name else 'N/A'}")
            st.write(f"**Designation:** {designation if designation else 'N/A'}")
            st.write(f"**Age Next Birthday:** {age_next} Years")

        st.divider()

        st.subheader("🟢 Part-A) Pensionary Benefits")
        st.markdown(f"""
            <div class="highlight-box">1. Monthly Pension before Commutation: ₹{monthly_pension_before:,.2f} + DR</div>
            <div class="highlight-box">2. Commuted Pension: ₹{comm_amt:,.2f}</div>
            <div class="highlight-box">3. Residuary Pension after Commutation: ₹{residuary:,.2f} + DR</div>
            <div class="highlight-box">4. Commuted Value [Lump sum]: ₹{lump_sum:,}</div>
            <div class="highlight-box">5. Pension Gratuity Admissible: ₹{total_gratuity_admissible:,.2f}</div>
            <div class="highlight-box">6. Amount of Gratuity to be Withheld (Rounded Up): ₹{withheld_gratuity:,}</div>
            <div class="highlight-box" style="background-color: #c8e6c9; border-left-color: #1b5e20;">7. Net Payable Gratuity: ₹{payable_gratuity:,.2f}</div>
        """, unsafe_allow_html=True)

        st.subheader("🔵 Part-B) Family Pension")
        st.markdown(f"""
            <div class="family-box">1. Enhanced Family Pension: ₹{enhanced_fp:,.2f} + DR</div>
            <div class="family-box">2. Ordinary Family Pension: ₹{ordinary_fp:,.2f} + DR</div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        Developed by: <b>Mithun Biswas</b>, Executive Assistant, Pension Cell, CGST & C.Ex. Mumbai Central
    </div>
""", unsafe_allow_html=True)