import pandas as pd
import numpy as np
import streamlit as st
import requests 
import yfinance as yf

import plotly.express as px
import plotly.graph_objects as go



st.sidebar.title("Options")
option = st.sidebar.selectbox("Which Dashboard?", ("Chart", "Ishares Etf Position Explorer", "Symbol", "ARK Invest Portfolio", "Total Portfolio Holding Calculator"), 0)


#st.title(option)

if option == "Chart":
    symbol = st.sidebar.text_input(label="Symbol:", value="ASML",)
    years = st.sidebar.slider("Years:", 1, 6, value=3)
    
    @st.cache
    def get_ticker_data(symbol, period=f"{years}y"):
        ticker = yf.Ticker(symbol)
        infos = ticker.info
        hist_data = ticker.history(period)
        
        return ticker, infos, hist_data
    
    #data_load_state = st.text("Loading data...")
    ticker, infos, hist_data = get_ticker_data(symbol)
    #data_load_state.text("Data loaded.")
 
    st.image(infos["logo_url"])
    st.header(infos["longName"]) 
    st.subheader("Basic Info:")
    
    f"""
    **Country:** {infos["country"]}
    
    **Sector:** {infos["industry"]}
    
    **Dividend:** {infos["dividendRate"]} %
    
    **Website:** {infos["website"]}
    
    ---
    """
    
    
    @st.cache
    def plot_data():     
        fig = go.Figure(data=[
                              go.Candlestick(x=hist_data.index.date.tolist(),
                                             open=hist_data["Open"],
                                             high=hist_data["High"],
                                             low=hist_data["Low"],
                                             close=hist_data["Close"],
                                             name=symbol)
                             ]
                       )


        fig.update_xaxes(type='category')
        fig.update_layout(height=800, width=1000)
        return fig
    
    try:
        fig = plot_data()
        st.plotly_chart(fig, use_container_width=True)
        st.write(hist_data)
    except:
        st.write("No Plot Data available right now...")

    

if option == "Symbol":
    symbol = st.sidebar.text_input(label="Symbol:", value="ASML",)
   
    st.subheader(f'Chart:')
    #@st.cache
    st.image(f'https://finviz.com/chart.ashx?t={symbol}')
    
    st.markdown("---")
    st.header(f'Stocktwits for {symbol}:')
    stocktwits_symbol_url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json".format(symbol)
    
    r = requests.get(stocktwits_symbol_url)
    data = r.json()
    
    st.subheader(f'Stocktwits for: {data["symbol"]["title"]}')
    
    for message in data["messages"]:
        st.image(message["user"]["avatar_url"])
        st.write(message["user"]["username"])
        st.write(message["created_at"])
        st.write(message["body"])
        st.markdown("---")


    st.write(data)
    
if option == "Ishares Etf Position Explorer":
    st.subheader("Get all Positions of an ETF in a Table")
    @st.cache
    def read_ishares_data(url):
        df = pd.read_csv(url, skiprows=2)
        return df

    url2 = st.text_area("ETF Url", value="", height=None, max_chars=None, key=None)
    if url2 == "":
        st.write("No Url Input.")
    else:
        df = read_ishares_data(url2)
        st.dataframe(df)

if option == "ARK Invest Portfolio":    
    
    
if option == "Total Portfolio Holding Calculator":   
    



