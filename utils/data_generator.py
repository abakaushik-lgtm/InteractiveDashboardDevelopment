import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data(start_date_str="2024-01-01", end_date_str="2025-12-31"):
    """
    Generates a realistic customer-transaction dataset to support cohort analysis,
    retention metrics, and general business intelligence reporting.
    """
    np.random.seed(42)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    total_days = (end_date - start_date).days
    
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    segments = ["Consumer", "Corporate", "Home Office"]
    channels = ["Online Store", "Retail Outlet", "Authorized Distributor"]
    
    catalog = {
        "Electronics": {
            "Smart Phone Pro": {"price": 999.0, "margin_min": 0.15, "margin_max": 0.22},
            "Ultrabook Laptop": {"price": 1299.0, "margin_min": 0.12, "margin_max": 0.18},
            "Wireless Headphones": {"price": 249.0, "margin_min": 0.25, "margin_max": 0.35},
            "Smart Watch Series 5": {"price": 349.0, "margin_min": 0.20, "margin_max": 0.28}
        },
        "Fashion": {
            "Premium Denim Jeans": {"price": 89.0, "margin_min": 0.50, "margin_max": 0.65},
            "Classic Leather Jacket": {"price": 299.0, "margin_min": 0.45, "margin_max": 0.55},
            "Organic Cotton T-Shirt": {"price": 29.0, "margin_min": 0.60, "margin_max": 0.75},
            "All-Weather Windbreaker": {"price": 120.0, "margin_min": 0.40, "margin_max": 0.50}
        },
        "Home & Living": {
            "Ergonomic Office Chair": {"price": 349.0, "margin_min": 0.30, "margin_max": 0.42},
            "Minimalist Floor Lamp": {"price": 79.0, "margin_min": 0.35, "margin_max": 0.50},
            "Luxury Wool Rug": {"price": 450.0, "margin_min": 0.40, "margin_max": 0.55},
            "Memory Foam Pillow": {"price": 59.0, "margin_min": 0.45, "margin_max": 0.60}
        },
        "Sports": {
            "Running Shoes": {"price": 130.0, "margin_min": 0.30, "margin_max": 0.40},
            "Eco-Friendly Yoga Mat": {"price": 49.0, "margin_min": 0.40, "margin_max": 0.55},
            "Adjustable Dumbbells": {"price": 299.0, "margin_min": 0.25, "margin_max": 0.35},
            "Waterproof Backpack": {"price": 89.0, "margin_min": 0.35, "margin_max": 0.45}
        }
    }
    
    # 1. Create a pool of 2,000 customers
    num_customers = 2000
    customers = []
    
    for i in range(num_customers):
        cust_id = f"CUST-{10000 + i}"
        region = np.random.choice(regions, p=[0.40, 0.30, 0.20, 0.10])
        segment = np.random.choice(segments, p=[0.55, 0.30, 0.15])
        channel = np.random.choice(channels, p=[0.50, 0.35, 0.15])
        
        # When did this customer first buy? (Slightly skewed towards earlier months)
        first_buy_day_offset = int(np.random.beta(1.5, 2.5) * total_days)
        first_buy_date = start_date + timedelta(days=first_buy_day_offset)
        
        # Number of lifetime transactions (between 1 and 12)
        # Using geometric-like distribution for realistic churn (many buy once, few buy a lot)
        num_txs = int(np.random.geometric(p=0.25))
        num_txs = min(num_txs, 12)
        
        customers.append({
            "cust_id": cust_id,
            "region": region,
            "segment": segment,
            "channel": channel,
            "first_buy_date": first_buy_date,
            "num_txs": num_txs
        })
        
    # 2. Generate transactions based on customer profiles
    transactions = []
    
    for cust in customers:
        current_date = cust["first_buy_date"]
        
        for tx_idx in range(cust["num_txs"]):
            # If the next transaction falls after the end date, skip it
            if current_date > end_date:
                break
                
            # Month/seasonality factors for prices/quantities
            month = current_date.month
            day_of_week = current_date.weekday()
            year = current_date.year
            
            seasonality_factor = 1.0
            if month in [11, 12]:  # Q4 Peak
                seasonality_factor = 1.40
            elif month in [1, 2]:   # Post-holiday dip
                seasonality_factor = 0.85
            elif month in [6, 7]:   # Mid-year sale
                seasonality_factor = 1.10
                
            if day_of_week in [5, 6]:  # Weekend boost
                seasonality_factor *= 1.15
                
            # Choose product category & specific product
            cat_probs = [0.25, 0.25, 0.25, 0.25]
            if cust["region"] == "North America":
                cat_probs = [0.35, 0.25, 0.20, 0.20]  # Tech heavy
            elif cust["region"] == "Europe":
                cat_probs = [0.20, 0.30, 0.20, 0.30]  # Fashion & Sports
                
            categories = list(catalog.keys())
            chosen_cat = np.random.choice(categories, p=cat_probs)
            chosen_prod_name = np.random.choice(list(catalog[chosen_cat].keys()))
            prod_info = catalog[chosen_cat][chosen_prod_name]
            
            # Quantity purchased
            qty = int(np.random.negative_binomial(2, 0.6) + 1)
            qty = max(1, int(round(qty * seasonality_factor)))
            
            # Unit price with slight variation
            unit_price = prod_info["price"] * np.random.uniform(0.98, 1.02)
            sales = round(unit_price * qty, 2)
            
            # Margin and Profit
            margin = np.random.uniform(prod_info["margin_min"], prod_info["margin_max"])
            # Corporate segment gets small discount, slightly lower margin
            if cust["segment"] == "Corporate":
                margin *= 0.95
                sales *= 0.95
                
            profit = round(sales * margin, 2)
            cost = round(sales - profit, 2)
            
            # Targets (realistic projections)
            target = round(sales * np.random.uniform(0.92, 1.15), 2)
            
            transactions.append({
                "Date": current_date.strftime("%Y-%m-%d"),
                "CustomerID": cust["cust_id"],
                "Region": cust["region"],
                "Product": chosen_prod_name,
                "Category": chosen_cat,
                "Sales": sales,
                "Profit": profit,
                "Cost": cost,
                "Customers": 1,  # Number of unique entities in transaction
                "Segment": cust["segment"],
                "Sales Channel": cust["channel"],
                "Target": target
            })
            
            # Time between purchases (30 to 180 days)
            days_to_next = np.random.randint(30, 180)
            current_date += timedelta(days=days_to_next)
            
    df = pd.DataFrame(transactions)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df
