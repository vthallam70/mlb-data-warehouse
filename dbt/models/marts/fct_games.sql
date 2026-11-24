{{ config(materialized='table') }}
-- Game fact table: one row per game, with foreign keys to dim_dates, dim_teams and dim_venues.
select g.game_id,
       d.date_key,
       g.home_team_id, g.away_team_id, g.venue_id,
       g.game_type, g.game_state, g.status_detail, g.day_night,
       g.double_header <> 'N' as is_doubleheader, g.game_number,
       g.home_score, g.away_score,
       case when g.game_state = 'completed' then g.home_score - g.away_score end as home_run_differential,
       case when g.game_state <> 'completed' or g.home_score = g.away_score then null
            when g.home_score > g.away_score then g.home_team_id else g.away_team_id end as winning_team_id
from {{ ref('stg_games') }} g
join {{ ref('dim_dates') }} d on d.date_day = g.game_date
