{{ config(materialized='table') }}
select venue_id, arg_max(venue_name, game_date) as venue_name, count(*) as games_hosted
from {{ ref('stg_games') }}
group by venue_id
