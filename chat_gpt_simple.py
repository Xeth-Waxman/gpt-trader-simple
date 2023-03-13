import requests
import pandas as pd
import numpy as np

def get_stock_data(api_key, symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
    df = df.astype(float)
    df = df.fillna(method='ffill')
    df = df.dropna()
    return df

def generate_signals(df, short_window=3, long_window=20):
    df[f'SMA{short_window}'] = df['4. close'].rolling(window=short_window).mean()
    df[f'SMA{long_window}'] = df['4. close'].rolling(window=long_window).mean()
    df['Signal'] = 0.0
    df['Signal'][short_window:] = np.where(df[f'SMA{short_window}'][short_window:] > df[f'SMA{long_window}'][short_window:], 1.0, 0.0)
    df['Position'] = df['Signal'].diff()
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

def generate_and_print_signals(api_key, symbol, short_window=3, long_window=20):
    try:
        df = get_stock_data(api_key, symbol)
        df = generate_signals(df, short_window, long_window)
        print_signals(df, symbol)
    except KeyError:
        print(f"Invalid symbol {symbol}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
api_key = 'ZG5MLKJMUZ2UEAJ8'
symbols = ['MSFT', 'LPLA', 'IBM']

for symbol in symbols:
    generate_and_print_signals(api_key, symbol, short_window=3, long_window=20)
