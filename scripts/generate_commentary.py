"""
Reads the aggregated stock performance metrics from Snowflake, sends each
ticker's numbers to Groq's LLM API to generate a short analyst-style
commentary, and writes the results back into Snowflake as a new table.
"""

import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from groq import Groq
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

DATABASE = os.getenv("SNOWFLAKE_DATABASE", "MARKET_INSIGHTS_PIPELINE")
SOURCE_SCHEMA = "RAW_MARTS"
SOURCE_TABLE = "FCT_STOCK_PERFORMANCE"
TARGET_SCHEMA = "ENRICHED"
TARGET_TABLE = "STOCK_COMMENTARY"

MODEL = "openai/gpt-oss-120b"


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    )


def fetch_performance(conn) -> pd.DataFrame:
    query = f"""
        select *
        from {DATABASE}.{SOURCE_SCHEMA}.{SOURCE_TABLE}
    """
    cur = conn.cursor()
    cur.execute(query)
    return cur.fetch_pandas_all()


def build_prompt(row: pd.Series) -> str:
    return (
        "You are a financial analyst. In up to 2 sentences, comment on this "
        f"stock's performance based on the following data: total return of "
        f"{row['TOTAL_RETURN'] * 100:.2f}%, average daily return of "
        f"{row['AVG_DAILY_RETURN'] * 100:.4f}%, average 30-day volatility of "
        f"{row['AVG_VOLATILITY_30D'] * 100:.2f}%, worst day of "
        f"{row['WORST_DAY_RETURN'] * 100:.2f}%, best day of "
        f"{row['BEST_DAY_RETURN'] * 100:.2f}%. Be direct and objective."
    )


def generate_commentary(client: Groq, df: pd.DataFrame) -> pd.DataFrame:
    comments = []

    for _, row in df.iterrows():
        print(f"Generating commentary for {row['TICKER']}...")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": build_prompt(row)}],
            temperature=0.3,
            max_tokens=150,
        )

        comments.append(response.choices[0].message.content.strip())

    df = df.copy()
    df["AI_COMMENTARY"] = comments
    return df[["TICKER", "AI_COMMENTARY"]]


def main():
    conn = get_connection()

    try:
        performance_df = fetch_performance(conn)
        print(f"Loaded {len(performance_df)} tickers from {SOURCE_TABLE}")

        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        commentary_df = generate_commentary(client, performance_df)

        cur = conn.cursor()
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.{TARGET_SCHEMA}")

        success, n_chunks, n_rows, _ = write_pandas(
            conn,
            commentary_df,
            table_name=TARGET_TABLE,
            database=DATABASE,
            schema=TARGET_SCHEMA,
            auto_create_table=True,
            overwrite=True,
        )

        print(f"Load complete: success={success}, rows={n_rows}, chunks={n_chunks}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()