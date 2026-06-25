import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Premium color palette definitions
PRIMARY_COLOR = "#3B82F6"   # Electric Blue
SECONDARY_COLOR = "#10B981" # Emerald Green
ACCENT_COLOR = "#8B5CF6"    # Royal Purple
WARNING_COLOR = "#F59E0B"   # Warm Amber
DANGER_COLOR = "#EF4444"    # Coral Red
BG_COLOR = "#F8FAFC"
GRID_COLOR = "#E2E8F0"

def apply_chart_theme(fig, height=310):
    """
    Applies unified high-end styling to a Plotly figure.
    """
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Outfit, sans-serif", size=12),
        margin=dict(l=40, r=40, t=45, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        linecolor=GRID_COLOR,
        tickfont=dict(color="#64748B"),
        title_font=dict(color="#475569")
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID_COLOR,
        linecolor=GRID_COLOR,
        tickfont=dict(color="#64748B"),
        title_font=dict(color="#475569")
    )
    return fig

def plot_revenue_trend(df, frequency="Month"):
    """
    Plots an interactive line/area chart showing Sales and Profit trends.
    """
    # Resample based on selection
    if frequency == "Day":
        df_trend = df.groupby("Date").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
        x_col = "Date"
    elif frequency == "Month":
        df_trend = df.copy()
        df_trend["Month"] = df_trend["Date"].dt.to_period("M").astype(str)
        df_trend = df_trend.groupby("Month").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
        x_col = "Month"
    else:  # Year
        df_trend = df.copy()
        df_trend["Year"] = df_trend["Date"].dt.year.astype(str)
        df_trend = df_trend.groupby("Year").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
        x_col = "Year"
        
    fig = go.Figure()
    
    # Sales Area
    fig.add_trace(go.Scatter(
        x=df_trend[x_col],
        y=df_trend["Sales"],
        name="Sales (Revenue)",
        mode="lines+markers",
        line=dict(width=3, color=PRIMARY_COLOR),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.1)",
        hovertemplate="Period: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    # Profit Area
    fig.add_trace(go.Scatter(
        x=df_trend[x_col],
        y=df_trend["Profit"],
        name="Profit",
        mode="lines+markers",
        line=dict(width=3, color=SECONDARY_COLOR),
        fill="tozeroy",
        fillcolor="rgba(16, 185, 129, 0.08)",
        hovertemplate="Period: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
    ))
    
    # Rolling average overlay for monthly trends
    if frequency == "Month" and len(df_trend) >= 3:
        df_trend["Sales_MA"] = df_trend["Sales"].rolling(window=3, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df_trend[x_col],
            y=df_trend["Sales_MA"],
            name="Sales (3-Mo Rolling Avg)",
            mode="lines",
            line=dict(dash="dash", color=ACCENT_COLOR, width=2),
            hovertemplate="3-Mo Avg Sales: $%{y:,.2f}<extra></extra>"
        ))
        
    fig.update_layout(
        title="Revenue & Profit Growth Trend Analysis",
        xaxis_title=frequency,
        yaxis_title="Amount ($)",
        hovermode="x unified"
    )
    
    return apply_chart_theme(fig)

def plot_product_performance(df, metric="Sales", top_n=10):
    """
    Plots a horizontal bar chart displaying top product performers.
    """
    df_product = df.groupby("Product").agg({
        "Sales": "sum",
        "Profit": "sum",
        "Target": "sum"
    }).reset_index()
    
    df_sorted = df_product.sort_values(metric, ascending=True).tail(top_n)
    
    fig = go.Figure()
    
    # Main metric bar
    bar_color = PRIMARY_COLOR if metric == "Sales" else SECONDARY_COLOR
    fig.add_trace(go.Bar(
        y=df_sorted["Product"],
        x=df_sorted[metric],
        orientation="h",
        name=f"Actual {metric}",
        marker=dict(color=bar_color, line=dict(color="rgba(255, 255, 255, 0.5)", width=1)),
        hovertemplate="Product: %{y}<br>Value: $%{x:,.2f}<extra></extra>"
    ))
    
    # Target overlay marker (vertical ticks)
    if metric == "Sales":
        fig.add_trace(go.Scatter(
            y=df_sorted["Product"],
            x=df_sorted["Target"],
            mode="markers",
            name="KPI Target",
            marker=dict(symbol="line-ns-open", size=14, line=dict(width=3, color=DANGER_COLOR)),
            hovertemplate="KPI Target: $%{x:,.2f}<extra></extra>"
        ))
        
    fig.update_layout(
        title=f"Top {top_n} Products by {metric}",
        xaxis_title=f"{metric} ($)",
        yaxis_title="Product Name",
        barmode="overlay",
        legend=dict(x=1, y=0, xanchor="right", yanchor="bottom")
    )
    
    return apply_chart_theme(fig)

