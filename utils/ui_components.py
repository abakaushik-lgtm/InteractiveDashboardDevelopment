import streamlit as st

def load_css(file_path):
    """
    Loads custom CSS stylesheet into the Streamlit app.
    """
    try:
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def render_kpi_card(title, value, delta=None, is_delta_positive=True, card_type="default", icon="💰", caption="vs target"):
    """
    Generates HTML string for a premium dashboard KPI card.
    
    Parameters:
    - title (str): The metric label.
    - value (str): The main value to show (e.g. $5.2M).
    - delta (str/float/int): The change value (e.g. 18.4% or 12.3k).
    - is_delta_positive (bool): True for up trend (green), False for down trend (red).
    - card_type (str): Accent class ('profit', 'growth', 'customers', 'aov', or 'default').
    - icon (str): Emoji or icon to display in the top right.
    - caption (str): Label next to the delta value.
    """
    delta_html = ""
    if delta is not None:
        delta_class = "kpi-delta-up" if is_delta_positive else "kpi-delta-down"
        arrow = "▲" if is_delta_positive else "▼"
        prefix = "+" if (is_delta_positive and "%" in str(delta) or isinstance(delta, (int, float)) and delta > 0) else ""
        delta_html = f"""
        <div class="kpi-footer">
            <span class="{delta_class}">{arrow} {prefix}{delta}</span>
            <span class="kpi-caption">{caption}</span>
        </div>
        """
    else:
        delta_html = f"""
        <div class="kpi-footer">
            <span class="kpi-caption">Active Period</span>
        </div>
        """
        
    card_html = f"""
    <div class="kpi-card {card_type}">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    return card_html

def render_kpi_grid(cards_data):
    """
    Renders multiple KPI cards side-by-side using Streamlit columns.
    cards_data should be a list of dicts matching render_kpi_card arguments.
    """
    cols = st.columns(len(cards_data))
    for col, card in zip(cols, cards_data):
        with col:
            st.markdown(
                render_kpi_card(
                    title=card.get("title", ""),
                    value=card.get("value", ""),
                    delta=card.get("delta"),
                    is_delta_positive=card.get("is_delta_positive", True),
                    card_type=card.get("card_type", "default"),
                    icon=card.get("icon", "💰"),
                    caption=card.get("caption", "vs target")
                ),
                unsafe_allow_html=True
            )

def render_header(title, subtitle):
    """
    Renders a premium title and description block.
    """
    st.markdown(f'<h1 class="main-title">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{subtitle}</p>', unsafe_allow_html=True)
