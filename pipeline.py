import argparse, datetime as dt, json, sqlite3, urllib.request
from pathlib import Path

API = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={}"
def dates(start, end):
    a,b=dt.date.fromisoformat(start),dt.date.fromisoformat(end)
    if b<a: raise ValueError("end must be on or after start")
    while a<=b:
        yield a.isoformat(); a+=dt.timedelta(days=1)
def load(db, payload):
    db.execute("CREATE TABLE IF NOT EXISTS games (game_id INTEGER PRIMARY KEY, game_date TEXT NOT NULL, home TEXT NOT NULL, away TEXT NOT NULL)")
    rows=[]
    for day in payload.get("dates",[]):
        for game in day.get("games",[]):
            rows.append((game["gamePk"],day["date"],game["teams"]["home"]["team"]["name"],game["teams"]["away"]["team"]["name"]))
    db.executemany("INSERT INTO games VALUES (?,?,?,?) ON CONFLICT(game_id) DO UPDATE SET game_date=excluded.game_date,home=excluded.home,away=excluded.away",rows)
    db.commit(); return len(rows)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--start',required=True); p.add_argument('--end',required=True); p.add_argument('--out',default='data'); a=p.parse_args()
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(out/'warehouse.sqlite') as db:
        for day in dates(a.start,a.end):
            with urllib.request.urlopen(API.format(day), timeout=30) as r: payload=json.load(r)
            (out/f'{day}.json').write_text(json.dumps(payload,indent=2))
            print(day,load(db,payload),'games')
if __name__=='__main__': main()
