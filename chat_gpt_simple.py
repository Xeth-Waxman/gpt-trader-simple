import requests
import pandas as pd
import numpy as np
import yfinance as yf
import logging
import configparser

logger = logging.getLogger("yfinance")
logger.setLevel(logging.ERROR)

def get_stock_data(symbol):
    data = yf.download(symbol, period='max', group_by='ticker')
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data.columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
    data = data.dropna()
    return data

def generate_signals(df, short_window=50, long_window=200):
    df[f'SMA{short_window}'] = df['4. close'].rolling(window=short_window).mean()
    df[f'SMA{long_window}'] = df['4. close'].rolling(window=long_window).mean()
    df['Signal'] = 0.0
    df.loc[df.index[short_window:], 'Signal'] = np.where(df[f'SMA{short_window}'][short_window:] > df[f'SMA{long_window}'][short_window:], 1.0, 0.0)
    df['Position'] = df['Signal'].diff()
    return df

def backtest_strategy(data, short_window=50, long_window=200, initial_capital=10000):
    df = data.copy()
    df = generate_signals(df, short_window, long_window)
    df['Returns'] = df['4. close'].pct_change() * df['Position'].shift(1)
    df['Cumulative Returns'] = (1 + df['Returns']).cumprod()
    df['Position'] = df['Signal']
    df['Portfolio Holdings'] = df['Position'] * initial_capital * df['Cumulative Returns']
    df['Cash'] = initial_capital - (df['Position'].diff() * df['4. close']).cumsum()
    df['Total Holdings'] = df['Cash'] + df['Portfolio Holdings']
    df['Returns'] = df['Total Holdings'].pct_change()
    
    # Count the number of trades
    num_trades = sum(abs(df['Position'].diff()) > 0)
    
    return df

def print_signals(df, symbol):
    if df['Position'].sum() == 0:
        print(f"No signals generated for {symbol}")
    else:
        df.index = pd.to_datetime(df.index)
        for i in range(len(df)):
            if df['Position'][i] == 1:
                print(f"BUY {symbol} at {df['4. close'][i]} on {df.index[i].date()}")
            elif df['Position'][i] == -1:
                print(f"SELL {symbol} at {df['4. close'][i]} on {df.index[i].date()}")

def generate_and_backtest_signals(api_key, symbol, short_window=50, long_window=200, initial_capital=10000):
    try:
        # Step 1: Get historical stock data
        data = get_stock_data(symbol)

        # Step 2: Generate signals and backtest strategy
        df = backtest_strategy(data, short_window, long_window, initial_capital)

        # Step 3: Extract signals
        signals = []
        for i in range(len(df)):
            if df['Position'][i] == 1:
                signals.append(('BUY', df['4. close'][i], df.index[i].date()))
            elif df['Position'][i] == -1:
                signals.append(('SELL', df['4. close'][i], df.index[i].date()))

        return df, signals

    except KeyError:
        print(f"Invalid symbol {symbol}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('API', 'key')
dow_jones_symbols = ['AAPL', 'AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'DIS', 'DOW', 'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PG', 'PFE', 'TRV', 'UNH', 'RTX', 'VZ', 'V', 'WBA', 'WMT', 'XOM']

results = []
initial_capital = 10000

for symbol in dow_jones_symbols:
    df, signals = generate_and_backtest_signals(api_key, symbol, short_window=50, long_window=200, initial_capital=initial_capital)
    annualized_return = ((df['Total Holdings'][-1] / initial_capital) ** (252 / len(df))) - 1
    total_return = ((df['Total Holdings'][-1] / initial_capital) - 1) * 100
    num_trades = sum(abs(df['Position'].diff()) > 0)
    results.append((symbol, annualized_return, total_return, num_trades))

# Sort results by annualized return in descending order
results.sort(key=lambda x: x[1], reverse=True)

# Print results
print("Results:")
for result in results:
    print(f"{result[0]}: {result[1]:.2%} ({result[2]:.2f}%), {result[3]} trades")