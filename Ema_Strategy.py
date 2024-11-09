import os

import alpaca_trade_api as tradeapi
import pandas as pd
import datetime

# Alpaca API credentials
API_KEY = os.environ.get("APCA_API_KEY_ID")
API_SECRET = os.environ.get("APCA_API_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'


# Initialize the Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')


def get_historical_data(symbol, start_date, end_date):
    barset = api.get_bars(symbol, tradeapi.TimeFrame.Day, start=start_date, end=end_date).df
    barset = barset.rename(columns={
        't': 'timestamp', 'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'
    })
    barset.index = pd.to_datetime(barset.index)
    return barset


def ema_strategy(symbol, start_date, end_date, daily_amount):
    df = get_historical_data(symbol, start_date, end_date)
    df['EMA30'] = df['close'].ewm(span=30, adjust=False).mean()

    balance = 0
    num_shares = 0
    total_invested = 0

    for index, row in df.iterrows():
        # Allocate $100 each day
        balance += daily_amount

        # Buy condition: stock price goes below EMA30
        if row['close'] < row['EMA30']:
            num_shares_to_buy = balance / row['close']
            num_shares += num_shares_to_buy
            total_invested += balance
            print(f'Bought {num_shares_to_buy:.4f} shares at {row["close"]} on {index}')
            balance = 0  # Reset the balance after buying

        # Sell condition: stock price goes above EMA30
        elif row['close'] > row['EMA30'] and num_shares > 0:
            balance += num_shares * row['close']
            print(f'Sold {num_shares:.4f} shares at {row["close"]} on {index}')
            num_shares = 0  # Reset the number of shares after selling

    final_balance = balance + num_shares * df['close'].iloc[-1]
    profit = final_balance - total_invested
    return final_balance, num_shares, total_invested, profit


# Parameters
symbol = 'QQQ'
start_date = '2015-01-01'
end_date = '2024-01-31'
daily_amount = 100

final_balance, num_shares, total_invested, profit = ema_strategy(symbol, start_date, end_date, daily_amount)

print(f'Final Balance: ${final_balance}')
print(f'Remaining Shares: {num_shares:.4f}')
print(f'Total Invested: ${total_invested}')
print(f'Profit: ${profit}')
