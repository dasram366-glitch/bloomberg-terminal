# app.py
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini Bloomberg Terminal (with Login)", layout="wide")

# ---- Session initialization ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
# Demo users (stored in-session only)
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234", "mrinmoy": "pass123"}

# ---- Sidebar: Login / Register / Logout ----
with st.sidebar:
    st.header("🔐 Account")
    if st.session_state.logged_in:
        st.success(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()
    else:
        mode = st.selectbox("Choose", ["Login", "Register"])
        if mode == "Login":
            ui_user = st.text_input("Username", key="ui_user")
            ui_pass = st.text_input("Password", type="password", key="ui_pass")
            if st.button("Login"):
                if ui_user in st.session_state.users and st.session_state.users[ui_user] == ui_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = ui_user
                    st.success("✅ Login successful")
                    st.experimental_rerun()
                else:
                    st.error("❌ Invalid username or password")
        else:  # Register
            new_user = st.text_input("New username", key="new_user")
            new_pass = st.text_input("New password", type="password", key="new_pass")
            if st.button("Register"):
                if not new_user or not new_pass:
                    st.error("Enter username and password")
                elif new_user in st.session_state.users:
                    st.error("User already exists")
                else:
                    st.session_state.users[new_user] = new_pass
                    st.success("✅ Registered — now choose Login and sign in")

# If user not logged in, block access to the terminal
if not st.session_state.logged_in:
    st.title("Welcome — please login")
    st.info("Use the sidebar to login or create an account (demo accounts stored only for this session).")
    st.stop()

# ---- Main app: Terminal ----
st.title("📈 Mini Bloomberg Terminal")
st.markdown(f"**User:** {st.session_state.username}")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Watchlist")
    # simple watchlist (session-managed)
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["AAPL", "TSLA", "INFY.NS"]
    ticker_input = st.text_input("Add ticker (e.g. AAPL or INFY.NS)", "")
    if st.button("Add"):
        t = ticker_input.strip().upper()
        if t and t not in st.session_state.watchlist:
            st.session_state.watchlist.append(t)
    # show watchlist
    for t in st.session_state.watchlist:
        if st.button(f"Open {t}", key=f"open_{t}"):
            st.session_state.selected = t
    st.write("---")
    if st.button("Clear watchlist"):
        st.session_state.watchlist = []

with col2:
    # selected ticker (default)
    selected = st.session_state.get("selected", st.session_state.watchlist[0])
    selected = st.selectbox("Selected ticker", st.session_state.watchlist, index=st.session_state.watchlist.index(selected) if selected in st.session_state.watchlist else 0)
    st.session_state.selected = selected

    # Fetch data safely
    st.subheader(f"{selected} — Quote & Chart")
    try:
        ticker = yf.Ticker(selected)
    except Exception as e:
        st.error("Error creating ticker: " + str(e))
        st.stop()

    # Company info
    try:
        info = ticker.info
    except Exception:
        info = {}
    if info:
        st.write("**Company info (partial)**")
        # show selected keys
        keys = ["shortName", "longName", "sector", "industry", "country", "website"]
        small = {k: info.get(k) for k in keys if info.get(k)}
        if small:
            st.json(small)
    else:
        st.info("No company info available.")

    # Price history and chart
    try:
        hist = ticker.history(period="6mo")
        if hist is None or hist.empty:
            st.warning("No price history found for this ticker (it may be delisted or the symbol is invalid). Try a different ticker.")
        else:
            fig, ax = plt.subplots()
            ax.plot(hist.index, hist["Close"], linewidth=1)
            ax.set_ylabel("Price")
            ax.set_title(f"{selected} — Last 6 months")
            st.pyplot(fig)
    except Exception as e:
        st.error("Error fetching history: " + str(e))

    # Latest news (safe get)
    st.subheader("Latest news (if available)")
    try:
        news_list = getattr(ticker, "news", []) or []
        if not news_list:
            st.info("No news found for this ticker.")
        else:
            for n in news_list[:6]:
                title = n.get("title") or n.get("publisher") or "No title"
                link = n.get("link") or n.get("linkHref") or None
                published = n.get("providerPublishTime")
                if link:
                    st.markdown(f"- [{title}]({link})")
                else:
                    st.write(f"- {title}")
    except Exception as e:
        st.info("News not available: " + str(e))

# small footer
st.write("---")
st.caption("Demo login is session-only (no database). For production, connect to a DB or OAuth provider.")
