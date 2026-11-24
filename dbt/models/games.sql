{{ config(materialized='incremental', unique_key='game_id') }}
-- Postponed games appear on the schedule for both the original and the makeup date
-- under the same game_id; keep the latest scheduled date (when the game was played).
with source as (
  select cast(game_id as bigint) as game_id, cast(game_date as date) as game_date,
         home_team, away_team, cast(home_score as integer) as home_score, cast(away_score as integer) as away_score
  from read_parquet('../data/processed/*/*.parquet', hive_partitioning=true)
  where game_id is not null
  {% if is_incremental() %}
    and cast(game_date as date) >= (select coalesce(max(game_date) - interval 7 day, date '1900-01-01') from {{ this }})
  {% endif %}
)
select * from source
qualify row_number() over (partition by game_id order by game_date desc) = 1
