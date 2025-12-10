import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_percentage_error
import numpy as np
from datetime import datetime, timedelta
import os
import time
import extra_streamlit_components as stx

# --- Constants & Setup ---
USERS_DIR = "users"
DEFAULT_USER = "DefaultUser"

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# --- User Management Functions ---
def get_users():
    """Get list of existing users"""
    if not os.path.exists(USERS_DIR):
        return []
    return [d for d in os.listdir(USERS_DIR) if os.path.isdir(os.path.join(USERS_DIR, d))]

def create_user(username):
    """Create a new user workspace with empty structure"""
    user_dir = os.path.join(USERS_DIR, username)
    if os.path.exists(user_dir):
        return False
    
    # Create user directories
    # Create user directories
    os.makedirs(user_dir, exist_ok=True)
    os.makedirs(os.path.join(user_dir, "projects"), exist_ok=True)
    os.makedirs(os.path.join(user_dir, "uploaded_files"), exist_ok=True)
    
    # Initialize empty database
    user_db = os.path.join(user_dir, "data.db")
    init_db(user_db)
    
    return True

def init_user_workspace(username):
    """Ensure user workspace exists with proper structure"""
    user_dir = os.path.join(USERS_DIR, username)
    if not os.path.exists(user_dir):
        create_user(username)

