with prices as (

    select * from {{ ref('stg_stock_prices') }}

),

with_returns as (

    select
        *,
        close_price / lag(close_price) over (
            partition by ticker order by price_date
        ) - 1                                            as daily_return

    from prices

),

with_rolling_metrics as (

    select
        *,

        -- Rolling averages of closing price
        avg(close_price) over (
            partition by ticker order by price_date
            rows between 6 preceding and current row
        )                                                 as sma_7d,

        avg(close_price) over (
            partition by ticker order by price_date
            rows between 29 preceding and current row
        )                                                 as sma_30d,

        -- Volatility: standard deviation of daily return over a 30-day window
        stddev(daily_return) over (
            partition by ticker order by price_date
            rows between 29 preceding and current row
        )                                                 as volatility_30d

    from with_returns

)

select * from with_rolling_metrics