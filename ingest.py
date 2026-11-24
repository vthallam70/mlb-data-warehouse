"""Fetch MLB daily schedule and boxscores to local storage or an S3 bucket."""
import argparse, datetime as dt, json, os, urllib.request
from pathlib import Path
BASE='https://statsapi.mlb.com/api/v1'
def fetch(path):
 with urllib.request.urlopen(BASE+path, timeout=30) as response: return json.load(response)
def store(key, obj):
 data=json.dumps(obj).encode()
 if os.getenv('S3_BUCKET'):
  import boto3
  boto3.client('s3').put_object(Bucket=os.environ['S3_BUCKET'],Key=key,Body=data,ContentType='application/json')
 path=Path(os.getenv('RAW_DIR','data/raw'))/key; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
def run(day):
 dt.date.fromisoformat(day)
 schedule=fetch('/schedule?sportId=1&date='+day); store(f'schedule/{day}.json',schedule)
 for group in schedule.get('dates',[]):
  for game in group.get('games',[]):
   game_id=game['gamePk']; store(f'boxscores/{day}/{game_id}.json',fetch(f'/game/{game_id}/boxscore'))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--date',required=True); run(p.parse_args().date)
