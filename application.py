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
PROJECTS_DIR = "projects"
DEFAULT_DB = "shop_data.db"

if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

def get_db_connection(db_path=DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    return conn

def init_db(db_path=DEFAULT_DB):
    """Ensure table exists even if init_db.py wasn't run"""
    conn = get_db_connection(db_path)
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

# Initialize default DB
init_db()

# --- Sidebar ---
st.sidebar.title("📈 ShopPulse")
st.sidebar.markdown("---")

# Project Selection
st.sidebar.subheader("🗂️ Project")
project_options = ["Default"] + [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
selected_project = st.sidebar.selectbox("Select Project", project_options)

if selected_project == "Default":
    current_db_path = DEFAULT_DB
    current_upload_dir = "uploaded_files"
else:
    current_db_path = os.path.join(PROJECTS_DIR, selected_project, "data.db")
    current_upload_dir = os.path.join(PROJECTS_DIR, selected_project, "uploads")

# Ensure directories exist for the selected project (if not default)
if selected_project != "Default":
    if not os.path.exists(current_upload_dir):
        os.makedirs(current_upload_dir)
    # Initialize DB if it doesn't exist
    init_db(current_db_path)

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔮 Demand Prediction", "📂 Upload Data"])
st.sidebar.markdown("---")
dark_mode = st.sidebar.checkbox("🌙 Dark Mode")
st.sidebar.info(f"💡 **Project:** {selected_project}")

# --- Custom CSS Styling ---
if dark_mode:
    # DARK MODE CSS
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* Main Background */
        .stApp {
            background-color: #0e1117;
            background-image: linear-gradient(to bottom right, #0e1117, #161b22);
            color: #fafafa;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1a1c24;
            border-right: 1px solid #2d3436;
        }
        [data-testid="stSidebar"] * {
            color: #dfe6e9 !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #fafafa !important;
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Metrics Cards - Glassmorphism */
        div[data-testid="metric-container"] {
            background: rgba(38, 39, 48, 0.7);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 5px solid #3498db;
            transition: transform 0.2s;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-5px);
        }
        div[data-testid="metric-container"] label {
            color: #b2bec3 !important;
            font-size: 0.9rem;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #fafafa !important;
            font-weight: 700;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #3498db, #2980b9);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 12px 28px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border: 1px solid #2d3436;
        }
        
        /* Upload Box */
        .upload-box {
            background: rgba(38, 39, 48, 0.7) !important;
            backdrop-filter: blur(10px);
            color: #fafafa !important;
            border: 1px dashed #444;
        }
        .upload-box h3, .upload-box p {
            color: #fafafa !important;
        }

        /* Radio Buttons (Navigation) */
        div[row-widget="radio"] > div {
            flex-direction: row;
            align-items: stretch;
            background-color: transparent;
        }
        div[row-widget="radio"] label {
            background-color: #262730;
            border: 1px solid #444;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 8px;
            transition: all 0.3s;
            cursor: pointer;
            font-weight: 500;
        }
        div[row-widget="radio"] label:hover {
            background-color: #34495e;
            border-color: #3498db;
            transform: translateX(5px);
        }
        div[row-widget="radio"] label[data-baseweb="radio"] {
            background: linear-gradient(90deg, #3498db, #2980b9) !important;
            border-color: transparent !important;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)
else:
    # LIGHT MODE CSS
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        /* Global Font */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* Main Background */
        .stApp {
            background-color: #f8f9fa;
            background-image: linear-gradient(to bottom right, #f8f9fa, #e9ecef);
            color: #2d3436;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
        }
        [data-testid="stSidebar"] * {
            color: #2d3436 !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #2d3436;
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Metrics Cards */
        div[data-testid="metric-container"] {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border-left: 5px solid #3498db;
            transition: transform 0.2s;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-5px);
        }
        div[data-testid="metric-container"] label {
            color: #636e72 !important;
            font-size: 0.9rem;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #2d3436 !important;
            font-weight: 700;
        }
        div[data-testid="stMetricLabel"] {
            color: #2d3436 !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #3498db, #2980b9);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 12px 28px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid #e9ecef;
        }
        
        /* Upload Box */
        .upload-box {
            background-color: white !important;
            color: #2d3436 !important;
            border: 1px dashed #bdc3c7;
        }

        /* Radio Buttons (Navigation) */
        div[row-widget="radio"] > div {
            flex-direction: row;
            align-items: stretch;
            background-color: transparent;
        }
        div[row-widget="radio"] label {
            background-color: #f1f2f6;
            border: 1px solid #dfe6e9;
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 8px;
            transition: all 0.3s;
            cursor: pointer;
            color: #2c3e50 !important;
            font-weight: 500;
        }
        div[row-widget="radio"] label:hover {
            background-color: #dfe6e9;
            border-color: #3498db;
            transform: translateX(5px);
        }
        div[row-widget="radio"] label[data-baseweb="radio"] {
            background: linear-gradient(90deg, #3498db, #2980b9) !important;
            border-color: transparent !important;
            color: white !important;
            box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)

# --- Dashboard Page ---
if page == "📊 Dashboard":
    st.title("📊 Business Overview")
    st.markdown("Welcome back! Here's how your shop is performing.")
    
    conn = get_db_connection(current_db_path)
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
    
    conn = get_db_connection(current_db_path)
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
        
        # Manage Data Section
        with st.expander("🗑️ Manage Data"):
            # --- File Management ---
            st.subheader("📂 Saved Files")
            
            if not os.path.exists(current_upload_dir):
                os.makedirs(current_upload_dir)
            
            files = os.listdir(current_upload_dir)
            st.write(f"**Total Saved Files:** {len(files)}")
            
            #deleting old file 
            if len(files) > 0:
                files_to_delete = st.multiselect("Select files to delete", files)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete Selected", type="primary", use_container_width=True):
                        if files_to_delete:
                            deleted_count = 0
                            for f in files_to_delete:
                                try:
                                    os.remove(os.path.join(current_upload_dir, f))
                                    deleted_count += 1
                                except Exception as e:
                                    st.error(f"Error deleting {f}: {e}")
                            
                            if deleted_count > 0:
                                st.success(f"Deleted {deleted_count} files.")
                                time.sleep(0.5)
                                st.rerun()
                        else:
                            st.warning("Please select files to delete.")
                            
                with col2:
                    if st.button("⚠️ Clear All Files", type="secondary", use_container_width=True):
                        deleted_count = 0
                        for f in files:
                            try:
                                os.remove(os.path.join(current_upload_dir, f))
                                deleted_count += 1
                            except Exception as e:
                                st.error(f"Error deleting {f}: {e}")
                        
                        if deleted_count > 0:
                            st.success(f"Deleted {deleted_count} files.")
                            time.sleep(0.5)
                            st.rerun()
            else:
                st.info("No files to clear.")

            st.markdown("---")

            # --- Database Management ---
            st.subheader("🗄️ Database Records")
            
            conn = get_db_connection(current_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]
            conn.close()
            
            st.write(f"**Total Sales Records:** {count}")
            
            if count > 0:
                if st.button("Clear All Database Records", type="primary"):
                    try:
                        conn = get_db_connection(current_db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM sales")
                        conn.commit()
                        conn.close()
                        st.success("✅ All database records deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing database: {e}")
            else:
                st.info("Database is empty.")

            st.markdown("---")
            
            # --- Hard Reset ---
            st.subheader("⚠️ Danger Zone")
            if st.button("🧨 Delete Database File (Hard Reset)", type="primary"):
                try:
                    if os.path.exists(current_db_path):
                        os.remove(current_db_path)
                        st.success("✅ Database file deleted successfully! App will reload...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Database file not found.")
                except Exception as e:
                    st.error(f"Error deleting database file: {e}")

        st.write("") # Spacer
        
        # New Project Creation Option
        new_project_name = st.text_input("🆕 Create New Project (Optional)", placeholder="Enter project name to create a new separate workspace")
        
        uploaded_file = st.file_uploader("Drop your Excel file here", type=["xlsx", "xls"])

        if uploaded_file is not None:
            try:
                # Determine target paths
                if new_project_name.strip():
                    # Sanitize project name
                    safe_project_name = "".join([c for c in new_project_name if c.isalnum() or c in (' ', '_', '-')]).strip()
                    if not safe_project_name:
                        st.error("Invalid project name.")
                        st.stop()
                        
                    target_project_dir = os.path.join(PROJECTS_DIR, safe_project_name)
                    target_upload_dir = os.path.join(target_project_dir, "uploads")
                    target_db_path = os.path.join(target_project_dir, "data.db")
                    
                    if not os.path.exists(target_upload_dir):
                        os.makedirs(target_upload_dir)
                    
                    # Initialize DB for new project
                    init_db(target_db_path)
                    
                    st.success(f"Creating new project: **{safe_project_name}**")
                    active_upload_dir = target_upload_dir
                    active_db_path = target_db_path
                else:
                    active_upload_dir = current_upload_dir
                    active_db_path = current_db_path

                # Save the file to disk
                if not os.path.exists(active_upload_dir):
                    os.makedirs(active_upload_dir)
                
                timestamp = int(time.time())
                original_filename = uploaded_file.name
                saved_filename = f"{timestamp}_{original_filename}"
                file_path = os.path.join(active_upload_dir, saved_filename)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"File saved locally as: {saved_filename}")
                
                # Refresh to show the new file in the list
                time.sleep(1)
                st.rerun()

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
                        conn = get_db_connection(active_db_path)
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


