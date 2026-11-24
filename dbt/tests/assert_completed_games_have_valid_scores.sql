-- Completed games must have non-negative scores, and a winner unless the game ended tied.
select game_id
from {{ ref('fct_games') }}
where game_state = 'completed'
  and (home_score is null or away_score is null or home_score < 0 or away_score < 0
       or (home_score <> away_score and winning_team_id is null))
