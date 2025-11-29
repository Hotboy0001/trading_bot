# Turtle Soup Trading Bot 🐢

A sophisticated algorithmic trading bot for MetaTrader 5 (MT5) that combines the **Turtle Soup ICT Strategy** with **Support & Resistance Confirmation**.

## 🚀 Features

*   **Multi-Timeframe Analysis**: Scans Higher Timeframes (H4, H2, H1) for major setups.
*   **Precision Entry**: Executes on Lower Timeframes (M15, M5, M1) using MSS + FVG.
*   **Dynamic Risk Management**: Adjusts Risk:Reward (1:3 to 1:7) and Volume based on signal confidence.
*   **S/R Confirmation**: Filters trades using High Volume Support & Resistance levels.

## 🛠️ Setup

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/trading_bot.git
    cd trading_bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    *   Rename `.env.example` to `.env`.
    *   Edit `.env` and add your Exness/MT5 credentials:
        ```text
        MT5_LOGIN=12345678
        MT5_PASSWORD=your_secret_password
        MT5_SERVER=Exness-MT5Trial
        ```

4.  **Run**:
    ```bash
    python main.py
    ```

## ⚠️ Disclaimer
Trading Forex and Crypto involves significant risk. This bot is for educational purposes. Use at your own risk.
