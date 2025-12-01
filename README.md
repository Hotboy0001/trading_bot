# Turtle Soup Trading Bot 🐢

A sophisticated algorithmic trading bot for MetaTrader 5 (MT5) that combines the **Turtle Soup ICT Strategy** with **Support & Resistance Confirmation**.

## 🚀 Features

*   **Multi-Pair Support**: Trades GBPUSD, EURUSD, XAUUSD, BTCUSD, ETHUSD, NZDUSD simultaneously.
*   **Multi-Timeframe Analysis**: Scans Higher Timeframes (H4, H2, H1) for major setups.
*   **Precision Entry**: Executes on Lower Timeframes (M15, M5, M1) using MSS + FVG.
*   **Dynamic Position Sizing**: Never risks more than 5% of account balance per trade.
*   **Adaptive Risk:Reward**: Adjusts RR (1:3 to 1:7) based on signal confidence.
*   **S/R Confirmation**: Filters trades using High Volume Support & Resistance levels.

## 🛠️ Setup

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/Hotboy0001/trading_bot.git
    cd trading_bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Setup** (Interactive Configuration):
    ```bash
    python setup.py
    ```
    The setup will ask you to:
    *   Choose between **Real** or **Trial** account
    *   Enter your MT5 login and password
    *   Confirm and save

4.  **Run**:
    ```bash
    python main.py
    ```

## ⚠️ Disclaimer
Trading Forex and Crypto involves significant risk. This bot is for educational purposes. Use at your own risk.
