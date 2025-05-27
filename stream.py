'''import streamlit as st
import plotly.express as px
import pandas as pd
import threading
from strategy import *
from main import *
from live_trade import *
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')  # Use non-interactive backend


stop_event = threading.Event()

def stop1():
    stop_event.set() 
    if ws and hasattr(ws, 'close'): 
        ws.close()
    else:
        print("WebSocket is either None or doesn't have a close method.")
    return "Live trading stopped."
#st.set_page_config(page_title="Testing And Trading", page_icon=":chart_with_upwards_trend:",layout="wide")
def you(client):
     
    info = client.get_account()
    balance = info['balances']
    available =[]
    asset=[]
    
    for dict in balance:
        free = dict["free"]
        name=dict["asset"]
        if name =="USDT":
            money =free
        available.append(free)
        asset.append(name)
    df=pd.DataFrame({
        "available":available,
        "name":asset
    })
    return df,float(money)
def main():
    st.title(":bar_chart: Strategy Analysis")
    st.markdown("<style>div.bloack-container{padding-top:1rem;}</style>",unsafe_allow_html=True)
    
    client = Client(config.API_KEY,config.SECRET_KEY,testnet=True)

    df,money=you(client)


    col1,col2= st.columns((2))
  

    with col2:
        
        st.write("### Account Balances")
        st.metric(label="USDT Balance", value=f"{money:.2f} USDT")
        fig = px.bar(df, x='name', y='available', text='available', labels={'available': 'Available Balance', 'name': 'Asset'})
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', 
            width=1200,  
            height=300,  
            margin=dict(t=10) )
        st.plotly_chart(fig, use_container_width=True)
        st.sidebar.dataframe(df.style.highlight_max(axis=0, color='lightgreen'), width=800)
    st.sidebar.header("What you want to do ?")
    choice = st.sidebar.selectbox("Pick your choice",["Live Trading ","Backtest"])

    with col1:
        symbol= st.text_input("Enter the symbol name")
        
        
        if choice=="Backtest":
            interval=st.selectbox("Interval",["1m","1h","1d"])
            strategy_choice = st.selectbox("Choose Strategy", ("Mean Reversion", "Moving Average Crossover", "Momentum Strategy"))
            stop_loss=st.number_input("Stop loss",value=0.02)
            take_profit=st.number_input("Take profit at",value=0.05)
            if strategy_choice == "Mean Reversion":
                strategy_class = MeanReversion
                bollinger_period = st.number_input("Bollinger Period", value=20)
                bollinger_dev = st.number_input("Bollinger Dev", value=2)
                rsi_period = st.number_input("RSI Period", value=14)
                rsi_oversold = st.number_input("RSI Oversold", value=30)
                rsi_overbought = st.number_input("RSI Overbought", value=70)
                strategy_params = {
                    'bollinger_period': bollinger_period,
                    'bollinger_dev': bollinger_dev,
                    'rsi_period': rsi_period,
                    'rsi_oversold': rsi_oversold,
                    'rsi_overbought': rsi_overbought,
                    'stop_loss':stop_loss,
                    'take_profit':take_profit
                }

            elif strategy_choice == "Moving Average Crossover":
                strategy_class = MovingAverageCrossover
                short_period = st.number_input("Short SMA Period", value=20)
                long_period = st.number_input("Long SMA Period", value=50)
                rsi_period = st.number_input("RSI Period", value=14)
                rsi_overbought = st.number_input("RSI Overbought", value=70)
                rsi_oversold = st.number_input("RSI Oversold", value=30)
                    
                strategy_params = {
                    'short_period': short_period,
                    'long_period': long_period,
                    'rsi_period': rsi_period,
                    'rsi_overbought': rsi_overbought,
                    'rsi_oversold': rsi_oversold,
                    'stop_loss':stop_loss,
                    'take_profit':take_profit
                }
            

            elif strategy_choice == "Momentum Strategy":
                strategy_class = MomentumStrategy
                momentum_period = st.number_input("Momentum Period", value=100)
                roc_threshold = st.number_input("ROC Threshold", value=0)
                
                strategy_params = {
                    'momentum_period': momentum_period,
                    'roc_threshold': roc_threshold,
                    'stop_loss':stop_loss,
                    'take_profit':take_profit

                }
            
            startdate=pd.to_datetime(st.date_input("Start date"))
            enddate=pd.to_datetime(st.date_input("End date"))
            if st.sidebar.button("Run Backtest"):
                st.write("Running portfolio backtest... Please wait.")
                cerebro= run_backtest(strategy_class,strategy_params,symbol,money,startdate,enddate,interval)
                      
                        
                        
                with col2:
                    cerebro.plot()
        else:
            live_strategy=st.sidebar.selectbox("choose:",("RSI","MOVING_AVERAGE"))
            pla = st.sidebar.empty() 
            plaa = st.sidebar.empty()
            if live_strategy=="RSI":

                rsi_p=st.number_input("Enter RSI period Value",value=14)
                rsi_ob=st.number_input("Enter rsi overbought",value =70)
                rsi_os=st.number_input("Enter rsi oversold",value =30)
                trade_q=st.number_input("Eenter trade quantity",value =0.05)
                if st.sidebar.button("Stop Live Trading"):
                        st.write(stop1())
                if st.button("Start Live Trading"):
                    stop_event.clear()  
                    
                    #threading.Thread(target=real_call, args=(RSI, money, rsi_ob, rsi_os, rsi_p, trade_q, symbol, pla, plaa, 0)).start() 
                    real_call(RSI,money,rsi_ob,rsi_os,rsi_p,trade_q,symbol,pla,plaa,0) 
            else:
           
                trade_q=st.number_input("Eenter trade quantity",value =0.05)

                if st.sidebar.button("Stop Live Trading"):
                        st.write(stop1())
                if st.button("Start Live Trading"):
                    stop_event.clear()  
                    #threading.Thread(target=real_call, args=(MOVING_AVERAGE, money, rsi_ob, rsi_os, rsi_p, trade_q, symbol, pla, plaa, 0)).start()
                    real_call(MOVING_AVERAGE,money,70,30,14,trade_q,symbol,pla,plaa,0) 
   
                    #threading.Thread(target=real_call, args=(moving_average, money, 70, 30, 14, trade_q, symbol, pla, plaa, 0)).start()
                        
 
                
                  

if __name__ == "__main__":
    main()
    
'''



