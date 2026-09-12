with metrics as (

    select * from {{ ref('int_stock_metrics') }}

),

aggregated as (

    select
        ticker,
        min(price_date)                          as start_date,
        max(price_date)                          as end_date,
        count(*)                                 as trading_days,

        min(close_price)                         as min_close,
        max(close_price)                         as max_close,

        (max_by(close_price, price_date)
            / min_by(close_price, price_date) - 1)  as total_return,

        avg(daily_return)                        as avg_daily_return,
        avg(volatility_30d)                      as avg_volatility_30d,

        min(daily_return)                        as worst_day_return,
        max(daily_return)                        as best_day_return

    from metrics
    group by ticker

)

select * from aggregated
order by total_return desc