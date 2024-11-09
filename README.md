# Trading Strategies Backtesting with Alpaca API

This repository contains several Python scripts that use the Alpaca API for backtesting trading strategies. The repository is structured to help users test different strategies on historical stock data provided by Alpaca’s API, including Bollinger Bands, Exponential Moving Averages (EMA), Moving Average Convergence Divergence (MACD), and Daily Buying patterns.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)


## Overview

This project leverages the Alpaca API, which provides free access to historical stock data. By using this API, users can easily fetch historical data and apply various trading strategies to simulate and backtest ideas. Each strategy has its own script in the repository, allowing users to focus on specific trading techniques.

The main objectives of this repository are:
1. To provide a framework for easy backtesting of trading ideas.
2. To demonstrate the implementation of several trading strategies.
3. To analyze the effectiveness of each strategy on historical data.

## Requirements

1. **Python 3.8+**
2. **Alpaca API Key**: You’ll need an Free Alpaca Paper Trading account and API key to fetch data. [Sign up here](https://docs.alpaca.markets/docs/paper-trading) if you don't have one.
3. **Python Packages**:
   - `alpaca-trade-api`
   - `pandas`
   - `matplotlib`
   - `numpy`
4. Setup Environment variables
   APCA_API_KEY_ID
   APCA_API_SECRET_KEY


   ```bash
   pip install alpaca-trade-api pandas matplotlib numpy
   ```
   
## Installation

### 1. Clone the Repository

First, clone this repository to your local machine using the following command:

```bash
git clone https://github.com/yourusername/your-repo-name.git
```

### Set Up Alpaca API Credentials

You can the free account for Paper Trading from Alpaca 
Refer https://docs.alpaca.markets/docs/paper-trading

### Execute the Script 
  Example
 ```python backtesting.py ```
   