def plot_category_distribution(df):
    """
    Plots a doughnut chart showing category-wise revenue distribution.
    """
    df_cat = df.groupby("Category").agg({"Sales": "sum"}).reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=df_cat["Category"],
        values=df_cat["Sales"],
        hole=0.55,
        marker=dict(colors=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR]),
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        hovertemplate="Category: %{label}<br>Sales: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title="Revenue Contribution by Product Category",
        annotations=[dict(text="Sales Share", x=0.5, y=0.5, font_size=16, font_family="Outfit", showarrow=False)]
    )
    
    return apply_chart_theme(fig)

def plot_category_profitability(df):
    """
    Plots a grouped bar chart of Sales vs Cost vs Profit by Category.
    """
    df_cat = df.groupby("Category").agg({
        "Sales": "sum",
        "Cost": "sum",
        "Profit": "sum"
    }).reset_index().sort_values("Sales", ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_cat["Category"],
        y=df_cat["Sales"],
        name="Sales",
        marker_color=PRIMARY_COLOR,
        hovertemplate="Category: %{x}<br>Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=df_cat["Category"],
        y=df_cat["Cost"],
        name="Cost",
        marker_color=WARNING_COLOR,
        hovertemplate="Category: %{x}<br>Cost: $%{y:,.2f}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=df_cat["Category"],
        y=df_cat["Profit"],
        name="Profit",
        marker_color=SECONDARY_COLOR,
        hovertemplate="Category: %{x}<br>Profit: $%{y:,.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Financial Breakdown by Product Category",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        barmode="group"
    )
    
    return apply_chart_theme(fig)

def plot_regional_map(df):
    """
    Plots a map visualization representing sales by geography.
    Maps general regions to representative country polygons.
    """
    mapping = {
        "North America": {"code": "USA", "name": "United States"},
        "Europe": {"code": "FRA", "name": "France"},
        "Asia-Pacific": {"code": "AUS", "name": "Australia"},
        "Latin America": {"code": "BRA", "name": "Brazil"}
    }
    
    df_reg = df.groupby("Region").agg({"Sales": "sum", "Profit": "sum", "CustomerID": "nunique"}).reset_index()
    df_reg["Code"] = df_reg["Region"].map(lambda r: mapping.get(r, {}).get("code", ""))
    df_reg["Country"] = df_reg["Region"].map(lambda r: mapping.get(r, {}).get("name", ""))
    
    fig = px.choropleth(
        df_reg,
        locations="Code",
        color="Sales",
        hover_name="Region",
        hover_data={"Code": False, "Country": True, "Sales": ":$,.2f", "Profit": ":$,.2f", "CustomerID": True},
        color_continuous_scale=[[0, "#EFF6FF"], [0.2, "#BFDBFE"], [0.5, "#60A5FA"], [1, "#1D4ED8"]],
        title="Global Sales Distribution Map"
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
            landcolor="#F1F5F9",
            coastlinecolor="#CBD5E1"
        ),
        coloraxis_colorbar=dict(title="Sales ($)"),
        margin=dict(l=0, r=0, t=35, b=0),
        height=310
    )
    
    return fig

def plot_regional_ranking(df):
    """
    Plots a horizontal bar chart of Regional Performance.
    """
    df_reg = df.groupby("Region").agg({
        "Sales": "sum",
        "Profit": "sum",
        "CustomerID": "nunique"
    }).reset_index().sort_values("Sales", ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_reg["Region"],
        x=df_reg["Sales"],
        orientation="h",
        name="Sales",
        marker_color=PRIMARY_COLOR,
        hovertemplate="Region: %{y}<br>Sales: $%{x:,.2f}<extra></extra>"
    ))
    
    # Secondary line axis for profit margins
    margin_pct = (df_reg["Profit"] / df_reg["Sales"]) * 100
    
    fig.add_trace(go.Scatter(
        y=df_reg["Region"],
        x=df_reg["Profit"],
        mode="markers+text",
        name="Profit",
        text=[f"${v/1000:,.0f}k" for v in df_reg["Profit"]],
        textposition="middle right",
        marker=dict(color=SECONDARY_COLOR, size=10, symbol="diamond"),
        hovertemplate="Region: %{y}<br>Profit: $%{x:,.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Sales and Profit Rankings by Geography",
        xaxis_title="Amount ($)",
        yaxis_title="Region"
    )
    
    return apply_chart_theme(fig)

def plot_customer_funnel(df):
    """
    Generates a funnel chart tracing customer segments or purchase depth.
    All Customers -> Repeat Customers -> Engaged Customers -> Super Buyers.
    """
    if "CustomerID" not in df.columns:
        # Fallback to segments
        df_seg = df.groupby("Segment").agg({"CustomerID": "nunique"}).reset_index().sort_values("CustomerID", ascending=False)
        fig = go.Figure(go.Funnel(
            y=df_seg["Segment"],
            x=df_seg["CustomerID"],
            textinfo="value+percent initial",
            marker=dict(color=[PRIMARY_COLOR, ACCENT_COLOR, WARNING_COLOR])
        ))
        fig.update_layout(title="Customer Count by Segment Funnel")
        return apply_chart_theme(fig)
        
    # Analyze loyalty depth
    counts = df.groupby("CustomerID").size()
    
    stage1 = len(counts) # All Customers
    stage2 = (counts >= 2).sum() # Repeat (2+ purchases)
    stage3 = (counts >= 4).sum() # Engaged (4+ purchases)
    stage4 = (counts >= 6).sum() # Super Buyers (6+ purchases)
    
    stages = ["All Customers", "Repeat (2+ Orders)", "Engaged (4+ Orders)", "Loyals (6+ Orders)"]
    values = [stage1, stage2, stage3, stage4]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=[PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR]),
        connector=dict(fillcolor="rgba(148, 163, 184, 0.2)")
    ))
    
    fig.update_layout(
        title="Customer Loyalty Funnel (Purchase Frequency)",
        yaxis_title="Loyalty Stage"
    )
    
    return apply_chart_theme(fig)

