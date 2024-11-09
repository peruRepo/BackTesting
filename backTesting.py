import os

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from alpaca_trade_api.rest import TimeFrame

# Alpaca API credentials
#  get from environment variables
API_KEY = os.environ.get("APCA_API_KEY_ID")
API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize the Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

def get_historical_data(symbol, start_date, end_date):
    barset = api.get_bars(symbol, TimeFrame.Day, start=start_date, end=end_date).df
    barset = barset.rename(columns={
        't': 'timestamp', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'
    })
    barset.index = pd.to_datetime(barset.index)
    return barset

def backtest_strategy(symbol, start_date, end_date, initial_balance):
    df = get_historical_data(symbol, start_date, end_date)
    df['EMA30'] = df['close'].ewm(span=30, adjust=False).mean()
    df['signal'] = 0
    df['signal'][30:] = np.where(df['close'][30:] < df['EMA30'][30:], 1, 0)
    df['position'] = df['signal'].diff()

    balance = initial_balance
    num_shares = 0
    buy_price = 0

    for index, row in df.iterrows():
        if row['position'] == 1:  # Buy signal
            if balance > 0:
                num_shares = balance // row['close']
                buy_price = row['close']
                balance -= num_shares * buy_price
                print(f'Bought {num_shares} shares at {buy_price} on {index}')
        elif row['position'] == -1:  # Sell signal
            if num_shares > 0:
                sell_price = row['close']
                balance += num_shares * sell_price
                print(f'Sold {num_shares} shares at {sell_price} on {index}')
                num_shares = 0

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance


def backtest_strategy2(symbol, start_date, end_date, initial_balance):
    df = get_historical_data(symbol, start_date, end_date)
    df['EMA5'] = df['close'].ewm(span=30, adjust=False).mean()
    df['EMA10'] = df['close'].ewm(span=60, adjust=False).mean()
    df['position'] = 0  # Position 1 means buy, -1 means sell

    balance = initial_balance
    num_shares = 0
    total_investment = 0

    for index, row in df.iterrows():
        # Buying strategy
        if row['close'] < row['EMA30']:
            if balance > 0:
                num_shares_to_buy = balance // row['close']
                if num_shares_to_buy > 0:
                    total_investment += num_shares_to_buy * row['close']
                    balance -= num_shares_to_buy * row['close']
                    num_shares += num_shares_to_buy
                    print(f'Bought {num_shares_to_buy} shares at {row["close"]} on {index}')

        # Selling strategy
        if row['close'] > row['EMA60'] and num_shares > 0:
            num_shares_to_sell = max(1, num_shares // 10)  # Sell one-tenth or at least one share
            sell_amount = num_shares_to_sell * row['close']
            balance += sell_amount
            num_shares -= num_shares_to_sell
            total_investment -= num_shares_to_sell * row['close']
            print(f'Sold {num_shares_to_sell} shares at {row["close"]} on {index}')

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance, num_shares, balance

# Parameters
def backtest_strategy3(symbol, start_date, end_date, initial_balance, buy_amount, sell_amount):
    df = get_historical_data(symbol, start_date, end_date)
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA30'] = df['close'].ewm(span=30, adjust=False).mean()

    balance = initial_balance
    num_shares = 0

    for index, row in df.iterrows():
        # Buying strategy: Buy $10 worth of stock every day if the price is above the 50-day EMA
        if row['close'] > row['EMA50'] and balance >= buy_amount:
            num_shares_to_buy = buy_amount // row['close']
            cost = num_shares_to_buy * row['close']
            if cost <= balance:
                num_shares += num_shares_to_buy
                balance -= cost
                print(f'Bought {num_shares_to_buy} shares at {row["close"]} on {index}')

        # Selling strategy: Sell $10 worth of stock every day if the price is above the 30-day EMA
        if row['close'] > row['EMA30'] and num_shares > 0:
            num_shares_to_sell = min(sell_amount // row['close'], num_shares)
            revenue = num_shares_to_sell * row['close']
            num_shares -= num_shares_to_sell
            balance += revenue
            print(f'Sold {num_shares_to_sell} shares at {row["close"]} on {index}')

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance, num_shares, balance


def backtest_strategy4(symbol, start_date, end_date, initial_balance, buy_amount, sell_amount):
    df = get_historical_data(symbol, start_date, end_date)
    df['EMA5'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA10'] = df['close'].ewm(span=30, adjust=False).mean()

    balance = initial_balance
    num_shares = 0

    for index, row in df.iterrows():
        # Buying strategy: Buy $10 worth of stock every day if the price is above the 50-day EMA
        if row['close'] > row['EMA10'] and balance >= buy_amount:
            num_shares_to_buy = buy_amount / row['close']
            cost = num_shares_to_buy * row['close']
            if cost <= balance:
                num_shares += num_shares_to_buy
                balance -= cost
                print(f'Bought {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

        # Selling strategy: Sell $10 worth of stock every day if the price is above the 30-day EMA
        if row['close'] > row['EMA5'] and num_shares > 0:
            num_shares_to_sell = min(sell_amount / row['close'], num_shares)
            revenue = num_shares_to_sell * row['close']
            num_shares -= num_shares_to_sell
            balance += revenue
            print(f'Sold {num_shares_to_sell:.4f} shares at {row["close"]} on {index}')

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance, num_shares, balance


def bollinger_bands_strategy(symbol, start_date, end_date, initial_balance):
    df = get_historical_data(symbol, start_date, end_date)
    df['SMA'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['Upper Band'] = df['SMA'] + (df['std'] * 2)
    df['Lower Band'] = df['SMA'] - (df['std'] * 2)

    balance = initial_balance
    num_shares = 0

    for index, row in df.iterrows():
        # Buy when the stock price touches the lower Bollinger Band
        if row['close'] <= row['Lower Band'] and balance >= row['close']:
            num_shares_to_buy = balance // row['close']
            cost = num_shares_to_buy * row['close']
            if cost <= balance:
                num_shares += num_shares_to_buy
                balance -= cost
                print(f'Bought {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

        # Sell when the stock price touches the upper Bollinger Band
        if row['close'] >= row['Upper Band'] and num_shares > 0:
            num_shares_to_sell = num_shares
            revenue = num_shares_to_sell * row['close']
            num_shares -= num_shares_to_sell
            balance += revenue
            print(f'Sold {num_shares_to_sell:.4f} shares at {row["close"]} on {index}')

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance, num_shares, balance


# Parameters
symbol = 'AAPL'
start_date = '2021-01-01'
end_date = '2023-01-01'
initial_balance = 1000

# final_balance, num_shares, balance = bollinger_bands_strategy(symbol, start_date, end_date, initial_balance)
# print(f'Initial Balance: ${initial_balance}')
# print(f'Final Balance: ${final_balance}')
# print(f'Remaining Shares: {num_shares:.4f}')
# print(f'Cash Balance: ${balance}')

# Parameters
symbol = 'AAPL'
start_date = '2021-01-01'
end_date = '2023-01-01'
initial_balance = 1000
buy_amount = 10
sell_amount = 10

final_balance, num_shares, balance = backtest_strategy4(symbol, start_date, end_date, initial_balance, buy_amount,
                                                       sell_amount)
print(f'Initial Balance: ${initial_balance}')
print(f'Final Balance: ${final_balance}')
print(f'Remaining Shares: {num_shares:.4f}')
print(f'Cash Balance: ${balance}')