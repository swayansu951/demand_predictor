import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import os
import time

# Page Config
st.set_page_config(
    page_title="ShopPulse | Demand Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Connection
DB_NAME = "shop_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    """Ensure table exists even if init_db.py wasn't run"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Sidebar ---
st.sidebar.title("📈 ShopPulse")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔮 Demand Prediction", "📂 Upload Data"])
st.sidebar.markdown("---")
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
st.sidebar.info("💡 **Tip:** Upload new sales data regularly for better predictions.")

# --- Custom CSS Styling ---
if dark_mode:
    # DARK MODE CSS
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #262730;
        }
        [data-testid="stSidebar"] * {
            color: #fafafa !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #fafafa !important;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }
        
        /* Metrics Cards */
        div[data-testid="metric-container"] {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border-left: 5px solid #3498db;
        }
        div[data-testid="metric-container"] label {
            color: #fafafa !important;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #fafafa !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Upload Box */
        .upload-box {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        .upload-box h3, .upload-box p {
            color: #fafafa !important;
        }
        </style>
        """, unsafe_allow_html=True)
else:
    # LIGHT MODE CSS
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #f8f9fa;
            color: #000000;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #2c3e50;
        }
        [data-testid="stSidebar"] * {
            color: #ecf0f1 !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #000000;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }
        
        /* Metrics Cards */
        div[data-testid="metric-container"] {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }
        div[data-testid="metric-container"] label {
            color: #000000 !important;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #000000 !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #000000 !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Upload Box */
        .upload-box {
            background-color: white !important;
            color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# --- Dashboard Page ---
if page == "📊 Dashboard":
    st.title("📊 Business Overview")
    st.markdown("Welcome back! Here's how your shop is performing.")
    
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        total_sales = df['quantity'].sum()
        total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
        unique_products = df['product_name'].nunique()
        latest_date = df['date'].max().strftime('%b %d, %Y')
        
        col1.metric("Total Units Sold", f"{total_sales:,.0f}")
        col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        col3.metric("Active Products", unique_products)
        col4.metric("Last Update", latest_date)
        
        st.markdown("---")
        
        # Charts Row 1
        c1, c2 = st.columns(2)
        
        chart_bgcolor = '#262730' if dark_mode else 'white'
        font_color = '#fafafa' if dark_mode else '#000000'
        
        with c1:
            st.subheader("📈 Sales Trend")
            sales_over_time = df.groupby('date')['quantity'].sum().reset_index()
            fig_time = px.area(sales_over_time, x='date', y='quantity', 
                             title='Daily Sales Volume',
                             color_discrete_sequence=['#3498db'])
            fig_time.update_layout(
                plot_bgcolor=chart_bgcolor, 
                paper_bgcolor=chart_bgcolor,
                font_color=font_color
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
        with c2:
            st.subheader("🏆 Top Products")
            product_dist = df.groupby('product_name')['quantity'].sum().reset_index().sort_values('quantity', ascending=True).tail(10)
            fig_prod = px.bar(product_dist, y='product_name', x='quantity', orientation='h',
                            title='Best Selling Products',
                            color='quantity',
                            color_continuous_scale='Blues')
            fig_prod.update_layout(
                plot_bgcolor=chart_bgcolor, 
                paper_bgcolor=chart_bgcolor,
                font_color=font_color
            )
            st.plotly_chart(fig_prod, use_container_width=True)
            
    else:
        st.info("👋 Welcome! Please go to the **Upload Data** page to get started.")

# --- Prediction Page ---
elif page == "🔮 Demand Prediction":
    st.title("🔮 AI Demand Forecast")
    st.markdown("Predict future inventory needs using our smart algorithms.")
    
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        products = sorted(df['product_name'].unique())
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("### Configuration")
            selected_product = st.selectbox("Select Product", products)
            forecast_days = st.slider("Forecast Days", 7, 60, 30)
            
        with col2:
            if selected_product:
                # Filter data for product
                product_data = df[df['product_name'] == selected_product].copy()
                product_data = product_data.groupby('date')['quantity'].sum().reset_index()
                product_data = product_data.sort_values('date')
                
                if len(product_data) < 5:
                    st.warning("⚠️ Not enough data points to make a reliable prediction. Need at least 5 days of data.")
                else:
                    # Prepare data for Linear Regression
                    product_data['date_ordinal'] = product_data['date'].map(datetime.toordinal)
                    
                    X = product_data[['date_ordinal']]
                    y = product_data['quantity']
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Predict next N days
                    last_date = product_data['date'].max()
                    future_dates = [last_date + timedelta(days=x) for x in range(1, forecast_days + 1)]
                    future_ordinals = [[d.toordinal()] for d in future_dates]
                    
                    future_predictions = model.predict(future_ordinals)
                    future_predictions = [max(0, p) for p in future_predictions]
                    
                    # Create DataFrame for plotting
                    future_df = pd.DataFrame({
                        'date': future_dates,
                        'quantity': future_predictions,
                        'type': 'Predicted'
                    })
                    
                    product_data['type'] = 'Historical'
                    
                    combined_df = pd.concat([product_data[['date', 'quantity', 'type']], future_df])
                    
                    # Plot
                    chart_bgcolor = '#262730' if dark_mode else 'white'
                    font_color = '#fafafa' if dark_mode else '#2c3e50'

                    fig_forecast = px.line(combined_df, x='date', y='quantity', color='type', 
                                         title=f'Demand Forecast: {selected_product}',
                                         color_discrete_map={"Historical": "#95a5a6", "Predicted": "#2ecc71"},
                                         markers=True)
                    
                    fig_forecast.add_vline(x=last_date.timestamp() * 1000, line_width=1, line_dash="dash", line_color="red")
                    fig_forecast.update_layout(
                        plot_bgcolor=chart_bgcolor, 
                        paper_bgcolor=chart_bgcolor, 
                        font_color=font_color,
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig_forecast, use_container_width=True)
                    
                    # Insights
                    avg_predicted = sum(future_predictions) / len(future_predictions)
                    current_avg = product_data['quantity'].mean()
                    growth = ((avg_predicted - current_avg) / current_avg) * 100
                    
                    st.markdown("### 💡 Insights")
                    i1, i2, i3 = st.columns(3)
                    i1.metric("Predicted Avg Daily Demand", f"{avg_predicted:.1f} units")
                    i2.metric("Expected Growth", f"{growth:+.1f}%", delta_color="normal")
                    i3.metric("Recommended Stock", f"{sum(future_predictions):.0f} units", help=f"Total units needed for next {forecast_days} days")
                    
                    st.markdown("### 🤖 Suggestion")
                    if growth > 20:
                        suggestion = f"🚀 **High Demand Alert!** Sales for **{selected_product}** are expected to surge by {growth:.1f}%. Consider increasing your inventory orders immediately to avoid stockouts."
                        box_color = "#d4edda" if not dark_mode else "#1e4620"
                        text_color = "black" if not dark_mode else "#d4edda"
                    elif growth > 5:
                        suggestion = f"📈 **Steady Growth.** Demand is rising moderately ({growth:.1f}%). Maintain healthy stock levels and monitor closely."
                        box_color = "#fff3cd" if not dark_mode else "#4d3e14"
                        text_color = "black" if not dark_mode else "#fff3cd"
                    elif growth > -5:
                        suggestion = f"⚖️ **Stable Demand.** Sales are expected to remain consistent. Standard restocking is recommended."
                        box_color = "#d1ecf1" if not dark_mode else "#103f47"
                        text_color = "black" if not dark_mode else "#d1ecf1"
                    else:
                        suggestion = f"📉 **Declining Trend.** Demand is projected to drop by {abs(growth):.1f}%. Consider running a promotion or reducing future orders to prevent overstocking."
                        box_color = "#f8d7da" if not dark_mode else "#4c1d21"
                        text_color = "black" if not dark_mode else "#f8d7da"
                        
                    st.markdown(f"""
                    <div style="background-color: {box_color}; color: {text_color}; padding: 15px; border-radius: 10px; border-left: 5px solid {text_color};">
                        {suggestion}
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.warning("Please upload data first.")

# --- Upload Data Page ---
elif page == "📂 Upload Data":
    st.title("📂 Data Management")
    
    with st.container():
        st.markdown("""
        <div class='upload-box' style='padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h3>Upload New Sales Records</h3>
            <p>Upload your Excel file to update the database. Ensure columns: <b>Date, Product, Quantity</b>. Optional: <b>Price</b> (to auto-calculate Revenue).</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Manage Files Section
        with st.expander("🗑️ Manage Saved Files"):
            save_dir = "uploaded_files"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            files = os.listdir(save_dir)
            st.write(f"**Total Saved Files:** {len(files)}")
            
            #deleting old file 
            if len(files) > 0:
                if st.button("Clear All Saved Files", type="primary"):
                    deleted_count = 0
                    for f in files:
                        try:
                            os.remove(os.path.join(save_dir, f))
                            deleted_count += 1
                        except Exception as e:
                            st.error(f"Error deleting {f}: {e}")
                    
                    if deleted_count > 0:
                        st.success(f"Deleted {deleted_count} files.")
                        st.rerun()
            else:
                st.info("No files to clear.")

        st.write("") # Spacer
        
        uploaded_file = st.file_uploader("Drop your Excel file here", type=["xlsx", "xls"])



        if uploaded_file is not None:
            try:
                # Save the file to disk
                save_dir = "uploaded_files"
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                
                timestamp = int(time.time())
                original_filename = uploaded_file.name
                saved_filename = f"{timestamp}_{original_filename}"
                file_path = os.path.join(save_dir, saved_filename)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"File saved locally as: {saved_filename}")

                df = pd.read_excel(uploaded_file)
                st.success("File uploaded successfully!")
                
                with st.expander("👀 Preview Data"):
                    st.dataframe(df.head())

                # Validate columns
                # Normalize columns for case-insensitive matching
                col_map = {str(col).lower().strip(): col for col in df.columns}
                required_keys = ['date', 'product', 'quantity']
                
                if all(key in col_map for key in required_keys):
                    if st.button("💾 Save to Database", use_container_width=True):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        total_rows = len(df)
                        
                        # Get actual column names from the map
                        date_col = col_map['date']
                        prod_col = col_map['product']
                        qty_col = col_map['quantity']
                        price_col = col_map.get('price')
                        rev_col = col_map.get('revenue')

                        for index, row in df.iterrows():
                            try:
                                date_str = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
                                
                                # Calculate Revenue
                                quantity = row[qty_col]
                                if price_col and pd.notna(row[price_col]):
                                    revenue = quantity * row[price_col]
                                elif rev_col and pd.notna(row[rev_col]):
                                    revenue = row[rev_col]
                                else:
                                    revenue = 0.0
                                
                                cursor.execute('''
                                    INSERT INTO sales (date, product_name, quantity, revenue)
                                    VALUES (?, ?, ?, ?)
                                ''', (date_str, row[prod_col], quantity, revenue))
                            except Exception as e:
                                st.warning(f"Skipping row {index}: {e}")
                                continue
                            
                            if index % 10 == 0:
                                progress = min(index / total_rows, 1.0)
                                progress_bar.progress(progress)
                                status_text.text(f"Processing row {index}/{total_rows}...")
                                
                        conn.commit()
                        conn.close()
                        progress_bar.progress(1.0)
                        status_text.text("Done!")
                        st.balloons()
                        st.success(f"✅ Successfully added {total_rows} records!")
                else:
                    st.error(f"❌ Missing columns. Required: Date, Product, Quantity (case-insensitive)")
            except Exception as e:
                st.error(f"Error: {e}")


