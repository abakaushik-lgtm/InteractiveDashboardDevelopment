import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

# Import custom utilities
from utils.data_generator import generate_mock_data
from utils.data_profiler import profile_data
from utils.ui_components import load_css, render_kpi_grid, render_header
import utils.visualizations as viz

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="Executive Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Stylesheet
load_css("assets/styles.css")

# Helper to format currency
def format_currency(val):
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.1f}k"
    else:
        return f"${val:.2f}"

# Helper to format count
def format_count(val):
    if val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"{val / 1_000:.1f}k"
    else:
        return f"{val}"

# ----------------- SESSION STATE INIT -----------------
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = None
if "mapped_df" not in st.session_state:
    st.session_state["mapped_df"] = None
if "data_source" not in st.session_state:
    st.session_state["data_source"] = None

# ----------------- SIDEBAR: DATA INTEGRATION -----------------
with st.sidebar:
    st.markdown("### 📥 Data Integration")
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload dataset (CSV, XLSX, JSON)", 
        type=["csv", "xlsx", "json"],
        help="Upload your business records to populate the dashboard."
    )
    
    # Action buttons if no file uploaded
    if uploaded_file is None:
        st.markdown("<p style='text-align: center; color: #64748B;'>OR</p>", unsafe_allow_html=True)
        if st.button("⚡ Load Demo BI Dataset", use_container_width=True, type="primary"):
            with st.spinner("Generating demo sales dataset..."):
                demo_df = generate_mock_data()
                st.session_state["raw_df"] = demo_df
                st.session_state["mapped_df"] = demo_df.copy()
                st.session_state["data_source"] = "Demo System Dataset"
                st.success("Loaded demo dataset with 15,000 transactions!")
                
    # Read file if uploaded
    if uploaded_file is not None:
        try:
            filename = uploaded_file.name
            if filename.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            elif filename.endswith(".xlsx"):
                df_upload = pd.read_excel(uploaded_file)
            elif filename.endswith(".json"):
                df_upload = pd.read_json(uploaded_file)
                
            st.session_state["raw_df"] = df_upload
            st.session_state["data_source"] = f"Uploaded: {filename}"
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")

    # Column Mapping Section (Only if file is uploaded)
    if st.session_state["raw_df"] is not None and st.session_state["data_source"] != "Demo System Dataset":
        st.markdown("---")
        with st.sidebar.expander("⚙️ Map Dataset Columns", expanded=True):
            raw_cols = list(st.session_state["raw_df"].columns)
            
            # Helper for smart column detection
            def find_default_col(kw_list, cols):
                for kw in kw_list:
                    for col in cols:
                        if kw.lower() in col.lower():
                            return cols.index(col)
                return 0
                
            # Perform column selector bindings
            date_idx = find_default_col(["date", "time", "day"], raw_cols)
            region_idx = find_default_col(["region", "territory", "country", "geo"], raw_cols)
            prod_idx = find_default_col(["product", "item", "sku", "name"], raw_cols)
            sales_idx = find_default_col(["sales", "revenue", "amount", "turnover"], raw_cols)
            profit_idx = find_default_col(["profit", "gain", "margin"], raw_cols)
            cat_idx = find_default_col(["category", "cat", "class", "dept"], raw_cols)
            cust_idx = find_default_col(["customerid", "customer_id", "custid", "customers"], raw_cols)
            target_idx = find_default_col(["target", "budget", "goal"], raw_cols)
            
            # Form select boxes
            map_date = st.selectbox("Date Column", raw_cols, index=date_idx)
            map_region = st.selectbox("Region Column", raw_cols, index=region_idx)
            map_prod = st.selectbox("Product Column", raw_cols, index=prod_idx)
            map_sales = st.selectbox("Sales (Revenue)", raw_cols, index=sales_idx)
            map_profit = st.selectbox("Profit Column", raw_cols, index=profit_idx)
            map_cat = st.selectbox("Category Column", raw_cols, index=cat_idx)
            map_cust = st.selectbox("CustomerID Column", raw_cols, index=cust_idx)
            map_target = st.selectbox("Target Column (Optional)", ["None"] + raw_cols, index=target_idx + 1 if target_idx < len(raw_cols) else 0)
            
            if st.button("Apply Column Mapping", use_container_width=True):
                # Apply map and create standardized df
                mapped = pd.DataFrame()
                src_df = st.session_state["raw_df"]
                
                try:
                    mapped["Date"] = pd.to_datetime(src_df[map_date])
                    mapped["Region"] = src_df[map_region].astype(str)
                    mapped["Product"] = src_df[map_prod].astype(str)
                    mapped["Sales"] = pd.to_numeric(src_df[map_sales]).astype(float)
                    mapped["Profit"] = pd.to_numeric(src_df[map_profit]).astype(float)
                    mapped["Category"] = src_df[map_cat].astype(str)
                    
                    # Map Customer ID
                    mapped["CustomerID"] = src_df[map_cust].astype(str)
                    mapped["Customers"] = 1
                    
                    # Calculate Cost
                    mapped["Cost"] = mapped["Sales"] - mapped["Profit"]
                    
                    # Targets
                    if map_target != "None":
                        mapped["Target"] = pd.to_numeric(src_df[map_target]).astype(float)
                    else:
                        mapped["Target"] = mapped["Sales"] * 1.05  # Muted default target
                        
                    # Transfer other useful columns (like Segment, Channel) if they exist
                    for col in ["Segment", "Sales Channel"]:
                        found_col = find_default_col([col], raw_cols)
                        if raw_cols[found_col].lower() in [c.lower() for c in raw_cols]:
                            mapped[col] = src_df[raw_cols[found_col]].astype(str)
                        else:
                            # Generate mock if not exists
                            mapped[col] = "General"
                            
                    st.session_state["mapped_df"] = mapped.sort_values("Date").reset_index(drop=True)
                    st.success("Column mapping applied successfully!")
                except Exception as ex:
                    st.error(f"Mapping failed: {str(ex)}")

