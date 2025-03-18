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
sales_df.to_csv("data/historical_sales.csv", index=False)
