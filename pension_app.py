import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import math
import calendar

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

st.set_page_config(page_title="Pension Benefits Pro", layout="wide", initial_sidebar_state="collapsed")

# Custom Function for Indian Currency Formatting (Lakhs/Crores)
def format_indian_currency(number, include_decimal=True):
    s = str(math.floor(number))
    out = ""
    if len(s) > 3:
        last_three = s[-3:]
        remaining = s[:-3]
        out = "," + last_three
        while len(remaining) > 2:
            out = "," + remaining[-2:] + out
            remaining = remaining[:-2]
        out = remaining + out
    else:
        out = s
    
    if include_decimal:
        paise = f"{number:.2f}".split('.')[1]
        return f"₹{out}.{paise}"
    return f"₹{out}"

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stSidebar"] { display: none; }
    .header-subtext { color: #555; font-size: 1.1rem; font-style: italic; margin-top: -15px; margin-bottom: 25px; }
    .highlight-box { padding: 15px; border-radius: 8px; border-left: 5px solid #2e7d32; background-color: #e8f5e9; margin-bottom: 10px; font-weight: bold; font-size: 1.1rem; }
    .family-box { padding: 15px; border-radius: 8px; border-left: 5px solid #1565c0; background-color: #e3f2fd; margin-bottom: 10px; font-weight: bold; font-size: 1.1rem; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f0f2f6; color: #555; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #ddd; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

st.title("🏦 Pensionary Benefits Calculator")
st.markdown('<p class="header-subtext">Created by: Mithun Biswas, Executive Assistant, Pension Cell, CGST & C.Ex. Mumbai Central</p>', unsafe_allow_html=True)

MIN_DATE = date(1950, 1, 1)

# --- Input Section ---
st.subheader("📋 Enter Employee Details")
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name = st.text_input("Full Name", value="")
        designation = st.text_input("Designation", value="")
        ret_type = st.selectbox("Type of Retirement", ["Superannuation", "Voluntary Retirement", "Compulsory Retirement"])
        # Format set to DD/MM/YYYY
        dob = st.date_input("Date of Birth", value=date(1965, 10, 3), min_value=MIN_DATE, format="DD/MM/YYYY")

    with col2:
        basic_pay = st.number_input("Basic Pay (Rs.)", value=0, step=500)
        da_percent = st.number_input("Current DA/DR (%)", value=0.0)
        doj = st.date_input("Date of Entry", value=date(1995, 1, 1), min_value=MIN_DATE, format="DD/MM/YYYY")

    with col3:
        # Superannuation Logic
        birth_month, birth_year = dob.month, dob.year
        ret_year = birth_year + 60
        if dob.day == 1:
            if birth_month == 1: target_month, ret_year = 12, ret_year - 1
            else: target_month = birth_month - 1
        else:
            target_month = birth_month
        last_day = calendar.monthrange(ret_year, target_month)[1]
        default_dor = date(ret_year, target_month, last_day)
        min_dor = doj + timedelta(days=int(5*365.25))
        
        if ret_type == "Superannuation":
            dor = st.date_input("Date of Retirement", value=max(default_dor, min_dor), min_value=min_dor, format="DD/MM/YYYY")
        else:
            dor = st.date_input("Date of Retirement", value=date.today() if date.today() > min_dor else min_dor, min_value=min_dor, format="DD/MM/YYYY")
            
        comm_percent = st.slider("Commutation Opted (%)", 0, 40, 0)
        govt_acc = st.selectbox("Govt. Accommodation?", ["No", "Yes"])

    st.write("")
    calculate = st.button("Generate Calculation Report", type="primary", use_container_width=True)

if calculate:
    if basic_pay <= 0:
        st.error("Please enter a valid Basic Pay amount.")
    else:
        # Calculations
        delta = dor - doj
        years_service = delta.days // 365
        remaining_days = delta.days % 365
        months_service = remaining_days // 30
        days_service = remaining_days % 30
        
        periods = (years_service * 2)
        if months_service >= 9: periods += 3
        elif months_service >= 3: periods += 1
        six_monthly_periods = min(66, periods)
        
        emoluments = float(basic_pay) * (1 + float(da_percent) / 100)
        monthly_pension_before = float(basic_pay) / 2
        comm_amt = (monthly_pension_before * float(comm_percent)) / 100
        residuary = monthly_pension_before - comm_amt
        
        calc_age_next = (dor.year - dob.year) + 1
        final_age_next = 61 if (ret_type == "Superannuation" and calc_age_next < 61) else calc_age_next
        factor = commutation_df[commutation_df['Age'] == final_age_next]['Factor'].values[0]
        lump_sum = math.ceil(comm_amt * 12 * factor)
        
        total_grat = min(2500000.0, (emoluments / 4) * six_monthly_periods)
        withheld = math.ceil(total_grat * 0.10) if govt_acc == "Yes" else 0
        payable_grat = total_grat - withheld

        # --- Display Results ---
        st.divider()
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.subheader("📊 Summary Statistics")
            st.write(f"**Basic Pay:** {format_indian_currency(basic_pay, False)}")
            st.write(f"**Retirement Type:** {ret_type}")
            # No commas between Y, M, and D
            st.write(f"**Qualifying Service:** {years_service} Years {months_service} Months {days_service} Days")
        with res_col2:
            st.subheader("📅 Retirement Info")
            st.write(f"**Retiree Name:** {name if name else 'N/A'}")
            st.write(f"**Commutation Age Applied:** {final_age_next} Years")

        st.divider()
        st.subheader("🟢 Part-A) Pensionary Benefits")
        st.markdown(f"""
            <div class="highlight-box">1. Monthly Pension before Commutation: {format_indian_currency(monthly_pension_before)} + DR</div>
            <div class="highlight-box">2. Commuted Pension: {format_indian_currency(comm_amt)}</div>
            <div class="highlight-box">3. Residuary Pension after Commutation: {format_indian_currency(residuary)} + DR</div>
            <div class="highlight-box">4. Commuted Value [Lump sum]: {format_indian_currency(lump_sum, False)}</div>
            <div class="highlight-box">5. Pension Gratuity Admissible: {format_indian_currency(total_grat)}</div>
            <div class="highlight-box">6. Amount to be Withheld (Rounded Up): {format_indian_currency(withheld, False)}</div>
            <div class="highlight-box" style="background-color: #c8e6c9; border-left-color: #1b5e20;">7. Net Payable Gratuity: {format_indian_currency(payable_grat)}</div>
        """, unsafe_allow_html=True)

        st.subheader("🔵 Part-B) Family Pension")
        st.markdown(f"""
            <div class="family-box">1. Enhanced Family Pension: {format_indian_currency(monthly_pension_before)} + DR</div>
            <div class="family-box">2. Ordinary Family Pension: {format_indian_currency(max(9000.0, float(basic_pay) * 0.30))} + DR</div>
        """, unsafe_allow_html=True)

st.markdown("""<div class="footer">Developed by: <b>Mithun Biswas</b>, EA, Pension Cell, CGST & C.Ex. Mumbai Central</div>""", unsafe_allow_html=True)