# --- Page Config ---
st.set_page_config(
    page_title="ShopPulse | Demand Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database Functions ---
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def init_db(db_path):
    """Ensure table exists in the specified database"""
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

# --- Sidebar & User/Project Selection ---
# --- Authentication & Session Management ---
import auth

# Initialize Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Initialize Cookie Manager
cookie_manager = stx.CookieManager()

# Try Auto Login
auth.auto_login(cookie_manager)

# Show Login/Signup if not authenticated
if not st.session_state.authenticated:
    st.title("🔐 ShopPulse Authentication")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        auth.login_form(cookie_manager)
        
    with tab2:
        auth.signup_form()
        
    st.stop() # Stop execution here until logged in

# --- Authenticated User Workspace ---
# Initialize current user workspace
init_user_workspace(st.session_state.current_user)
user_dir = os.path.join(USERS_DIR, st.session_state.current_user)

# --- Sidebar ---
st.sidebar.title("📈 ShopPulse")
st.sidebar.markdown(f"**Welcome, {st.session_state.current_user}!**")

if st.sidebar.button("Logout", type="secondary"):
    auth.logout(cookie_manager)

st.sidebar.markdown("---")

st.sidebar.markdown("---")

# Project Selection
st.sidebar.subheader("🗂️ Workspace")
user_projects_dir = os.path.join(user_dir, "projects")
projects = [d for d in os.listdir(user_projects_dir) if os.path.isdir(os.path.join(user_projects_dir, d))]
project_options = ["Default Project"] + projects
selected_project = st.sidebar.selectbox("Select Project", project_options)

# Determine Paths based on selection (user-specific)
if selected_project == "Default Project":
    current_db_path = os.path.join(user_dir, "data.db")
    current_upload_dir = os.path.join(user_dir, "uploaded_files")
else:
    project_path = os.path.join(user_projects_dir, selected_project)
    current_db_path = os.path.join(project_path, "data.db")
    current_upload_dir = os.path.join(project_path, "uploads")

# Ensure directories exist
if not os.path.exists(current_upload_dir):
    os.makedirs(current_upload_dir)
# Ensure DB exists for selected project
init_db(current_db_path)

st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔮 Demand Prediction", "📂 Upload Data"])
st.sidebar.markdown("---")
# dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)
st.sidebar.info(f"👤 **User:** {st.session_state.current_user}")
st.sidebar.info(f"🎯 **Project:** {selected_project}")

# --- Custom CSS Styling ---
# if dark_mode:
    # DARK MODE CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        background-image: linear-gradient(to bottom right, #0e1117, #161b22);
        color: #fafafa;
        font-family: 'Poppins', sans-serif;
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
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #3498db;
    }
    div[data-testid="metric-container"] label {
        color: #b2bec3 !important;
        font-size: 0.9rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #fafafa !important;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.5);
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #2d3436;
    }
    
    /* Upload Box */
    .upload-box {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        color: #fafafa !important;
        border: 1px dashed #3498db;
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
# else:
#     # LIGHT MODE CSS
#     st.markdown("""
#         <style>
#         @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
#         /* Main Background */
#         .stApp {
#             background-color: #f8f9fa;
#             color: #2d3436;
#             font-family: 'Poppins', sans-serif;
#         }
        
#         /* Sidebar */
#         [data-testid="stSidebar"] {
#             background-color: #ffffff;
#             border-right: 1px solid #e0e0e0;
#         }
#         [data-testid="stSidebar"] * {
#             color: #2d3436 !important;
#         }
        
#         /* Headers */
#         h1, h2, h3 {
#             color: #2d3436 !important;
#             font-family: 'Poppins', sans-serif;
#             font-weight: 700;
#         }
        
#         /* Metrics Cards */
#         div[data-testid="metric-container"] {
#             background: white;
#             padding: 20px;
#             border-radius: 15px;
#             box-shadow: 0 4px 20px rgba(0,0,0,0.05);
#             border: 1px solid #f0f0f0;
#             transition: transform 0.3s ease;
#         }
#         div[data-testid="metric-container"]:hover {
#             transform: translateY(-5px);
#             border-color: #3498db;
#         }
        
#         /* Buttons */
#         .stButton>button {
#             background: linear-gradient(90deg, #3498db, #2980b9);
#             color: white;
#             border-radius: 10px;
#             border: none;
#             padding: 12px 28px;
#             font-weight: 600;
#             box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
#         }
        
#         /* Upload Box */
#         .upload-box {
#             background: white !important;
#             color: #2d3436 !important;
#             border: 1px dashed #3498db;
#         }
#         </style>
#         """, unsafe_allow_html=True)

# --- Dashboard Page ---
if page == "📊 Dashboard":
    st.title("📊 Business Overview")
    st.markdown(f"Overview for **{selected_project}**")
    
    conn = get_db_connection(current_db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM sales", conn)
    except Exception:
        df = pd.DataFrame()
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
        
        chart_bgcolor = '#262730' #if dark_mode else 'white'
        font_color = '#fafafa' #if dark_mode else '#000000'
        
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
    st.markdown(f"Predictions for **{selected_project}**")
    
    conn = get_db_connection(current_db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM sales", conn)
    except Exception:
        df = pd.DataFrame()
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

                    # Calculate Training Accuracy (Goodness of Fit)
                    y_pred_train = model.predict(X)
                    r2_train = r2_score(y, y_pred_train)
                    try:
                        mape_train = mean_absolute_percentage_error(y, y_pred_train)
                    except:
                        mape_train = 0.0
                    acc_train = max(0, (1 - mape_train) * 100)
                    
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
                    chart_bgcolor = '#262730' #if dark_mode else 'white'
                    font_color = '#fafafa' #if dark_mode else '#2c3e50'

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
                    i3.metric("Model Confidence", f"{acc_train:.1f}%", help=f"Historical Accuracy based on R2: {r2_train:.2f}")
                    
                    st.markdown("### 🤖 Suggestion")
                    if growth > 20:
                        suggestion = f"🚀 **High Demand Alert!** Sales for **{selected_product}** are expected to surge by {growth:.1f}%. Consider increasing your inventory orders immediately to avoid stockouts."
                        box_color = "#d4edda" #if not dark_mode else "#1e4620"
                        text_color = "black" #if not dark_mode else "#d4edda"
                    elif growth > 5:
                        suggestion = f"📈 **Steady Growth.** Demand is rising moderately ({growth:.1f}%). Maintain healthy stock levels and monitor closely."
                        box_color = "#fff3cd" #if not dark_mode else "#4d3e14"
                        text_color = "black" #if not dark_mode else "#fff3cd"
                    elif growth > -5:
                        suggestion = f"⚖️ **Stable Demand.** Sales are expected to remain consistent. Standard restocking is recommended."
                        box_color = "#d1ecf1" #if not dark_mode else "#103f47"
                        text_color = "black" #if not dark_mode else "#d1ecf1"
                    else:
                        suggestion = f"📉 **Declining Trend.** Demand is projected to drop by {abs(growth):.1f}%. Consider running a promotion or reducing future orders to prevent overstocking."
                        box_color = "#f8d7da" #if not dark_mode else "#4c1d21"
                        text_color = "black" #if not dark_mode else "#f8d7da"
                        
                    st.markdown(f"""
                    <div style="background-color: {box_color}; color: {text_color}; padding: 15px; border-radius: 10px; border-left: 5px solid {text_color};">
                        {suggestion}
                    </div>
                    """, unsafe_allow_html=True)

# --- Helper Functions ---
def process_excel_file(file_path, db_path, mode="Append"):
    """
    Reads an Excel file and efficiently loads it into the database using bulk operations.
    Returns: (success_bool, message_string, count_int)
    """
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        df_load = pd.read_excel(file_path)
        
        # Validate columns
        col_map = {str(col).lower().strip(): col for col in df_load.columns}
        required_keys = ['date', 'product', 'quantity']
        
        if not all(key in col_map for key in required_keys):
            conn.close()
            return False, "❌ File missing required columns (Date, Product, Quantity).", 0

        if mode == "Replace Database":
            cursor.execute("DELETE FROM sales")
        
        # Insert data
        date_col = col_map['date']
        prod_col = col_map['product']
        qty_col = col_map['quantity']
        price_col = col_map.get('price')
        rev_col = col_map.get('revenue')

        # --- OPTIMIZED BULK LOAD ---
        # 1. Pre-process Data in Memory (Vectorized)
        df_load.rename(columns={
            date_col: 'date',
            prod_col: 'product_name',
            qty_col: 'quantity'
        }, inplace=True)
        
        # Format Date
        df_load['date'] = pd.to_datetime(df_load['date']).dt.strftime('%Y-%m-%d')
        
        # Calculate Revenue
        if price_col and price_col in df_load.columns:
            df_load['revenue'] = df_load['quantity'] * df_load[price_col].fillna(0)
        elif rev_col and rev_col in df_load.columns:
            df_load['revenue'] = df_load[rev_col].fillna(0)
        else:
            df_load['revenue'] = 0.0
            
        # Keep only necessary columns
        final_df = df_load[['date', 'product_name', 'quantity', 'revenue']].copy()
        
        # 2. Database Transaction
        inserted_count = len(final_df)
        try:
            # Dump to temp table
            final_df.to_sql('temp_sales_import', conn, if_exists='replace', index=False)
            
            # Bulk Delete (Deduplication)
            # Remove rows from 'sales' that match (date, product) in temp table
            cursor.execute('''
                DELETE FROM sales 
                WHERE EXISTS (
                    SELECT 1 FROM temp_sales_import 
                    WHERE sales.date = temp_sales_import.date 
                    AND sales.product_name = temp_sales_import.product_name
                )
            ''')
            
            # Bulk Insert
            cursor.execute('''
                INSERT INTO sales (date, product_name, quantity, revenue)
                SELECT date, product_name, quantity, revenue FROM temp_sales_import
            ''')
            
            # Cleanup
            cursor.execute("DROP TABLE temp_sales_import")
            conn.commit()
        except Exception as db_err:
            conn.rollback()
            raise db_err
            
        conn.close()
        return True, f"✅ Successfully loaded {inserted_count} records!", inserted_count
        
    except Exception as e:
        return False, f"Error processing file: {e}", 0

# --- Upload Data Page ---
if page == "📂 Upload Data":
    st.title("📂 Data Management")
    
    with st.container():
        st.markdown("""
        <div class='upload-box' style='padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h3>Upload New Sales Records</h3>
            <p>DataFrame columns: <b>Date, Product, Quantity</b>. Optional: <b>Price</b>.</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        
        # --- NEW: Direct Upload Section ---
        col_up1, col_up2 = st.columns([2, 1])
        
        with col_up1:
            uploaded_file = st.file_uploader("Choose Excel File", type=["xlsx", "xls"])
            
        with col_up2:
            st.write("<b>Settings</b>", unsafe_allow_html=True)
            upload_destination = st.radio("Target", ["Current Project", "New Project"], horizontal=False, label_visibility="collapsed")
            new_project_name = ""
            if upload_destination == "New Project":
                new_project_name = st.text_input("Project Name", placeholder="New Project Name")

        if uploaded_file is not None:
             if st.button("🚀 Save & Process Data", type="primary", use_container_width=True):
                try:
                    # 1. Determine Paths
                    if upload_destination == "New Project" and new_project_name.strip():
                        safe_project_name = "".join([c for c in new_project_name if c.isalnum() or c in (' ', '_', '-')]).strip()
                        if not safe_project_name:
                            st.error("Invalid project name.")
                            st.stop()
                        target_project_dir = os.path.join(user_projects_dir, safe_project_name)
                        active_upload_dir = os.path.join(target_project_dir, "uploads")
                        active_db_path = os.path.join(target_project_dir, "data.db")
                        
                        if not os.path.exists(active_upload_dir):
                            os.makedirs(active_upload_dir)
                        init_db(active_db_path)
                        st.success(f"Created project: **{safe_project_name}**")
                    else:
                        active_upload_dir = current_upload_dir
                        active_db_path = current_db_path

                    # 2. Save File
                    original_filename = uploaded_file.name
                    
                    # Deduplicate local file
                    existing_files = os.listdir(active_upload_dir)
                    for existing_file in existing_files:
                        try:
                            parts = existing_file.split('_', 1)
                            if len(parts) > 1:
                                stored_filename = parts[1]
                                if stored_filename.lower() == original_filename.lower():
                                    os.remove(os.path.join(active_upload_dir, existing_file))
                        except Exception:
                            continue

                    timestamp = int(time.time())
                    saved_filename = f"{timestamp}_{original_filename}"
                    file_path = os.path.join(active_upload_dir, saved_filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.info(f"File saved: {saved_filename}")

                    # 3. Process & Load to DB
                    success, msg, count = process_excel_file(file_path, active_db_path, mode="Append")
                    
                    if success:
                        st.success(msg)
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(msg)
                        
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        
        # Manage Data Section (Collapsed)
        with st.expander("🗑️ Manage Saved Files & Database"):
            # --- File Management ---
            st.subheader("📂 Saved Files")
            
            files = os.listdir(current_upload_dir)
            st.write(f"**Total Saved Files:** {len(files)}")
            
            # --- Load Saved File ---
            if len(files) > 0:
                col_load1, col_load2 = st.columns([3, 1])
                with col_load1:
                    file_to_load = st.selectbox("Load existing file", ["Select..."] + files)
                
                if file_to_load != "Select...":
                    load_mode = st.radio("Mode", ["Append to Database", "Replace Database"], horizontal=True)
                    
                    if st.button("Re-Load Data", type="primary"):
                        file_path = os.path.join(current_upload_dir, file_to_load)
                        success, msg, count = process_excel_file(file_path, current_db_path, mode=load_mode)
                        if success:
                            st.success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)
            
            st.markdown("---")
            
            # --- Delete Files ---
            if len(files) > 0:
                files_to_delete = st.multiselect("Select files to delete", files)
                if st.button("🗑️ Delete Selected"):
                     for f in files_to_delete:
                        try:
                            os.remove(os.path.join(current_upload_dir, f))
                        except: pass
                     st.rerun()

            st.markdown("---")

            # --- Database Management ---
            conn = get_db_connection(current_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]
            conn.close()
            
            st.write(f"**Total Sales Records:** {count}")
            
            if count > 0:
                if st.button("Clear All Database Records", type="primary"):
                    conn = get_db_connection(current_db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sales")
                    conn.commit()
                    conn.close()
                    st.success("Cleared.")
                    st.rerun()

