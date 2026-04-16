import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
from stock_analyzer_backend import StockAnalyzer, Portfolio
import plotly.graph_objects as go

st.title("Portfolio Analyzer Tool", text_alignment="center")

num_stocks = st.number_input("How many stocks do you want to analyze?", min_value=1, max_value=10)

for i in range(num_stocks):
    st.text_input("Enter ticker symbol", key=f"ticker_{i}")
    st.text_input("Enter corresponding weight", key=f"weight_{i}")

start_date = st.date_input("What is the date you want to start with?", datetime.date(2026, 3, 6))
end_date = st.date_input("What is the date you want to end with?", datetime.date(2026, 3, 31))

if st.button("Analyze", type="primary"):
    tickers = [st.session_state[f"ticker_{i}"] for i in range(num_stocks)]
    weights_raw = [st.session_state[f"weight_{i}"] for i in range(num_stocks)]

    if any(t == "" for t in tickers) or any(w == "" for w in weights_raw):
        st.error("Please fill in all ticker symbols and weights!")
    else:
        weights = [float(w) for w in weights_raw]

        for ticker in tickers:
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty:
                st.error(f"{ticker} doesn't look right — check the ticker symbol!")
                st.stop()

        with st.spinner("Fetching stock data..."):
            stocks = []
            for i in range(num_stocks):
                stock = StockAnalyzer(tickers[i], str(start_date), str(end_date))
                if stock.data.empty:
                    st.error(f"No trading data found for {tickers[i]} in that date range!")
                    st.stop()
                stock.average_price()
                stocks.append(stock)

            portfolio = Portfolio(stocks, weights)
            portfolio.calculations()

        # Individual stock summaries
        
        for stock in stocks:
            st.markdown(f"## :blue[{stock.ticker_symbol.upper()}]")
            st.divider()
            st.subheader("Individual Stock Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric(label=f"Highest avg price ({stock.max_date.date()})", value=f"${stock.max_avg:.2f}")
            col2.metric(label=f"Lowest avg price ({stock.min_date.date()})", value=f"${stock.min_avg:.2f}")
            col3.metric(label="Volatility (CV)", value=f"{stock.cv:.2f}%")
            col4, col5 = st.columns(2)
            col4.metric(label="Return", value=f"{stock.stock_return:.2f}%")
            col5.metric(label="Max Drawdown", value=f"{stock.max_drawdown:.2f}%")
            st.divider()

        # Portfolio summary
        st.subheader("Portfolio Summary")
        st.write(f"While your picks returned {portfolio.portfolio_return:.2f}%, S&P returned {portfolio.sp_return:.2f}%")

        if portfolio.alpha > 0:
            st.success(f"Congratulations, you beat the S&P 500 by {portfolio.alpha:.2f}%!")
        else:
            st.error(f"Uh oh, the S&P 500 beat you by {abs(portfolio.alpha):.2f}%! Better luck next time!")

        if portfolio.sharpe < 1:
            st.error(f"That's not great, your return came with a lot of risk, Sharpe: {portfolio.sharpe:.2f}")
        elif portfolio.sharpe < 2:
            st.success(f"That's pretty good, moderate risk, Sharpe: {portfolio.sharpe:.2f}")
        else:
            st.success(f"Great job! Minimal risk, Sharpe: {portfolio.sharpe:.2f}!")

        if portfolio.weighted_beta < 1:
            st.success(f"Your picks were less risky than the market, Beta: {portfolio.weighted_beta:.2f}")
        else:
            st.error(f"Your picks were more risky than the market, Beta: {portfolio.weighted_beta:.2f}")

        # Chart
        sp_normalized = (portfolio.sp_data["Close"] / portfolio.sp_data["Close"].iloc[0]) * 100
        sp_normalized.index = sp_normalized.index.tz_localize(None)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sp_normalized.index, y=sp_normalized.values, name="S&P 500"))

        for stock in stocks:
            stock_normalized = (stock.data['Close'] / stock.data['Close'].iloc[0]) * 100
            stock_normalized.index = stock_normalized.index.tz_localize(None)
            fig.add_trace(go.Scatter(x=stock_normalized.index, y=stock_normalized.values, name=stock.ticker_symbol.upper()))

        fig.update_layout(title="Portfolio vs S&P 500", xaxis_title="Date", yaxis_title="Normalized Price (Base 100)")
        st.plotly_chart(fig)
