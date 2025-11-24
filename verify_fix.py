import pandas as pd
import numpy as np

def test_logic(df):
    # Normalize columns for case-insensitive matching
    col_map = {str(col).lower().strip(): col for col in df.columns}
    required_keys = ['date', 'product', 'quantity']
    
    if all(key in col_map for key in required_keys):
        print("[OK] Required columns found!")
        
        # Get actual column names from the map
        date_col = col_map['date']
        prod_col = col_map['product']
        qty_col = col_map['quantity']
        price_col = col_map.get('price')
        rev_col = col_map.get('revenue')
        
        print(f"Mapped columns: Date='{date_col}', Product='{prod_col}', Quantity='{qty_col}', Price='{price_col}', Revenue='{rev_col}'")

        for index, row in df.iterrows():
            try:
                # Calculate Revenue
                quantity = row[qty_col]
                if price_col and pd.notna(row[price_col]):
                    revenue = quantity * row[price_col]
                    source = "Price"
                elif rev_col and pd.notna(row[rev_col]):
                    revenue = row[rev_col]
                    source = "Revenue"
                else:
                    revenue = 0.0
                    source = "None"
                
                print(f"Row {index}: Quantity={quantity}, Revenue={revenue} (Source: {source})")
            except Exception as e:
                print(f"Error in row {index}: {e}")
    else:
        print("[FAIL] Required columns NOT found!")
        missing = [key for key in required_keys if key not in col_map]
        print(f"Missing: {missing}")

print("--- Test Case 1: Lowercase 'price' ---")
df1 = pd.DataFrame({
    'date': ['2023-01-01'],
    'product': ['Widget A'],
    'quantity': [10],
    'price': [5.0]
})
test_logic(df1)

print("\n--- Test Case 2: Mixed case 'ReVeNuE' ---")
df2 = pd.DataFrame({
    'Date': ['2023-01-02'],
    'Product': ['Widget B'],
    'Quantity': [5],
    'ReVeNuE': [100.0]
})
test_logic(df2)

print("\n--- Test Case 3: Missing columns ---")
df3 = pd.DataFrame({
    'Date': ['2023-01-03'],
    'Qty': [5] 
})
test_logic(df3)