def plot_cohort_heatmap(df):
    """
    Generates a monthly customer retention cohort heatmap.
    """
    if "CustomerID" not in df.columns or "Date" not in df.columns:
        return None
        
    df_cohort = df.copy()
    
    # 1. Order Month
    df_cohort["OrderMonth"] = df_cohort["Date"].dt.to_period("M")
    
    # 2. First Order Month (Cohort Month) per customer
    df_cohort["CohortMonth"] = df_cohort.groupby("CustomerID")["Date"].transform("min").dt.to_period("M")
    
    # 3. Aggregate unique customers per cohort month & order month
    cohort_group = df_cohort.groupby(["CohortMonth", "OrderMonth"]).agg(n_customers=("CustomerID", "nunique")).reset_index()
    
    # 4. Calculate period index (months elapsed)
    cohort_group["PeriodIndex"] = (cohort_group["OrderMonth"] - cohort_group["CohortMonth"]).apply(lambda attr: attr.n)
    
    # 5. Pivot
    cohort_pivot = cohort_group.pivot(index="CohortMonth", columns="PeriodIndex", values="n_customers")
    
    # 6. Convert to percentage
    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    # Fill missing columns and round
    retention_matrix = retention_matrix.round(1)
    
    # Format index and columns for plotting
    y_labels = [str(x) for x in retention_matrix.index]
    x_labels = [f"M+{col}" if col > 0 else "Acq" for col in retention_matrix.columns]
    
    # Mask NaN for hover/annotation
    annot_text = []
    for r in range(len(retention_matrix)):
        row_text = []
        for c in range(len(retention_matrix.columns)):
            val = retention_matrix.iloc[r, c]
            if pd.isna(val):
                row_text.append("")
            else:
                row_text.append(f"{val:.0f}%" if c > 0 else f"{cohort_size.iloc[r]:,.0f}")
        annot_text.append(row_text)
        
    fig = go.Figure(data=go.Heatmap(
        z=retention_matrix.values,
        x=x_labels,
        y=y_labels,
        colorscale="Blues",
        zmin=0,
        zmax=100,
        text=annot_text,
        texttemplate="%{text}",
        textfont={"size": 10, "family": "Outfit"},
        hovertemplate="Cohort: %{y}<br>Month: %{x}<br>Retention: %{z:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title="Monthly Customer Retention Cohorts (%)",
        xaxis_title="Months Since Acquisition",
        yaxis_title="Cohort Month",
        yaxis=dict(autorange="reversed")
    )
    
    return apply_chart_theme(fig)

def plot_margin_breakdown(df):
    """
    Plots profit margin trends and breakdown.
    """
    df_margin = df.copy()
    df_margin["Month"] = df_margin["Date"].dt.to_period("M").astype(str)
    
    df_grp = df_margin.groupby("Month").agg({
        "Sales": "sum",
        "Profit": "sum",
        "Cost": "sum"
    }).reset_index()
    
    df_grp["MarginPct"] = (df_grp["Profit"] / df_grp["Sales"]) * 100
    
    fig = go.Figure()
    
    # Area chart of revenue
    fig.add_trace(go.Bar(
        x=df_grp["Month"],
        y=df_grp["Sales"],
        name="Total Sales",
        marker_color="rgba(59, 130, 246, 0.4)",
        hovertemplate="Sales: $%{y:,.2f}<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        x=df_grp["Month"],
        y=df_grp["Profit"],
        name="Total Profit",
        marker_color="rgba(16, 185, 129, 0.6)",
        hovertemplate="Profit: $%{y:,.2f}<extra></extra>"
    ))
    
    # Secondary line for Margin %
    fig.add_trace(go.Scatter(
        x=df_grp["Month"],
        y=df_grp["MarginPct"] * (df_grp["Sales"].max() / 100), # Scale to fit on primary axis
        name="Profit Margin %",
        mode="lines+markers",
        line=dict(color=ACCENT_COLOR, width=3),
        hovertemplate="Margin: %{customdata:.1f}%<extra></extra>",
        customdata=df_grp["MarginPct"]
    ))
    
    # Custom yaxis representing the margin scale on the right
    fig.update_layout(
        title="Sales vs Profit Margin % Trend",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        barmode="overlay",
        hovermode="x unified"
    )
    
    return apply_chart_theme(fig)
