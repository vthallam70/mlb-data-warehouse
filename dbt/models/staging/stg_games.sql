{{ config(materialized='incremental', unique_key='game_id') }}
-- One row per MLB game from the processed schedule parquet.
-- Postponed games appear on the schedule for both the original and the makeup date under the
-- same game_id; keep the row where the game was completed, else the latest listing.
-- MLB reports postponed/cancelled games with abstract status 'Final', so game_state derives the
-- real outcome from the detailed status.
with source as (
  select cast(game_id as bigint) as game_id, cast(game_date as date) as game_date,
         game_type, cast(season as integer) as season, status, status_detail, day_night,
         double_header, game_number, venue_id, venue_name,
         home_team_id, home_team, away_team_id, away_team,
         cast(home_score as integer) as home_score, cast(away_score as integer) as away_score
  from read_parquet('../data/processed/*/*.parquet', hive_partitioning=true, union_by_name=true)
  where game_id is not null
  {% if is_incremental() %}
    and cast(game_date as date) >= (select coalesce(max(game_date) - interval 7 day, date '1900-01-01') from {{ this }})
  {% endif %}
)
select *,
       case when status_detail in ('Postponed', 'Cancelled') then 'postponed'
            when status = 'Final' then 'completed'
            else 'scheduled' end as game_state
from source
qualify row_number() over (partition by game_id order by (game_state = 'completed') desc, game_date desc) = 1
