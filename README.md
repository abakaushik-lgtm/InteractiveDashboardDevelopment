# Premium Interactive Business Intelligence (BI) Dashboard

A state-of-the-art enterprise analytics dashboard built with **Python**, **Streamlit**, and **Plotly**. The platform transforms raw corporate transaction datasets into interactive insights, mimicking enterprise tools like Tableau, Power BI, and Google Data Studio.

## 🚀 Key Features

1. **Executive KPI Dashboard**: Renders elegant custom HTML/CSS KPI cards with period-over-period trend deltas (▲ and ▼) for Revenue, Profit, Margin, Customers, and Average Order Value (AOV).
2. **Dynamic Period-over-Period Calculations**: Computes relative metrics comparing the selected date window to the immediately preceding period of the same duration.
3. **Data Profiling Module**: Analyzes columns, detects null cells and duplicate rows, renders sample lists, and computes a composite **Data Quality Score**.
4. **Flexible Column Mapping UI**: Upload custom CSV, Excel, or JSON datasets, and map columns dynamically via the sidebar, making the dashboard fully compatible with any generic schema.
5. **Interactive Filter Panes**: Filter by Date Range, Region, Product Categories, Customer Segments, and Sales Channels.
6. **Detailed Visualization Tabs**:
   - **Executive Overview**: Primary revenue/profit trends, category contribution doughnut, and financial bar charts.
   - **Product Performance**: Top ranking bar charts and metrics grids with target comparison indicators.
   - **Geographic Insights**: Interactive natural earth choropleth map and regional rankings.
   - **Customer & Profitability**: Cohort retention heatmaps, customer purchase frequency funnels, and margin percentage trends.

---

## 🛠️ Folder Structure

```text
├── assets/
│   └── styles.css          # Custom styling for KPI cards, animations, and typography
├── utils/
│   ├── data_generator.py   # Simulates high-quality customer transaction mock data
│   ├── data_profiler.py    # Code quality analyzer and column profiling metrics
│   ├── ui_components.py    # Custom HTML metrics rendering and style injectors
│   └── visualizations.py   # Plotly Express and Graph Object chart configurations
├── app.py                  # Main Streamlit entrance and filter layout script
├── README.md               # User guide and instructions
```

---

## 📦 Requirements & Installation

This application requires Python 3.8+ and the following libraries:
- `streamlit`
- `pandas`
- `numpy`
- `plotly`
- `openpyxl` (for Excel imports)

To install the dependencies, execute:
```bash
pip install streamlit pandas numpy plotly openpyxl
```

---

## 🖥️ Running the Dashboard

Launch the Streamlit server from your terminal inside the project directory:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal (usually `http://localhost:8501`) in your browser.

---

## ⚡ Quick Test (Demo Data)

If you don't have a dataset ready, click the **"⚡ Load Demo BI Dataset"** button in the sidebar. This generates a synthetic 2-year customer transaction log (15,000 transactions) complete with holidays seasonality, regional skewness, and category-specific profitability margins to showcase all features immediately.
