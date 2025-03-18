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
    data = {
        "input_data": {
            "columns": [
                "timestamp",
                "product_id",
                "country",
                "units_sold",
                "seasonality_factor",
                "is_promotion",
            ],
            "data": [
                [
                    datetime.now().isoformat(),
                    product_id,
                    country,
                    0,
                    seasonality,
                    int(is_promo),
                ]
            ],
        }
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    forecast = response.json().get("forecast", [0])[0]

    # Display metrics
    col1, col2 = st.columns(2)
    col1.metric("Forecasted Demand", forecast)

    current_inv = inventory[
        (inventory["product_id"] == product_id) & (inventory["country"] == country)
    ].iloc[-1]["current_inventory"]
    col2.metric("Current Inventory", current_inv)

    # Alert logic
    if current_inv < forecast:
        st.error(f"🚨 Order {forecast - current_inv} units now!")

with tab2:
    st.subheader("Supplier Management")
    supplier = suppliers[suppliers["product_id"] == product_id].iloc[0]

    st.write(f"**Supplier**: {supplier['supplier_id']}")
    st.write(f"**Lead Time**: {supplier['lead_time_days']} days")
    st.write(f"**Delay Risk**: {supplier['supplier_delay_rate'] * 100:.1f}%")

    if st.button("Place Order"):
        order_data = {
            "product_id": product_id,
            "quantity": max(0, forecast - current_inv),
            "supplier_id": supplier["supplier_id"],
        }
        response = requests.post(LOGIC_APP_URL, json=order_data)
        if response.status_code == 200:
            st.success("Order placed! Supplier notified.")

# Sidebar
st.sidebar.header("Notifications")
st.sidebar.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.write("📦 Inventory levels updated.")
