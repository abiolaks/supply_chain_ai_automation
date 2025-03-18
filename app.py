import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Azure ML API Settings
API_ENDPOINT = os.getenv("AZURE_ML_ENDPOINT")
API_KEY = os.getenv("AZURE_API_KEY")
LOGIC_APP_URL = os.getenv("LOGIC_APP_URL")

# Load data
@st.cache_data
def load_data():
    inventory = pd.read_csv("data/inventory.csv")
    suppliers = pd.read_csv("data/suppliers.csv")
    return inventory, suppliers

inventory, suppliers = load_data()

# --------------------------
# Streamlit UI
# --------------------------
st.title("Dango Group Supply Chain Dashboard")
st.markdown("Real-time inventory tracking, AI forecasts, and automated ordering.")

# Tabs
tab1, tab2 = st.tabs(["Inventory & Forecast", "Supplier Actions"])

with tab1:
    st.subheader("Demand Forecasting")
    
    # Product and country selection
    product_id = st.selectbox("Product ID", inventory["product_id"].unique())
    country = st.selectbox("Country", inventory["country"].unique())
    
    # User inputs for seasonality/promotions
    seasonality = st.slider("Seasonality Factor", 0.5, 2.0, 1.2)
    is_promo = st.checkbox("Promotion Planned?")
    
    # Fetch forecast from Azure ML
    data =