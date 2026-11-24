import argparse, datetime as dt, subprocess, sys
p=argparse.ArgumentParser(); p.add_argument('--start',required=True); p.add_argument('--end',required=True); a=p.parse_args()
day=dt.date.fromisoformat(a.start); end=dt.date.fromisoformat(a.end)
if end<day: p.error('end precedes start')
while day<=end:
 for command in ([sys.executable,'ingest.py','--date',str(day)],[sys.executable,'spark_transform.py','--date',str(day)]): subprocess.run(command,check=True)
 day+=dt.timedelta(days=1)
subprocess.run(['dbt','build','--full-refresh','--profiles-dir','.'],cwd='dbt',check=True)
