# gpt-trader-simple
A simple trading application, written by ChatGPT. The rules:
1. ChatGPT must write all the code. 
2. When the code has errors, ChatGPT must be the one to correct the errors.
3. I can supply the error messages to ChatGPT, but I can't provide hints as to what might be wrong with the code. I am acting like a complete non-programmer.

# The initial prompt:
> I would like to create a python application that uses the Alpha Vantage TIME_SERIES_DAILY_ADJUSTED API to collect stock data for a selected stock, and then generate a buy or sell signal based on trading strategies. 

# Conclusion
This was pretty successful! While the trading strategy is terrible, and the hardcoded magic strings drive me nuts, this is a working application. The program downloads the list of DJIA stocks, uses a 50/200 Exponential Weighted Average crossover to determine buy/sell signals, and then backtests the strategy with a starting pot of $10k. Finally, it prints out the results of trading each stock, starting with the stock that had the highest annualized return, descending on that column.

The next project will move from defining the strategy in the application, to using an application to determine the most profitable strategy. ChatGPT has some real issues with data types and arrays,. but it is a productivity enhancer, particularly with things like sorting lists, formatting output, etc. 