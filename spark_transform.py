"""Normalize raw MLB schedules into partitioned parquet; reruns replace each date."""
import argparse
from pathlib import Path
from pyspark.sql import SparkSession, functions as F
p=argparse.ArgumentParser(); p.add_argument('--date',required=True); p.add_argument('--raw',default='data/raw'); p.add_argument('--output',default='data/processed'); a=p.parse_args()
spark=SparkSession.builder.appName('mlb-schedule').getOrCreate()
source=str(Path(a.raw)/'schedule'/f'{a.date}.json')
df=spark.read.option('multiLine','true').json(source)
games=df.select(F.explode('dates').alias('day')).select(F.col('day.date').alias('game_date'),F.explode('day.games').alias('game'))
def col(path, alias, dtype='string'):
 # optional fields (e.g. scores of postponed games) may be absent from a day's inferred schema
 try:
  games.select(F.col(path)).schema
  return F.col(path).cast(dtype).alias(alias)
 except Exception:
  return F.lit(None).cast(dtype).alias(alias)
result=games.select('game_date',
 F.col('game.gamePk').alias('game_id'),
 col('game.gameType','game_type'), col('game.season','season'),
 col('game.status.abstractGameState','status'), col('game.status.detailedState','status_detail'),
 col('game.dayNight','day_night'), col('game.doubleHeader','double_header'), col('game.gameNumber','game_number','int'),
 col('game.venue.id','venue_id','int'), col('game.venue.name','venue_name'),
 col('game.teams.home.team.id','home_team_id','int'), F.col('game.teams.home.team.name').alias('home_team'),
 col('game.teams.away.team.id','away_team_id','int'), F.col('game.teams.away.team.name').alias('away_team'),
 col('game.teams.home.score','home_score','int'), col('game.teams.away.score','away_score','int'))
result.write.mode('overwrite').parquet(str(Path(a.output)/f'game_date={a.date}'))
spark.stop()
