import os

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from alpaca_trade_api.rest import TimeFrame

# Alpaca API credentials
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


def bollinger_bands_strategy(symbol, start_date, end_date, initial_balance, initial_buy_amount, daily_amount):
    df = get_historical_data(symbol, start_date, end_date)
    df['SMA'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['Upper Band'] = df['SMA'] + (df['std'] * 2)
    df['Lower Band'] = df['SMA'] - (df['std'] * 2)

    balance = initial_balance
    num_shares = 0
    holding_initial = False

    for index, row in df.iterrows():
        # Buying strategy: Buy $1000 worth of stock when the price touches the lower Bollinger Band
        if row['close'] <= row['Lower Band'] and not holding_initial and balance >= initial_buy_amount:
            num_shares_to_buy = initial_buy_amount / row['close']
            cost = num_shares_to_buy * row['close']
            if cost <= balance:
                num_shares += num_shares_to_buy
                balance -= cost
                holding_initial = True
                print(f'Bought initial {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

        # Continue buying $10 worth of stock every day if holding initial shares
        if holding_initial and balance >= daily_amount:
            num_shares_to_buy = daily_amount / row['close']
            cost = num_shares_to_buy * row['close']
            if cost <= balance:
                num_shares += num_shares_to_buy
                balance -= cost
                print(f'Bought additional {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

        # Selling strategy: Sell the initial $1000 worth of stock when the price touches the upper Bollinger Band
        if row['close'] >= row['Upper Band'] and holding_initial:
            num_shares_to_sell = initial_buy_amount / row['close']
            revenue = num_shares_to_sell * row['close']
            if num_shares_to_sell <= num_shares:
                num_shares -= num_shares_to_sell
                balance += revenue
                holding_initial = False
                print(f'Sold initial {num_shares_to_sell:.4f} shares at {row["close"]} on {index}')

        # Continue selling $10 worth of stock every day if not holding initial shares
        if not holding_initial and num_shares > 0:
            num_shares_to_sell = min(daily_amount / row['close'], num_shares)
            revenue = num_shares_to_sell * row['close']
            num_shares -= num_shares_to_sell
            balance += revenue
            print(f'Sold additional {num_shares_to_sell:.4f} shares at {row["close"]} on {index}')

    final_balance = balance + num_shares * df['close'].iloc[-1]
    return final_balance, num_shares, balance


# Parameters
symbol = 'NFLX'
start_date = '2022-01-01'
end_date = '2023-01-01'
initial_balance = 10000
initial_buy_amount = 1000
daily_amount = 10

final_balance, num_shares, balance = bollinger_bands_strategy(symbol, start_date, end_date, initial_balance,
                                                              initial_buy_amount, daily_amount)
print(f'Initial Balance: ${initial_balance}')
print(f'Final Balance: ${final_balance}')
print(f'Remaining Shares: {num_shares:.4f}')
print(f'Cash Balance: ${balance}')