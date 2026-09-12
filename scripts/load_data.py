"""
Downloads historical stock price data via yfinance and loads it into the
RAW layer of Snowflake using write_pandas for a fast, efficient load.

Usage:
    python scripts/load_data.py
"""

import os

import pandas as pd
import snowflake.connector
import yfinance as yf
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

TICKERS = os.getenv("TICKERS", "AAPL,MSFT,GOOGL,AMZN,NVDA").split(",")
PERIOD = os.getenv("HISTORY_PERIOD", "3y")
DATABASE = os.getenv("SNOWFLAKE_DATABASE", "MARKET_INSIGHTS_PIPELINE")
SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")
TABLE = "STOCK_PRICES_RAW"


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    )


def download_prices(tickers: list[str], period: str) -> pd.DataFrame:
    frames = []

    for ticker in tickers:
        ticker = ticker.strip()
        print(f"Downloading {ticker}...")
        hist = yf.Ticker(ticker).history(period=period)
        hist = hist.reset_index()
        hist["TICKER"] = ticker
        frames.append(hist)

    df = pd.concat(frames, ignore_index=True)

    # Normalize column names for Snowflake
    df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]

    return df


def main():
    df = download_prices(TICKERS, PERIOD)
    print(f"Downloaded {len(df)} rows across {len(TICKERS)} tickers")

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.{SCHEMA}")
        cur.execute(f"USE DATABASE {DATABASE}")
        cur.execute(f"USE SCHEMA {SCHEMA}")

        success, n_chunks, n_rows, _ = write_pandas(
            conn,
            df,
            table_name=TABLE,
            database=DATABASE,
            schema=SCHEMA,
            auto_create_table=True,
            overwrite=True,
            use_logical_type=True,
        )

        print(f"Load complete: success={success}, rows={n_rows}, chunks={n_chunks}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()