import streamlit as st
import plotly.express as px
import pandas as pd
import threading
from strategy import *
from main import *
from live_trade import *
import matplotlib
matplotlib.use('Agg')  # Must be before other matplotlib imports
import matplotlib.pyplot as plt
from binance.client import Client
import config
from queue import Queue

# Global variables
#stop_event = threading.Event()
#plot_queue = Queue()

def stop_trading():
    #stop_event.set()
    if 'ws' in globals() and ws and hasattr(ws, 'close'):
        ws.close()
    return "Live trading stopped."

def get_account_balance(client):
    info = client.get_account()
    balance = info['balances']
    available = []
    asset = []
    money = 0.0
    
    for item in balance:
        free = item["free"]
        name = item["asset"]
        if name == "USDT":
            money = free
        if float(free) > 0:  # Only show assets with balance
            available.append(free)
            asset.append(name)
    df = pd.DataFrame({"available": available, "name": asset})
    return df, float(money)
import json

def run_backtest_wrapper(strategy_class, strategy_params, symbol, money, startdate, enddate, interval):
    try:
        cerebro ,data,buy_signals ,sell_signals= run_backtest(strategy_class, strategy_params, symbol, money, startdate, enddate, interval)
        fig, ax = plt.subplots(figsize=(14, 7))
        '''print("love u")
        print(buy_signals)
        print("herde")
        print("sell:",sell_signals)

        print(data)'''

        



        data['Open time'] = pd.to_datetime(data['Open time'])


        # Plot close prices

        ax.plot(data['Open time'], data['Close'], label='Close Price', color='blue')
        
        # Plot buy signals
        #print("here")
        if buy_signals:
            buy_dates, buy_prices = zip(*buy_signals)
            ax.scatter(buy_dates, buy_prices, marker='^', color='green', label='Buy Signal', s=100)
        
        # Plot sell signals
        if sell_signals:
            sell_dates, sell_prices = zip(*sell_signals)
            ax.scatter(sell_dates, sell_prices, marker='v', color='red', label='Sell Signal', s=100)
        
        # Set titles and labels
        ax.set_title('Price Chart with Buy/Sell Signals')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()
        ax.grid(True)
        
        # Render the plot in Streamlit
        st.pyplot(fig)

        
        # Put the figure in the queue
    except Exception as e:
        st.error(f"Backtest error: {str(e)}")
        

