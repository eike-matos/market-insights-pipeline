with source as (

    select * from {{ source('raw', 'stock_prices_raw') }}

),

renamed as (

    select
        ticker::string                      as ticker,
        date::date                          as price_date,
        open::float                         as open_price,
        high::float                         as high_price,
        low::float                          as low_price,
        close::float                        as close_price,
        volume::number                      as volume

    from source
    where close is not null

)

select * from renamed