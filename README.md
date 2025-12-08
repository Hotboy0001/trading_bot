# Turtle Soup Trading Bot 🐢

A sophisticated algorithmic trading bot for MetaTrader 5 (MT5) that combines the **Turtle Soup ICT Strategy** with **Support & Resistance Confirmation**.

## 🚀 Features

*   **Multi-Pair Support**: Trades XAUUSD, EURUSD, BTCUSD, GBPUSD, NZDUSD simultaneously.
*   **Multi-Timeframe Analysis**: Scans Higher Timeframes (H4, H2, H1) for major setups.
*   **Precision Entry**: Executes on Lower Timeframes (M15, M5, M1) using MSS + FVG.
*   **Dynamic Position Sizing**: Never risks more than 5% of account balance per trade.
*   **Adaptive Risk:Reward**: Adjusts RR (1:3 to 1:7) based on signal confidence.
*   **S/R Confirmation**: Filters trades using High Volume Support & Resistance levels.

## 🛠️ Setup

**Prerequisites:**
*   Python 3.12.6 (64-bit) - [Download here](https://www.python.org/downloads/release/python-3126/)
*   MetaTrader 5 (64-bit) - [Download here](https://www.metatrader5.com/en/download)

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/Hotboy0001/trading_bot.git
    cd trading_bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Login to MT5**:
    *   Open MetaTrader 5 manually.
    *   **Login** to your account (File -> Login to Trade Account).
    *   **Keep MT5 running**.

4.  **Run**:
    ```bash
    python main.py
    ```

## ⚠️ Disclaimer
Trading Forex and Crypto involves significant risk. This bot is for educational purposes. Use at your own risk.
