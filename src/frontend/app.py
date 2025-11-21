import streamlit as st
import yaml
import os

# Load settings
with open('src/config/settings.yaml', 'r') as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title=config['app']['name'], layout="wide")

st.title(config['app']['name'])

st.sidebar.header("Navigation")
option = st.sidebar.selectbox("Choose Agent", ["Vendor Onboarding", "Requisition", "Compliance", "Approval"])

st.write(f"You selected: {option}")

# Placeholder for chat interface
st.subheader("Chat with Co-Pilot")
user_input = st.text_input("You:", "")
if user_input:
    st.write(f"Co-Pilot: Processing '{user_input}' with {option} agent...")
