# synthetic Data Generation
# synthetic_data.py
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)

products = [f"P{1000 + i}" for i in range(1000)]
countries = [fake.country_code() for _ in range(5)]

# Generate historical sales data with seasonality and promotions
sales_data = []
for product_id in products:
    base_sales = np.random.randint(100, 500)
    for week in range(52):
        date = datetime(2023, 1, 1) + timedelta(weeks=week)
        # Seasonality logic
        if date.month == 12:
            seasonality = 1.5
        elif date.month == 7:
            seasonality = 1.3
        else:
            seasonality = 1.0
        # Promotion logic (10% chance)
        is_promotion = 1 if np.random.rand() < 0.1 else 0
        units_sold = int(
            base_sales * seasonality + 50 * is_promotion + np.random.normal(0, 50)
        )
        sales_data.append(
            {
                "timestamp": date.strftime("%Y-%m-%d"),
                "product_id": product_id,
                "country": np.random.choice(countries),
                "units_sold": max(0, units_sold),
                "seasonality_factor": seasonality,
                "is_promotion": is_promotion,
            }
        )

sales_df = pd.DataFrame(sales_data)
sales_df.to_csv("./data/historical_sales.csv", index=False)

# Generate Inventory Data
inventory_data = []
for product_id in products:
    current_inventory = np.random.randint(500, 2000)  # Starting inventory
    avg_weekly_sales = np.mean(
        [s["units_sold"] for s in sales_data if s["product_id"] == product_id]
    )
    lead_time_days = np.random.choice([7, 14, 21])  # Vary lead times
    reorder_point = int(avg_weekly_sales * (lead_time_days / 7) * 1.2)  # Safety stock
    restock_quantity = int(avg_weekly_sales * 2)  # Order 2x weekly sales

    for week in range(52):
        date = datetime(2023, 1, 1) + timedelta(weeks=week)
        # Simulate inventory depletion
        weekly_sales = [
            s["units_sold"]
            for s in sales_data
            if s["product_id"] == product_id
            and s["timestamp"] == date.strftime("%Y-%m-%d")
        ]
        if weekly_sales:
            current_inventory -= weekly_sales[0]
        # Restock if below reorder point
        if current_inventory < reorder_point:
            current_inventory += restock_quantity
        inventory_data.append(
            {
                "inventory_id": fake.uuid4(),
                "timestamp": date.strftime("%Y-%m-%d"),
                "product_id": product_id,
                "current_inventory": max(0, current_inventory),  # No negative inventory
                "reorder_point": reorder_point,
                "lead_time_days": lead_time_days,
                "restock_quantity": restock_quantity,
            }
        )

inventory_df = pd.DataFrame(inventory_data)
inventory_df.to_csv("./data/inventory.csv", index=False)

# Generate Supplier Data
suppliers = [f"SUP_{i:02d}" for i in range(1, 11)]  # 10 suppliers

supplier_data = []
for product_id in products:
    supplier_id = np.random.choice(suppliers)
    lead_time_days = np.random.choice([7, 14, 21])
    delay_rate = np.random.choice([0.1, 0.2, 0.3])  # 10-30% delay chance
    unit_cost = round(np.random.uniform(10, 100), 2)  # Cost per unit
    supplier_data.append(
        {
            "supplier_id": supplier_id,
            "product_id": product_id,
            "lead_time_days": lead_time_days,
            "supplier_delay_rate": delay_rate,
            "unit_cost": unit_cost,
        }
    )

supplier_df = pd.DataFrame(supplier_data)
supplier_df.to_csv("./data/suppliers.csv", index=False)
