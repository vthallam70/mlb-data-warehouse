{{ config(materialized='table') }}
-- Team dimension keyed on the MLB team id; latest name seen wins.
with appearances as (
  select home_team_id as team_id, home_team as team_name, game_date from {{ ref('stg_games') }}
  union all
  select away_team_id, away_team, game_date from {{ ref('stg_games') }}
)
select team_id, arg_max(team_name, game_date) as team_name,
       min(game_date) as first_game_date, max(game_date) as last_game_date
from appearances
group by team_id
