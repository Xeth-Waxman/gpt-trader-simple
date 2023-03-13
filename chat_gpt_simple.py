import requests
import pandas as pd
import numpy as np

# Step 1: Enter your API key and stock symbol
api_key = 'ZG5MLKJMUZ2UEAJ8'
symbols = ['MSFT', 'LPLA', 'IBM']

for symbol in symbols:
    try:
        # Step 2: Make an API request
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}'
        response = requests.get(url)
        data = response.json()

        # Step 3: Convert the data to a DataFrame
        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')

        # Step 4: Clean the data
        df = df.astype(float)
        df = df.fillna(method='ffill')
        df = df.dropna()

        # Step 5: Generate buy or sell signals
        df['SMA3'] = df['4. close'].rolling(window=3).mean()
        df['SMA20'] = df['4. close'].rolling(window=20).mean()
        df['Signal'] = 0.0
        df['Signal'][3:] = np.where(df['SMA3'][3:] > df['SMA20'][3:], 1.0, 0.0)
        df['Position'] = df['Signal'].diff()

        # Step 6: Print the buy or sell signals
        if df['Position'].sum() == 0:
            print(f"No signals generated for {symbol}")
        else:
            df.index = pd.to_datetime(df.index)
            for i in range(len(df)):
                if df['Position'][i] == 1:
                    print(f"BUY {symbol} at {df['4. close'][i]} on {df.index[i].date()}")
                elif df['Position'][i] == -1:
                    print(f"SELL {symbol} at {df['4. close'][i]} on {df.index[i].date()}")

    except KeyError:
        print(f"Invalid symbol {symbol}")
    except Exception as e:
        print(f"Error: {e}")
