import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini Bloomberg Terminal", layout="wide")

st.title("📈 Mini Bloomberg Terminal")

# Sidebar input
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL")

# Get stock data
data = yf.Ticker(ticker)
hist = data.history(period="6mo")

# Company Info
st.subheader(f"Company Information: {ticker}")
try:
    st.write(data.info)
except Exception as e:
    st.error("Could not fetch company info.")

# Price Chart
st.subheader(f"{ticker} Price Chart (6 Months)")
fig, ax = plt.subplots()
ax.plot(hist.index, hist["Close"], label="Closing Price")
ax.legend()
st.pyplot(fig)

# News (if available)
if hasattr(data, "news") and data.news:
    st.subheader("Latest News")
    for n in data.news[:5]:
        st.write(f"- [{n['title']}]({n['link']})")
