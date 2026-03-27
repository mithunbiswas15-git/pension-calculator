import streamlit as st

# Set page title
st.set_page_config(page_title="Site Moved", layout="centered")

# Hide the sidebar and menu for a clean look
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Display the message
st.title("🚀 We Have Moved!")

st.info("The Pensionary Benefits & Leave Encashment Calculator has a new, faster home.")

st.markdown("### Please visit us at our new address:")
st.link_button("👉 ccspension.vercel.app", "https://ccspension.vercel.app", type="primary")

st.divider()

st.warning("Please update your bookmarks. This Streamlit version will be discontinued soon.")

st.write("Created by: Mithun Biswas, Executive Assistant, Pension Cell, CGST & C.Ex. Mumbai Central")