# ----------------- RENDER CORE CONTENT -----------------
if st.session_state["mapped_df"] is None:
    # Landing page layout before loading data
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; padding: 40px; background-color: #F8FAFC; border-radius: 16px; border: 1px solid #E2E8F0;'>
            <h1 style='color: #0F172A; font-family: Outfit, sans-serif; font-weight: 700; font-size: 2.5rem; margin-bottom: 10px;'>📊 Interactive Business Intelligence Dashboard</h1>
            <p style='color: #64748B; font-family: Outfit, sans-serif; font-size: 1.125rem; max-width: 600px; margin: 0 auto 30px auto;'>
                Transform raw transactional datasets into executive summaries, product performance tracking, regional insights, and cohort loyalty funnels.
            </p>
            <div style='display: inline-flex; gap: 15px; justify-content: center;'>
                <div style='text-align: left; background: white; padding: 15px 20px; border-radius: 8px; border: 1px solid #E2E8F0; width: 220px;'>
                    <span style='font-size: 1.5rem;'>⚡</span>
                    <h4 style='margin: 8px 0 4px 0; color: #1E293B;'>Demo Mode</h4>
                    <p style='margin: 0; font-size: 0.85rem; color: #64748B;'>Click the sidebar button to auto-generate a sales dataset instantly.</p>
                </div>
                <div style='text-align: left; background: white; padding: 15px 20px; border-radius: 8px; border: 1px solid #E2E8F0; width: 220px;'>
                    <span style='font-size: 1.5rem;'>📤</span>
                    <h4 style='margin: 8px 0 4px 0; color: #1E293B;'>Upload Files</h4>
                    <p style='margin: 0; font-size: 0.85rem; color: #64748B;'>Supports CSV, Excel, or JSON. Map custom column headers dynamically.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # We have data! Let's display the dashboard.
    df = st.session_state["mapped_df"]
    
    # ----------------- SIDEBAR FILTERS -----------------
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎛️ Filter Parameters")
        
        # Date Filter
        min_date = df["Date"].min().to_pydatetime()
        max_date = df["Date"].max().to_pydatetime()
        
        selected_date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Region Filter
        regions = sorted(df["Region"].unique())
        selected_regions = st.multiselect("Regions", regions, default=regions)
        
        # Category Filter
        categories = sorted(df["Category"].unique())
        selected_categories = st.multiselect("Product Categories", categories, default=categories)
        
        # Segment Filter (if present)
        segments = sorted(df["Segment"].unique()) if "Segment" in df.columns else []
        selected_segments = st.multiselect("Customer Segments", segments, default=segments) if segments else []
        
        # Channel Filter (if present)
        channels = sorted(df["Sales Channel"].unique()) if "Sales Channel" in df.columns else []
        selected_channels = st.multiselect("Sales Channels", channels, default=channels) if channels else []
        
        # Filter Reset
        if st.button("Reset All Filters", use_container_width=True):
            st.rerun()
            
        # Display current dataset status
        st.markdown("---")
        st.caption(f"**Data Origin:** {st.session_state['data_source']}")
        st.caption(f"**Total Dataset Rows:** {len(df):,}")

    # Apply filters
    # Make sure we handle empty/single date selection safely
    start_date = min_date
    end_date = max_date
    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_date = pd.to_datetime(selected_date_range[0])
        end_date = pd.to_datetime(selected_date_range[1])
    elif isinstance(selected_date_range, datetime) or isinstance(selected_date_range, pd.Timestamp):
        start_date = pd.to_datetime(selected_date_range)
        end_date = start_date
        
    # Apply categorical filters first (to compute correct Period-over-Period)
    filtered_df_pre_date = df.copy()
    if selected_regions:
        filtered_df_pre_date = filtered_df_pre_date[filtered_df_pre_date["Region"].isin(selected_regions)]
    if selected_categories:
        filtered_df_pre_date = filtered_df_pre_date[filtered_df_pre_date["Category"].isin(selected_categories)]
    if selected_segments:
        filtered_df_pre_date = filtered_df_pre_date[filtered_df_pre_date["Segment"].isin(selected_segments)]
    if selected_channels:
        filtered_df_pre_date = filtered_df_pre_date[filtered_df_pre_date["Sales Channel"].isin(selected_channels)]
        
    # Apply date filters to get current active dataset
    mask = (filtered_df_pre_date["Date"] >= start_date) & (filtered_df_pre_date["Date"] <= end_date)
    filtered_df = filtered_df_pre_date[mask]
    
    # Calculate Period-over-Period (PoP) metrics
    # Current active metrics
    curr_rev = filtered_df["Sales"].sum()
    curr_prof = filtered_df["Profit"].sum()
    curr_marg = (curr_prof / curr_rev * 100) if curr_rev > 0 else 0
    curr_cust = filtered_df["CustomerID"].nunique() if "CustomerID" in filtered_df.columns else len(filtered_df)
    curr_aov = (curr_rev / len(filtered_df)) if len(filtered_df) > 0 else 0
    
    # Previous period calculation
    duration_days = (end_date - start_date).days + 1
    prev_start_date = start_date - timedelta(days=duration_days)
    prev_end_date = start_date - timedelta(days=1)
    
    prev_mask = (filtered_df_pre_date["Date"] >= prev_start_date) & (filtered_df_pre_date["Date"] <= prev_end_date)
    prev_df = filtered_df_pre_date[prev_mask]
    
    prev_rev = prev_df["Sales"].sum()
    prev_prof = prev_df["Profit"].sum()
    prev_marg = (prev_prof / prev_rev * 100) if prev_rev > 0 else 0
    prev_cust = prev_df["CustomerID"].nunique() if "CustomerID" in prev_df.columns else len(prev_df)
    prev_aov = (prev_rev / len(prev_df)) if len(prev_df) > 0 else 0
    
    # Delta percentages
    def pct_change(curr, prev):
        if prev == 0:
            return None
        return round(((curr - prev) / prev) * 100, 1)
        
    rev_delta = pct_change(curr_rev, prev_rev)
    prof_delta = pct_change(curr_prof, prev_prof)
    marg_delta = round(curr_marg - prev_marg, 1)  # Absolute point change for margin
    cust_delta = pct_change(curr_cust, prev_cust)
    aov_delta = pct_change(curr_aov, prev_aov)

    # ----------------- RENDER HEADER -----------------
    render_header(
        "Executive Business Intelligence Dashboard",
        "A premium enterprise analytics workspace tracking sales operations, product categories, and buyer cohort metrics."
    )
    
    # ----------------- TABS SETUP -----------------
    # ==================== TABS SETUP ====================
    tab_overview, tab_products, tab_geography, tab_customers, tab_profiler = st.tabs([
        "📈 Executive Overview",
        "🏷️ Product & Category Performance",
        "🌍 Geographic Insights",
        "👥 Customer & Profitability",
        "⚙️ Data Profiling Module"
    ])
    
    # ==================== TAB 1: EXECUTIVE OVERVIEW ====================
    with tab_overview:
        # KPI Metric Grid
        cards_data = [
            {
                "title": "Total Revenue",
                "value": format_currency(curr_rev),
                "delta": f"{rev_delta}%" if rev_delta is not None else None,
                "is_delta_positive": rev_delta >= 0 if rev_delta is not None else True,
                "card_type": "default",
                "icon": "💵",
                "caption": "vs prev period"
            },
            {
                "title": "Total Profit",
                "value": format_currency(curr_prof),
                "delta": f"{prof_delta}%" if prof_delta is not None else None,
                "is_delta_positive": prof_delta >= 0 if prof_delta is not None else True,
                "card_type": "profit",
                "icon": "📈",
                "caption": "vs prev period"
            },
            {
                "title": "Profit Margin",
                "value": f"{curr_marg:.1f}%",
                "delta": f"{marg_delta:+.1f}%" if marg_delta != 0 else None,
                "is_delta_positive": marg_delta >= 0,
                "card_type": "growth",
                "icon": "⚖️",
                "caption": "pts vs prev period"
            },
            {
                "title": "Active Customers",
                "value": format_count(curr_cust),
                "delta": f"{cust_delta}%" if cust_delta is not None else None,
                "is_delta_positive": cust_delta >= 0 if cust_delta is not None else True,
                "card_type": "customers",
                "icon": "👥",
                "caption": "vs prev period"
            },
            {
                "title": "Avg Order Value (AOV)",
                "value": format_currency(curr_aov),
                "delta": f"{aov_delta}%" if aov_delta is not None else None,
                "is_delta_positive": aov_delta >= 0 if aov_delta is not None else True,
                "card_type": "aov",
                "icon": "🛍️",
                "caption": "vs prev period"
            }
        ]
        render_kpi_grid(cards_data)
        
        # Primary Sales Trend & Category Analysis (Side-by-Side to avoid vertical scrolling)
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            # Compact granularity selector and line plot
            c1, c2 = st.columns([2, 1])
            with c2:
                freq_select = st.segmented_control("Granularity", ["Day", "Month", "Year"], default="Month", label_visibility="collapsed")
            with c1:
                st.markdown("<p style='font-size:0.95rem; font-weight:600; margin-top:5px; color:#475569;'>Revenue & Profit Over Time</p>", unsafe_allow_html=True)
            trend_fig = viz.plot_revenue_trend(filtered_df, freq_select if freq_select else "Month")
            st.plotly_chart(trend_fig, use_container_width=True)
            
        with col_right:
            cat_view = st.segmented_control("Category Breakdown", ["Revenue Share", "Financials"], default="Revenue Share")
            if cat_view == "Revenue Share":
                st.plotly_chart(viz.plot_category_distribution(filtered_df), use_container_width=True)
            else:
                st.plotly_chart(viz.plot_category_profitability(filtered_df), use_container_width=True)

    # ==================== TAB 2: PRODUCT & CATEGORY PERFORMANCE ====================
    with tab_products:
        col_rank_select, col_empty = st.columns([2, 3])
        with col_rank_select:
            r1, r2 = st.columns(2)
            with r1:
                top_n = st.number_input("Products to Rank", min_value=3, max_value=25, value=8, step=1)
            with r2:
                metric_sort = st.selectbox("Rank By", ["Sales", "Profit"])
            
        col_rank_chart, col_rank_table = st.columns([3, 2])
        with col_rank_chart:
            prod_fig = viz.plot_product_performance(filtered_df, metric=metric_sort, top_n=top_n)
            st.plotly_chart(prod_fig, use_container_width=True)
            
        with col_rank_table:
            st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#475569;'>Performance Details Table</p>", unsafe_allow_html=True)
            prod_metrics = filtered_df.groupby("Product").agg({
                "Sales": "sum",
                "Profit": "sum",
                "Target": "sum",
                "CustomerID": "count"
            }).rename(columns={"CustomerID": "Orders"}).reset_index()
            
            prod_metrics["Margin %"] = (prod_metrics["Profit"] / prod_metrics["Sales"] * 100).round(1)
            prod_metrics["Target Achieved %"] = (prod_metrics["Sales"] / prod_metrics["Target"] * 100).round(1)
            
            display_table = prod_metrics.sort_values(metric_sort, ascending=False).reset_index(drop=True)
            display_table["Sales"] = display_table["Sales"].map(format_currency)
            display_table["Profit"] = display_table["Profit"].map(format_currency)
            display_table["Target"] = display_table["Target"].map(format_currency)
            
            st.dataframe(
                display_table[["Product", "Sales", "Profit", "Margin %", "Target Achieved %", "Orders"]],
                use_container_width=True,
                height=265,
                hide_index=True
            )

    # ==================== TAB 3: GEOGRAPHIC INSIGHTS ====================
    with tab_geography:
        col_map, col_ranking = st.columns([3, 2])
        
        with col_map:
            st.plotly_chart(viz.plot_regional_map(filtered_df), use_container_width=True)
            
        with col_ranking:
            # Segmented selector to choose between visual ranking and key regional cards
            geo_view = st.segmented_control("Geography Insights", ["Regional Ranks", "Quick Metrics"], default="Regional Ranks")
            
            if geo_view == "Regional Ranks":
                st.plotly_chart(viz.plot_regional_ranking(filtered_df), use_container_width=True)
            else:
                reg_agg = filtered_df.groupby("Region").agg({
                    "Sales": "sum",
                    "Profit": "sum",
                    "CustomerID": "nunique"
                }).reset_index()
                reg_agg["Margin %"] = (reg_agg["Profit"] / reg_agg["Sales"] * 100).round(1)
                
                # Render scrollable region cards container to stay compact
                metrics_container_html = "<div style='max-height: 270px; overflow-y: auto; padding-right: 5px;'>"
                for idx, row in reg_agg.sort_values("Sales", ascending=False).iterrows():
                    metrics_container_html += f"""
                    <div style='background-color: #F8FAFC; border-radius: 8px; padding: 10px 14px; border-left: 4px solid #3B82F6; margin-bottom: 8px; font-family: Outfit, sans-serif;'>
                        <div style='display: flex; justify-content: space-between; font-weight: 600; color: #1E293B;'>
                            <span>{row['Region']}</span>
                            <span>{format_currency(row['Sales'])}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; font-size: 0.85rem; color: #64748B; margin-top: 4px;'>
                            <span>Profit: {format_currency(row['Profit'])} ({row['Margin %']}%)</span>
                            <span>Customers: {row['CustomerID']:,}</span>
                        </div>
                    </div>
                    """
                metrics_container_html += "</div>"
                st.markdown(metrics_container_html, unsafe_allow_html=True)

    # ==================== TAB 4: CUSTOMER & PROFITABILITY ====================
    with tab_customers:
        cust_subtab1, cust_subtab2 = st.tabs(["👥 Loyalty & Retention", "⚖️ Margin Trends"])
        
        with cust_subtab1:
            col_funnel, col_heatmap = st.columns([2, 3])
            with col_funnel:
                st.plotly_chart(viz.plot_customer_funnel(filtered_df), use_container_width=True)
            with col_heatmap:
                cohort_fig = viz.plot_cohort_heatmap(filtered_df)
                if cohort_fig is not None:
                    st.plotly_chart(cohort_fig, use_container_width=True)
                else:
                    st.warning("Customer IDs are missing.")
                    
        with cust_subtab2:
            col_margin_chart, col_targets_info = st.columns([3, 2])
            with col_margin_chart:
                st.plotly_chart(viz.plot_margin_breakdown(filtered_df), use_container_width=True)
            with col_targets_info:
                st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#475569; margin-bottom: 10px;'>Target vs Actual Performance</p>", unsafe_allow_html=True)
                
                # Targets comparison summary
                tot_target = filtered_df["Target"].sum() if "Target" in filtered_df.columns else 0
                tot_sales = filtered_df["Sales"].sum()
                tot_profit = filtered_df["Profit"].sum()
                tot_cost = filtered_df["Cost"].sum()
                
                target_gap = tot_sales - tot_target
                target_color = "#10B981" if target_gap >= 0 else "#EF4444"
                target_sign = "+" if target_gap >= 0 else ""
                
                st.markdown(
                    f"""
                    <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; font-family: Outfit, sans-serif;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 12px;'>
                            <span style='color: #64748B;'>Cumulative Sales</span>
                            <span style='font-weight: 600; color: #0F172A;'>{format_currency(tot_sales)}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 12px;'>
                            <span style='color: #64748B;'>Sales Target Goal</span>
                            <span style='font-weight: 600; color: #0F172A;'>{format_currency(tot_target)}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;'>
                            <span style='color: #64748B;'>Goal Variance</span>
                            <span style='font-weight: 700; color: {target_color};'>{target_sign}{format_currency(target_gap)}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                            <span style='color: #64748B;'>Total Cost Expense</span>
                            <span style='font-weight: 600; color: #0F172A;'>{format_currency(tot_cost)}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #64748B;'>Total Net Profit</span>
                            <span style='font-weight: 600; color: #10B981;'>{format_currency(tot_profit)}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ==================== TAB 5: DATA PROFILING MODULE ====================
    with tab_profiler:
        # Profile Data
        cust_col_arg = "CustomerID" if "CustomerID" in filtered_df.columns else None
        profile_results = profile_data(filtered_df, sales_col="Sales", profit_col="Profit", customers_col=cust_col_arg)
        
        # Profile KPI Metrics
        col_prof_1, col_prof_2, col_prof_3, col_prof_4, col_prof_5 = st.columns(5)
        with col_prof_1:
            st.metric("Total Records", f"{profile_results['total_records']:,}")
        with col_prof_2:
            st.metric("Total Columns", f"{profile_results['total_columns']:,}")
        with col_prof_3:
            st.metric("Missing Cells", f"{profile_results['missing_cells']:,} ({profile_results['missing_pct']}%)")
        with col_prof_4:
            st.metric("Duplicate Rows", f"{profile_results['duplicate_rows']:,} ({profile_results['duplicate_pct']}%)")
        with col_prof_5:
            score = profile_results['quality_score']
            color_emoji = "🟢" if score >= 90 else "🟡" if score >= 70 else "🔴"
            st.metric("Data Quality Score", f"{color_emoji} {score}%")
            
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        col_details_table, col_data_preview = st.columns([2, 3])
        with col_details_table:
            st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#475569;'>Column Schema & Metadata</p>", unsafe_allow_html=True)
            st.dataframe(profile_results["type_summary"], use_container_width=True, height=210, hide_index=True)
            
        with col_data_preview:
            st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#475569;'>Raw Transaction Preview</p>", unsafe_allow_html=True)
            st.dataframe(filtered_df.head(100), use_container_width=True, height=170)
            
            # Download Row controls
            d1, d2 = st.columns(2)
            with d1:
                csv_buffer = io.StringIO()
                filtered_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Filtered (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name="filtered_bi_dataset.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with d2:
                if st.session_state["data_source"] == "Demo System Dataset":
                    base_csv = io.StringIO()
                    st.session_state["raw_df"].to_csv(base_csv, index=False)
                    st.download_button(
                        label="📥 Download Sample BI (CSV)",
                        data=base_csv.getvalue(),
                        file_name="sample_bi_dataset.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

