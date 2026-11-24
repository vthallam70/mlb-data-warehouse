"""Normalize raw MLB schedules into partitioned parquet; reruns replace each date."""
import argparse
from pathlib import Path
from pyspark.sql import SparkSession, functions as F
p=argparse.ArgumentParser(); p.add_argument('--date',required=True); p.add_argument('--raw',default='data/raw'); p.add_argument('--output',default='data/processed'); a=p.parse_args()
spark=SparkSession.builder.appName('mlb-schedule').getOrCreate()
source=str(Path(a.raw)/'schedule'/f'{a.date}.json')
df=spark.read.option('multiLine','true').json(source)
games=df.select(F.explode('dates').alias('day')).select(F.col('day.date').alias('game_date'),F.explode('day.games').alias('game'))
result=games.select('game_date',F.col('game.gamePk').alias('game_id'),F.col('game.teams.home.team.name').alias('home_team'),F.col('game.teams.away.team.name').alias('away_team'),F.col('game.teams.home.score').alias('home_score'),F.col('game.teams.away.score').alias('away_score'))
result.write.mode('overwrite').parquet(str(Path(a.output)/f'game_date={a.date}'))
spark.stop()
