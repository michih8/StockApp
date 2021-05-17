import pandas as pd
import numpy as np
import streamlit as st
import requests 
import yfinance as yf

import plotly.express as px
import plotly.graph_objects as go

import io


st.sidebar.title("Options")
option = st.sidebar.selectbox("Which Dashboard?", ("Chart", "Portfolio", "Crypto", "Total Portfolio Holding Calculator", "Ishares Etf Position Explorer", "Symbol", "ARK Invest Portfolio", ), 2)

@st.cache
def get_ticker_data(symbol, years=3):
    period=f"{years}y"
    ticker = yf.Ticker(symbol)
    infos = ticker.info
    hist_data = ticker.history(period)
    
    return ticker, infos, hist_data

@st.cache
def plot_data(hist_data):     
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
    
def plot_and_infos(symbol, isEtf=False):
    ticker, infos, hist_data = get_ticker_data(symbol)
    
    c1, c2 = st.beta_columns((1, 4))
    
    try:
        c1.image(infos["logo_url"])
    except:
        c1.subheader(symbol)
        
    with c2:
        c2.header(infos["longName"]) 
        c2.subheader("Basic Info:")
    
    if not isEtf:      
        f"""
        **Country:** {infos["country"]}
        
        **Sector:** {infos["industry"]}
        
        **Dividend:** {infos["dividendRate"]} %
        
        **Website:** {infos["website"]}
        
        ---
        """
        st.image(f'https://finviz.com/chart.ashx?t={symbol}')

    try:
        fig = plot_data(hist_data)
        st.plotly_chart(fig, use_container_width=True)        
        #st.write(hist_data)
        
    except:
        st.write("No Plot Data available right now...")

if option == "Crypto":
    st.image("https://alternative.me/crypto/fear-and-greed-index.png", caption="Fear & Greed Index")

#st.title(option)

if option == "Total Portfolio Holding Calculator":
    
    holdings_columns = ["Ticker","Weight","Url"]
    
    text_csv = st.text_area(f"Your Etf Positions in Format: {holdings_columns}")

    
    if st.button('Run'):
        if text_csv != None:
                portfolio_holdings_df = pd.read_csv(io.StringIO(text_csv), sep=";", names=holdings_columns) 
              
        else:
            st.write("Please Enter your holdings")
                

        '----'
        
        with st.spinner("Loading Data..."):
    
            
            
            #info_ticker = st.selectbox("Holdings Info", holdings_df["Ticker"])
            #plot_and_infos(u'{}'.format(info_ticker), isEtf=True)
            
            
            
            def conv_str_to_float(df, conv_cols):
                df_conv = df.copy()
                for col in conv_cols:
                    df_conv[col] = [float(i.replace('.', '').replace(',', '.')) for i in df_conv[col]]    
                    
                return df_conv
            
            def scan_ishares_etf_holdings(url):
                drop_cols = ["Anlageklasse", "Nominale", "Nominalwert", "Börse", "Marktwährung"]
                rename_cols = {"Gewichtung (%)":"Gewichtung"}
                conv_cols = ["Gewichtung", "Kurs", "Marktwert"]
                
                df = pd.read_csv(url, skiprows=2, )  
                df = df.drop(columns=drop_cols)
                df = df.rename(columns=rename_cols)
                df = df[:-1]
                df = conv_str_to_float(df, conv_cols)
                df = df.loc[df.Gewichtung > 0.01]
                return df  
            

            hold_positions = []
            for index, hold in portfolio_holdings_df.iterrows():
                hold_positions_df = scan_ishares_etf_holdings(hold["Url"])
                hold_positions_df.Gewichtung = hold_positions_df.Gewichtung / 100
                hold_positions_df["Gewichtung"] = hold.Weight * hold_positions_df.Gewichtung
                
                hold_positions.append(hold_positions_df)

            portfolioDf = pd.concat(hold_positions).sort_values("Gewichtung", ascending=False).reset_index(drop=True)
            
            st.header("Portfolio Holdings")
            st.write(portfolioDf)    
            st.balloons()
            







if option == "Chart":
    symbol = st.sidebar.text_input(label="Symbol:", value="ASML",)
    years = st.sidebar.slider("Years:", 1, 6, value=3)
    
    plot_and_infos(symbol)
    
    
        
    # akt_name = infos["name"]
    # isin = infos["isin"]
    # aktionär_url = f"https://www.deraktionaer.de/aktien/kurse/{akt_name}-{isin}.html"
    
    with st.beta_expander("Links:"):
        c1, c2 = st.beta_columns((1,3))
        c2.markdown(f'[![Der Aktionär](https://www.deraktionaer.de/assets/images/svg/logo-deraktionaer.svg)](https://www.deraktionaer.de/)')




if option == "Portfolio":   
    
    headcol, chartcol = st.beta_columns((1.5, 3))
    headcol.header("My Portfolio")
    chartcol.image(f'https://finviz.com/chart.ashx?t={"PLTR"}')
        
    bcol = st.beta_columns((3,1,1,1,1))
    bcol[1].button(label="Day")
    bcol[2].button(label="1Wk")
    bcol[3].button(label="1Mo")
    bcol[4].button(label="Max")

    st.subheader("Performance:")
    perfcol = st.beta_columns((1, 1, 1))
    perfcol[0].button(label="Performance: +500€")
    perfcol[1].button(label="Monthly Performance: +500€")
    perfcol[2].button(label="Yearly Performance: +500€")



    
    
        
    

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
    
    #  #holdings > div.holdings.fund-component-data-export > a

    url2 = st.text_area("ETF Url", value="", height=None, max_chars=None, key=None)
    if url2 == "":
        st.write("No Url Input.")
    else:
        df = read_ishares_data(url2)
        st.dataframe(df)
        
    

if option == "ARK Invest Portfolio":    
    st.write(option)
    st.markdown("[Ark Invest Fond Holdings](https://cathiesark.com/ark-funds-combined/complete-holdings)")

    



