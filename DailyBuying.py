import os

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import datetime
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


def monthly_investment_strategy(symbol, start_date, end_date, monthly_amount):
    df = get_historical_data(symbol, start_date, end_date)
    num_shares = 0
    total_invested = 0

    # Filter to get only the first trading day of each month
    df['month'] = df.index.to_period('M')
    first_day_of_month = df.groupby('month').head(1)

    for index, row in first_day_of_month.iterrows():
        num_shares_to_buy = monthly_amount / row['close']
        num_shares += num_shares_to_buy
        total_invested += monthly_amount
        print(f'Bought {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

    final_balance = num_shares * df['close'].iloc[-1]
    profit = final_balance - total_invested
    return final_balance, num_shares, total_invested, profit

def daily_investment_strategy(symbol, start_date, end_date, daily_amount):
    df = get_historical_data(symbol, start_date, end_date)
    num_shares = 0
    total_invested = 0

    for index, row in df.iterrows():
        num_shares_to_buy = daily_amount / row['close']
        num_shares += num_shares_to_buy
        total_invested += daily_amount
        print(f'Bought {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')

    final_balance = num_shares * df['close'].iloc[-1]
    profit = final_balance - total_invested
    return final_balance, num_shares, total_invested, profit


# Parameters
# symbols = ['MSFT', 'NVDA', 'AAPL', 'AMZN', 'META', 'AVGO', 'GOOGL', 'GOOG', 'COST', 'TSLA']
symbols = ['QQQ']

start_date = '2020-01-01'
end_date = '2024-01-01'
initial_balance = 100
daily_amount = 100

cumulative_final_balance = 0
cumulative_total_invested = 0
cumulative_profit = 0

for symbol in symbols:
    final_balance, num_shares, total_invested, profit = daily_investment_strategy(symbol, start_date, end_date, daily_amount)
    cumulative_final_balance += final_balance
    cumulative_total_invested += total_invested
    cumulative_profit += profit
# print(f'Initial Balance: ${initial_balance}')
# print(f'Final Balance: ${final_balance}')
# print(f'Remaining Shares: {num_shares:.4f}')
# print(f'Cash Balance: ${balance}')

print(f'Cumulative Final Balance: ${cumulative_final_balance}')
print(f'Cumulative Total Invested: ${cumulative_total_invested}')
print(f'Cumulative Profit: ${cumulative_profit}')


# symbols = ['MSFT', 'NVDA', 'AAPL', 'AMZN', 'META', 'AVGO', 'GOOGL', 'GOOG', 'COST', 'TSLA', 'NFLX', 'AMD', 'PEP', 'QCOM', 'TMUS']
# weights = [8.48, 8.13, 8.07, 5.17, 4.65, 4.51, 2.80, 2.72, 2.60, 2.31, 1.95, 1.87, 1.64, 1.62, 1.48]  # corresponding weights
# total_daily_investment = 100  # Total daily investment amount
#
# start_date = '2020-01-01'
# end_date = '2024-01-01'
#
# # Initialize cumulative final balance and total investment
# cumulative_final_balance = 0
# cumulative_total_invested = 0
# cumulative_profit = 0
#
# # Loop over each symbol and call the daily investment strategy
# for symbol, weight in zip(symbols, weights):
#     daily_amount = total_daily_investment * (weight / 100)
#     final_balance, num_shares, total_invested, profit = daily_investment_strategy(symbol, start_date, end_date, daily_amount)
#     cumulative_final_balance += final_balance
#     cumulative_total_invested += total_invested
#     cumulative_profit += profit
#     print(f'{symbol} - Final Balance: ${final_balance}')
#     print(f'{symbol} - Remaining Shares: {num_shares:.4f}')
#     print(f'{symbol} - Total Invested: ${total_invested}')
#     print(f'{symbol} - Profit: ${profit}')
#     print('--------------------------------------------')
#
# # Print cumulative results
# print(f'Cumulative Final Balance: ${cumulative_final_balance}')
# print(f'Cumulative Total Invested: ${cumulative_total_invested}')
# print(f'Cumulative Profit: ${cumulative_profit}')