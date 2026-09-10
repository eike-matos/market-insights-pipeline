# Market Insights Pipeline

Data pipeline that ingests historical stock price data, computes financial metrics
(returns, volatility, drawdown) with **dbt**, and generates automated natural-language
commentary using **Snowflake Cortex AI** (Snowflake's native LLM functions).

> Project under construction — full details coming as features are added.

## Stack

- Snowflake (warehouse + Cortex AI)
- dbt (dbt-snowflake)
- Python + yfinance (market data ingestion)
- Docker (reproducible environment)

## Branching

Workflow: `users/<username>/<feature>` → `dev` → `main`, following Conventional Commits.
