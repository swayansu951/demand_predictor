# ShopPulse - Demand Predictor

ShopPulse is a web-based application that helps you analyze your sales data and predict future demand for your products. It provides a user-friendly interface to upload your sales data, visualize trends, and get AI-powered demand forecasts.

## Features

- **Sales Dashboard:** Get a comprehensive overview of your sales performance with key metrics like total sales, revenue, and top-selling products.
- **Demand Forecasting:** Predict future demand for your products using a linear regression model.
- **Data Upload:** Easily upload your sales data from an Excel file.
- **Interactive Charts:** Visualize your sales data with interactive charts and graphs.
- **Customizable Interface:** Switch between light and dark modes for a personalized experience.

## How to Use

1. **Prerequisites:**
   - Python 3.6+
   - The required Python libraries listed in `requirements.txt`.

2. **Installation:**
   - Clone this repository or download the source code.
   - Install the required libraries:
     ```bash
     pip install -r requirements.txt
     ```

3. **Running the Application:**
   - Run the following command in your terminal:
     ```bash
     streamlit run application.py
     ```
   - The application will open in your web browser.

4. **Using the Application:**
   - **Upload Data:** Go to the "Upload Data" page and upload your sales data in an Excel file. The file should have the following columns: `Date`, `Product`, and `Quantity`. You can also include a `Price` column to automatically calculate revenue.
   - **Dashboard:** Once the data is uploaded, the "Dashboard" will show your sales overview.
   - **Demand Prediction:** Go to the "Demand Prediction" page to get future demand forecasts for your products.

## Project Structure

- `application.py`: The main Streamlit web application file.
- `initial_db.py`: A script to initialize the SQLite database.
- `requirements.txt`: A file listing the Python dependencies.
- `Sample_Data.py`: A script to generate a sample sales data Excel file (`sample_sales_data.xlsx`).
- `verify_fix.py`: A script to test the data processing logic.
- `task.txt`: A development task list.
- `.devcontainer/`: Contains development container configuration.

## Dependencies

- `streamlit`
- `pandas`
- `openpyxl`
- `scikit-learn`
- `plotly`
- `matplotlib`
