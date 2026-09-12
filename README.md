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

## Running with Docker

Instead of setting up a local Python environment, you can run everything inside a container:

\`\`\`bash
docker compose build
docker compose up -d
docker compose exec pipeline bash
\`\`\`

Once inside the container:

\`\`\`bash
python scripts/load_data.py
dbt run
dbt test
python scripts/generate_commentary.py
\`\`\`

Note: you still need `~/.dbt/profiles.yml` configured on your host machine — it gets
mounted read-only into the container.
