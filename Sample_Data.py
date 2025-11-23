import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample data
products = ['Milk', 'Bread', 'Eggs', 'Butter', 'Cheese']
start_date = datetime.now() - timedelta(days=60)
dates = [start_date + timedelta(days=x) for x in range(60)]

data = []
for date in dates:
    for product in products:
        # Random quantity with some trend
        base_demand = np.random.randint(10, 50)
        trend = 0.1 * (date - start_date).days if product == 'Milk' else 0 # Milk has increasing trend
        quantity = int(base_demand + trend + np.random.normal(0, 5))
        quantity = max(0, quantity)
        
        price = round(np.random.uniform(2.0, 10.0), 2)
        
        data.append({
            'Date': date,
            'Product': product,
            'Quantity': quantity,
            'Price': price,
            'Revenue': quantity * price
        })

df = pd.DataFrame(data)
df.to_excel('sample_sales_data.xlsx', index=False)
print("Created sample_sales_data.xlsx")