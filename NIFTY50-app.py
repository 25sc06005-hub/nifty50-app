import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(page_title="NIFTY 50 Dashboard", layout="wide")

st.title('NIFTY 50 Stock App 🇮🇳')

st.markdown("""
This app shows **NIFTY 50 stock prices**
* Data source: Yahoo Finance
""")


# NIFTY 50 symbols
nifty50 = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS", "POWERGRID.NS",
    "NTPC.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "HCLTECH.NS", "TECHM.NS",
    "ONGC.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "INDUSINDBK.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "COALINDIA.NS", "DRREDDY.NS", "CIPLA.NS", "EICHERMOT.NS",
    "GRASIM.NS", "HEROMOTOCO.NS", "HDFCLIFE.NS", "SBILIFE.NS", "BRITANNIA.NS",
    "DIVISLAB.NS", "APOLLOHOSP.NS", "UPL.NS", "BAJAJ-AUTO.NS", "SHREECEM.NS",
    "HINDALCO.NS", "TATACONSUM.NS", "IOC.NS", "M&M.NS", "BPCL.NS"
]






# Sidebar
st.sidebar.header('User Input')

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

selected_stocks = st.sidebar.multiselect(
    'Select NIFTY 50 Stocks',
    nifty50,
    default=nifty50[:5]
)

num_company = st.sidebar.slider('Number of Stocks to Plot', 1, 5)


if not selected_stocks:
    st.warning("Please select at least one stock.")
    st.stop()





# Load data
@st.cache_data
def load_data(stocks, start, end):
    return yf.download(
        tickers=stocks,
        start=start,
        end=end,
        group_by='ticker',
        auto_adjust=True
    )

@st.cache_data
def load_index(start, end):
    return yf.download("^NSEI", start=start, end=end)

data = load_data(selected_stocks, start_date, end_date)
nifty_index = load_index(start_date, end_date)






# Helper
def get_stock_df(stock):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            return data[stock].copy()
        else:
            return data.copy()
    except:
        return pd.DataFrame()


# Returns calculation
returns = {}

for stock in selected_stocks:
    try:
        df = get_stock_df(stock)
        df = df.dropna()

        if len(df) > 1:
            returns[stock] = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
    except:
        pass

# NIFTY return
if not nifty_index.empty:
    close = nifty_index['Close']

    # Fix: ensure it's a Series
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    close = close.dropna()

    if len(close) > 1:
        nifty_return = (close.iloc[-1] / close.iloc[0] - 1) * 100
    else:
        nifty_return = 0
else:
    nifty_return = 0



if returns:
    returns["NIFTY50"] = nifty_return




# KPI
st.metric(
    "NIFTY 50 Return (%)",
    f"{nifty_return:.2f}%",
    delta=f"{nifty_return:.2f}%"
)


# Returns chart
st.subheader("Returns Comparison (%)")
returns_df = pd.DataFrame.from_dict(returns, orient='index', columns=["Return (%)"])
fig = px.bar(
    returns_df,
    x=returns_df.index,
    y="Return (%)",
    color="Return (%)",
    color_continuous_scale="RdYlGn"
)

st.plotly_chart(fig, use_container_width=True)


# Index chart
st.subheader("NIFTY 50 Index")
if not nifty_index.empty:
    
    close = nifty_index['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    st.line_chart(close)

else:
    st.warning("No index data available.")




# Plot function
def price_plot(symbol, chart_type):
    df = get_stock_df(symbol)

    if df.empty:
        st.warning(f"No data for {symbol}")
        return

    df = df.dropna()
    st.subheader(symbol)

    if chart_type == "Candlestick":
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        ))

        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            yaxis='y2',
            opacity=0.3
        ))

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=500,
            template="plotly_dark",
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h")
        )


        # Moving averages
        df['MA50'] = df['Close'].rolling(50, min_periods=1).mean()
        df['MA200'] = df['Close'].rolling(200, min_periods=1).mean()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA50'],
            line=dict(width=1),
            name='MA50'
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['MA200'],
            line=dict(width=1),
            name='MA200'
        ))


        st.plotly_chart(fig, use_container_width=True)

    else:
        st.line_chart(df['Close'])



chart_type = st.sidebar.radio("Chart Type", ["Line", "Candlestick"])




# Show plots button

st.info("Charts update automatically based on your selection")

for stock in selected_stocks[:num_company]:
    price_plot(stock, chart_type)


            
# Raw data
if st.checkbox("Show Raw Data"):
    st.dataframe(data.tail())