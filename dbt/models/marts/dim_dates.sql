{{ config(materialized='table') }}
-- Calendar dimension covering every date in the loaded game range.
with bounds as (select min(game_date) as lo, max(game_date) as hi from {{ ref('stg_games') }}),
spine as (select cast(d as date) as date_day from bounds, generate_series(lo, hi, interval 1 day) as t(d))
select date_day,
       cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
       year(date_day) as year, month(date_day) as month, monthname(date_day) as month_name,
       dayname(date_day) as day_name, isodow(date_day) as iso_day_of_week,
       isodow(date_day) in (6, 7) as is_weekend
from spine
