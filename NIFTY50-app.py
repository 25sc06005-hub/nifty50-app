import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="NIFTY 50 Dashboard", layout="wide")

st.title('NIFTY 50 Stock Dashboard 🇮🇳')

st.markdown("""
Interactive dashboard for **NIFTY 50 stocks**  
Data source: Yahoo Finance
""")




# -------------------------------
# NIFTY 50 symbols
# -------------------------------
nifty50 = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
    "TITAN.NS","ULTRACEMCO.NS","NESTLEIND.NS","WIPRO.NS","POWERGRID.NS",
    "NTPC.NS","BAJFINANCE.NS","BAJAJFINSV.NS","HCLTECH.NS","TECHM.NS",
    "ONGC.NS","JSWSTEEL.NS","TATASTEEL.NS","INDUSINDBK.NS","ADANIENT.NS",
    "ADANIPORTS.NS","COALINDIA.NS","DRREDDY.NS","CIPLA.NS","EICHERMOT.NS",
    "GRASIM.NS","HEROMOTOCO.NS","HDFCLIFE.NS","SBILIFE.NS","BRITANNIA.NS",
    "DIVISLAB.NS","APOLLOHOSP.NS","UPL.NS","BAJAJ-AUTO.NS","SHREECEM.NS",
    "HINDALCO.NS","TATACONSUM.NS","IOC.NS","M&M.NS","BPCL.NS"
]





# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.header('User Input')

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

selected_stocks = st.sidebar.multiselect(
    'Stocks for Analysis',
    nifty50,
    default=nifty50[:5]
)

portfolio_stocks = st.sidebar.multiselect(
    "Portfolio Stocks",
    nifty50
)

num_company = st.sidebar.slider('Number of Charts', 1, 5)
chart_type = st.sidebar.radio("Chart Type", ["Line", "Candlestick"])

if not selected_stocks:
    st.warning("Select at least one stock.")
    st.stop()




# -------------------------------
# Load data (FIXED)
# -------------------------------
all_stocks = list(set(selected_stocks + portfolio_stocks))

@st.cache_data
def load_data(stocks, start, end):
    return yf.download(stocks, start=start, end=end, group_by='ticker', auto_adjust=True)

@st.cache_data
def load_index(start, end):
    return yf.download("^NSEI", start=start, end=end)

data = load_data(all_stocks, start_date, end_date)
nifty_index = load_index(start_date, end_date)



# -------------------------------
# Helper
# -------------------------------
def get_stock_df(stock):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            return data[stock].copy()
        return data.copy()
    except:
        return pd.DataFrame()



# -------------------------------
# RSI
# -------------------------------
def compute_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = -delta.clip(upper=0).rolling(window).mean()
    rs = gain / loss
    return (100 - (100 / (1 + rs))).fillna(0)



# -------------------------------
# RETURNS
# -------------------------------
returns = {}

for stock in selected_stocks:
    try:
        df = get_stock_df(stock)

        if df.empty or 'Close' not in df.columns:
            continue

        close = df['Close'].dropna()

        if len(close) > 1:
            returns[stock] = ((close.iloc[-1] / close.iloc[0]) - 1) * 100

    except Exception as e:
        continue



# NIFTY return
if not nifty_index.empty:
    close = nifty_index['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    close = close.dropna()
    nifty_return = (close.iloc[-1] / close.iloc[0] - 1) * 100 if len(close) > 1 else 0
else:
    nifty_return = 0

returns["NIFTY50"] = nifty_return
returns_df = pd.DataFrame.from_dict(returns, orient='index', columns=["Return (%)"])



# -------------------------------
# KPIs
# -------------------------------
col1, col2 = st.columns(2)

col1.metric("NIFTY 50 Return", f"{nifty_return:.2f}%")

if not returns_df.empty:
    best_stock = returns_df["Return (%)"].idxmax()
    best_value = returns_df["Return (%)"].max()
    col2.metric("Best Performer", best_stock, f"{best_value:.2f}%")




# -------------------------------
# RETURNS CHART
# -------------------------------
st.subheader("Returns Comparison")

if returns_df.empty:
    st.warning("No return data available.")
else:
    # If only one stock → avoid color scale bug
    if len(returns_df) == 1:
        fig = px.bar(
            returns_df,
            x=returns_df.index,
            y="Return (%)"
        )
    else:
        fig = px.bar(
            returns_df,
            x=returns_df.index,
            y="Return (%)",
            color="Return (%)",
            color_continuous_scale="RdYlGn"
        )

    st.plotly_chart(fig, use_container_width=True)




# -------------------------------
# INDEX
# -------------------------------
st.subheader("NIFTY 50 Index")

if not nifty_index.empty:
    close = nifty_index['Close']
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    st.line_chart(close)





# -------------------------------
# CHART FUNCTION
# -------------------------------
def price_plot(symbol):
    df = get_stock_df(symbol).dropna()
    if df.empty:
        return

    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()

    df['Signal'] = 0
    df.loc[df['MA50'] > df['MA200'], 'Signal'] = 1
    df.loc[df['MA50'] < df['MA200'], 'Signal'] = -1
    df['Position'] = df['Signal'].diff()

    st.subheader(symbol)

    if chart_type == "Candlestick":
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        ))

        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50'))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200'))

        buy = df[df['Position'] == 2]
        sell = df[df['Position'] == -2]

        fig.add_trace(go.Scatter(x=buy.index, y=buy['Close'], mode='markers', name='BUY'))
        fig.add_trace(go.Scatter(x=sell.index, y=sell['Close'], mode='markers', name='SELL'))

        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.line_chart(df[['Close', 'MA50', 'MA200']])

    # RSI
    st.markdown("**RSI**")
    df['RSI'] = compute_rsi(df)
    st.line_chart(df['RSI'])




# -------------------------------
# DISPLAY CHARTS
# -------------------------------
st.info("Charts update automatically")

for stock in selected_stocks[:num_company]:
    price_plot(stock)




# -------------------------------
# PORTFOLIO
# -------------------------------
st.header("📊 Portfolio Tracker")

portfolio = []

for stock in portfolio_stocks:
    qty = st.number_input(f"{stock} Quantity", 0, key=f"q_{stock}")
    price = st.number_input(f"{stock} Buy Price", 0.0, key=f"p_{stock}")

    if qty > 0 and price > 0:
        df = get_stock_df(stock)
        if not df.empty:
            current = df['Close'].dropna().iloc[-1]

            invested = qty * price
            value = qty * current

            portfolio.append({
                "Stock": stock,
                "Invested": invested,
                "Value": value,
                "Return %": ((value - invested) / invested) * 100
            })




if portfolio:
    dfp = pd.DataFrame(portfolio)
    st.dataframe(dfp)

    total_inv = dfp["Invested"].sum()
    total_val = dfp["Value"].sum()
    total_ret = (total_val - total_inv) / total_inv * 100

    st.metric("Portfolio Return", f"{total_ret:.2f}%")

    st.metric("NIFTY Return", f"{nifty_return:.2f}%")


# -------------------------------
# DOWNLOAD
# -------------------------------
st.download_button(
    "Download Data",
    data.to_csv().encode(),
    "nifty_data.csv"
)