def main():
    st.title(":bar_chart: Strategy Analysis")
    st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)
    
    client = Client(config.API_KEY, config.SECRET_KEY, testnet=True)
    df, money = get_account_balance(client)

    col1, col2 = st.columns((2))

    with col2:
        st.write("### Account Balances")
        st.metric(label="USDT Balance", value=f"{money:.2f} USDT")
        fig = px.bar(df, x='name', y='available', text='available', 
                    labels={'available': 'Available Balance', 'name': 'Asset'})
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', 
                        width=1200, height=300, margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
        st.sidebar.dataframe(df.style.highlight_max(axis=0, color='lightgreen'), width=800)

    st.sidebar.header("Choose Action")
    choice = st.sidebar.radio("Select Mode", ["Backtest", "Live Trading"])

    with col1:
        symbol = st.text_input("Trading Pair", value="BTCUSDT").upper()
        
        if choice == "Backtest":
            interval = st.selectbox("Timeframe", ["1m", "1h", "1d"])
            strategy_choice = st.selectbox("Strategy", 
                                         ("Mean Reversion", "Moving Average Crossover", "Momentum Strategy"))
            
            st.subheader("Risk Parameters")
            stop_loss = st.number_input("Stop Loss (%)", value=2.0, min_value=0.1, max_value=50.0, step=0.1)/100
            take_profit = st.number_input("Take Profit (%)", value=5.0, min_value=0.1, max_value=50.0, step=0.1)/100
            
            strategy_params = {
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }

            if strategy_choice == "Mean Reversion":
                st.subheader("Mean Reversion Parameters")
                strategy_class = MeanReversion
                strategy_params.update({
                    'bollinger_period': st.number_input("Bollinger Period", value=20, min_value=5, max_value=100),
                    'bollinger_dev': st.number_input("Bollinger Deviation", value=2.0, min_value=0.5, max_value=5.0, step=0.1),
                    'rsi_period': st.number_input("RSI Period", value=14, min_value=5, max_value=50),
                    'rsi_oversold': st.number_input("RSI Oversold", value=30, min_value=5, max_value=45),
                    'rsi_overbought': st.number_input("RSI Overbought", value=70, min_value=55, max_value=95)
                })

            elif strategy_choice == "Moving Average Crossover":
                st.subheader("Moving Average Parameters")
                strategy_class = MovingAverageCrossover
                strategy_params.update({
                    'short_period': st.number_input("Short SMA Period", value=20, min_value=5, max_value=100),
                    'long_period': st.number_input("Long SMA Period", value=50, min_value=10, max_value=200),
                    'rsi_period': st.number_input("RSI Period", value=14, min_value=5, max_value=50),
                    'rsi_overbought': st.number_input("RSI Overbought", value=70, min_value=55, max_value=95),
                    'rsi_oversold': st.number_input("RSI Oversold", value=30, min_value=5, max_value=45)
                })

            elif strategy_choice == "Momentum Strategy":
                st.subheader("Momentum Parameters")
                strategy_class = MomentumStrategy
                strategy_params.update({
                    'momentum_period': st.number_input("Momentum Period", value=100, min_value=10, max_value=200),
                    'roc_threshold': st.number_input("ROC Threshold", value=0.0, min_value=-10.0, max_value=10.0, step=0.1)
                })
            
            st.subheader("Backtest Period")
            startdate = pd.to_datetime(st.date_input("Start Date"))
            enddate = pd.to_datetime(st.date_input("End Date"))
            
            if st.button("Run Backtest"):
                with st.spinner("Running backtest... This may take a while"):
                    # Run backtest in a thread
                    
                    run_backtest_wrapper(strategy_class, strategy_params, symbol, money, startdate, enddate, interval)
                    
                        
                    
                    # Check for plot results

        else:  # Live Trading
            st.subheader("Live Trading Parameters")
            live_strategy = st.selectbox("Strategy Type", ("RSI", "MOVING_AVERAGE"))
            trade_q = st.number_input("Trade Quantity (USDT)", value=50.0, min_value=5.0, max_value=float(money), step=5.0)
            if st.sidebar.button("Stop Live Trading"):
                st.warning(stop_trading())
            if live_strategy == "RSI":
                st.subheader("RSI Parameters")
                rsi_p = st.number_input("RSI Period", value=14, min_value=5, max_value=50)
                rsi_ob = st.number_input("Overbought Level", value=70, min_value=55, max_value=95)
                rsi_os = st.number_input("Oversold Level", value=30, min_value=5, max_value=45)
                
                if st.button("Start RSI Strategy"):
                    #stop_event.clear()

                    print("started")
                    real_call("RSI", money, rsi_ob, rsi_os, rsi_p, trade_q, symbol, st.empty(), st.empty(), 0)
                    
                    
            else:  # MOVING_AVERAGE
                if st.button("Start MA Strategy"):
                    #stop_event.clear()
                    real_call("MOVING_AVERAGE", money, 70, 30, 14, trade_q, symbol, st.empty(), st.empty(), 0)
            
            

if __name__ == "__main__":
    main()