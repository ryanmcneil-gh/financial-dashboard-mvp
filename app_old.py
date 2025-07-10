import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Configure Streamlit page settings
st.set_page_config(
    page_title="Financial Dashboard MVP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("📊 Financial Dashboard MVP")

# Sidebar setup
st.sidebar.header("Dashboard Controls")

# Timeframe selector
timeframe_options = ["1M", "3M", "6M", "1Y", "2Y"]
selected_timeframe = st.sidebar.selectbox(
    "Select Timeframe:",
    options=timeframe_options,
    index=1,  # Default to 3M
    help="Choose the time period for data analysis"
)

# Manual refresh button
if st.sidebar.button("🔄 Manual Refresh", help="Click to refresh all data"):
    st.cache_data.clear()
    # Removed rerun() - cache clear is sufficient for MVP

# Add timezone info
st.sidebar.info("🕐 All times displayed in EDT (Eastern Daylight Time)")

# Placeholder for collapsible sections template
with st.expander("ℹ️ About This Dashboard"):
    st.write("""
    This Financial Dashboard provides real-time market data and analysis across multiple asset classes:
    
    - **Market Overview**: Broad asset class performance
    - **Equity Indices**: US major stock indices
    - **Currency Markets**: Major USD currency pairs
    - **Commodities**: Energy and precious metals
    - **Fixed Income**: Treasury yield analysis
    - **Volatility**: Market volatility indicators
    - **Correlation**: Asset correlation analysis
    - **Volume**: Unusual volume detection
    
    Data is sourced from Yahoo Finance and updated in real-time.
    """)

# yfinance connectivity test function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_historical_data(ticker, period_string):
    """
    Fetch historical data for a given ticker
    
    Args:
        ticker (str): Stock ticker symbol (e.g., '^GSPC', 'AAPL')
        period_string (str): Streamlit timeframe ('1M', '3M', '6M', '1Y', '2Y')
        
    Returns:
        pd.DataFrame: Historical price data or empty DataFrame on error
    """
    try:
        # Map Streamlit timeframe to yfinance format
        timeframe_mapping = {
            "1M": "1mo",
            "3M": "3mo", 
            "6M": "6mo",
            "1Y": "1y",
            "2Y": "2y"
        }
        
        yf_period = timeframe_mapping.get(period_string, "3mo")
        
        # Download data using period directly
        data = yf.download(ticker, period=yf_period, progress=False)
        
        if data.empty:
            st.warning(f"No data found for ticker: {ticker}")
            return pd.DataFrame()
            
        # Reset index to make Date a column
        data = data.reset_index()
        
        return data
        
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()
    
# Test yfinance connectivity
st.header("🔍 Data Connectivity Test")

with st.expander("yfinance Connection Test - S&P 500 (^GSPC)", expanded=True):
    st.write("Testing connection to Yahoo Finance API...")
    
    # Fetch sample data using the new function with selected timeframe
    sample_data = get_historical_data("^GSPC", selected_timeframe)
    
    if not sample_data.empty:
        st.success("✅ Successfully connected to Yahoo Finance!")
        
        # Display basic info about the data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Data Points", len(sample_data))
        
        with col2:
            st.metric("📅 Start Date", sample_data['Date'].min().strftime('%Y-%m-%d'))
        
        with col3:
            st.metric("📅 End Date", sample_data['Date'].max().strftime('%Y-%m-%d'))
        
        # Display sample data
        st.subheader("Sample Data (First 10 rows)")
        st.dataframe(
            sample_data.head(10),
            use_container_width=True,
            hide_index=True
        )
        
        # Simple price chart
        st.subheader("Sample Price Chart")

        # Debug: Show data info
        st.write(f"Data shape: {sample_data.shape}")
        st.write("Column names:")
        st.write(list(sample_data.columns))
        st.write("First few rows:")
        st.write(sample_data.head())

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_data['Date'],
            y=sample_data['Close'],
            mode='lines+markers',  # Added markers to see data points
            name='S&P 500 Close Price',
            line=dict(color='#1f77b4', width=2)
        ))

        fig.update_layout(
            title=f"S&P 500 - {selected_timeframe} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("❌ Failed to connect to Yahoo Finance. Please check your internet connection.")

# Placeholder sections for future phases
st.header("📋 Dashboard Sections")

# Market Overview - Broad Asset Class Performance (Updated)
st.header("🌍 Market Overview")

with st.expander("📈 Broad Asset Class Performance", expanded=True):
    st.subheader("Normalized Performance Comparison")
    st.write("Comparing major asset classes normalized to 100 at start of period")
    
    # Define asset tickers and names
    overview_assets = {
        "^GSPC": "S&P 500",
        "DXY": "US Dollar Index", 
        "GLD": "Gold ETF",
        "USO": "Oil ETF",
        "TLT": "20+ Year Treasury"
    }
    
    # Fetch data for all assets
    asset_data = {}
    for ticker, name in overview_assets.items():
        data = get_historical_data(ticker, selected_timeframe)
        if not data.empty:
            asset_data[name] = data
    
    if asset_data:
        # Create normalized performance chart
        fig = go.Figure()
        
        for asset_name, data in asset_data.items():
            if 'Close' in data.columns and len(data) > 0:
                # Normalize to 100 at start
                normalized_prices = (data['Close'] / data['Close'].iloc[0]) * 100
                
                fig.add_trace(go.Scatter(
                    x=data['Date'],
                    y=normalized_prices,
                    mode='lines',
                    name=asset_name,
                    hovertemplate=f'<b>{asset_name}</b><br>' +
                                  'Date: %{x}<br>' +
                                  'Normalized: %{y:.1f}<br>' +
                                  '<extra></extra>'
                ))
        
        fig.update_layout(
            title=f"Asset Class Performance - {selected_timeframe}",
            xaxis_title="Date",
            yaxis_title="Normalized Price (Start = 100)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show current performance summary
        st.subheader("Current Performance Summary")
        perf_data = []
        for asset_name, data in asset_data.items():
            if 'Close' in data.columns and len(data) > 1:
                start_price = data['Close'].iloc[0]
                end_price = data['Close'].iloc[-1]
                performance = ((end_price - start_price) / start_price) * 100
                perf_data.append({
                    "Asset": asset_name,
                    "Performance": f"{performance:+.1f}%"
                })
        
        if perf_data:
            perf_df = pd.DataFrame(perf_data)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
    else:
        st.error("Unable to fetch data for market overview assets")

# Equity Indices placeholder
with st.expander("🇺🇸 US Major Indices", expanded=False):
    st.info("📊 US equity indices analysis coming in Phase 2...")
    st.write("Will include: S&P 500, NASDAQ, Dow Jones, Russell 2000")

# Currency Markets placeholder
with st.expander("💱 Major USD Currency Pairs", expanded=False):
    st.info("💰 Currency market analysis coming in Phase 2...")
    st.write("Will include: EUR/USD, GBP/USD, USD/JPY, USD/CHF, USD/CAD, AUD/USD")

# Commodities placeholder
with st.expander("🛢️ Energy Complex", expanded=False):
    st.info("⚡ Energy commodities analysis coming in Phase 2...")
    st.write("Will include: Crude Oil, Natural Gas, Gasoline")

with st.expander("🥇 Precious Metals", expanded=False):
    st.info("✨ Precious metals analysis coming in Phase 2...")
    st.write("Will include: Gold, Silver, Platinum")

# Advanced features placeholders
with st.expander("📈 Treasury Yield Curve", expanded=False):
    st.info("🏦 Fixed income analysis coming in Phase 3...")
    st.write("Will include: 3M, 5Y, 10Y, 30Y Treasury yields")

with st.expander("📊 Volatility Analysis", expanded=False):
    st.info("📉 Volatility indicators coming in Phase 3...")
    st.write("Will include: VIX, VXN, RVX")

with st.expander("🔄 Rolling Correlation Matrix", expanded=False):
    st.info("🔗 Correlation analysis coming in Phase 3...")
    st.write("Will include: 30-day rolling correlations between major assets")

with st.expander("📢 Unusual Volume Detection", expanded=False):
    st.info("🔍 Volume analysis coming in Phase 3...")
    st.write("Will include: Volume spike detection and alerts")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Financial Dashboard MVP - Phase 1 Complete</p>
        <p>Data provided by Yahoo Finance via yfinance library</p>
        <p>Built with Streamlit & Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Development notes (will be removed in production)
if st.sidebar.checkbox("🔧 Show Development Notes"):
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Phase 1 Status: ✅ Complete**")
    st.sidebar.markdown("**Next: Phase 2 - Core Asset Classes**")
    st.sidebar.markdown("**Selected Timeframe:**")
    st.sidebar.code(f"Current: {selected_timeframe}")
    
    # Display current timeframe mapping for development
    timeframe_mapping = {
        "1M": "1mo",
        "3M": "3mo", 
        "6M": "6mo",
        "1Y": "1y",
        "2Y": "2y"
    }
    st.sidebar.markdown("**yfinance Mapping:**")
    st.sidebar.code(f"yfinance period: {timeframe_mapping[selected_timeframe]}")