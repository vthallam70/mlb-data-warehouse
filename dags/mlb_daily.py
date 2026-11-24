"""Airflow daily schedule; use catchup for backfills."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
with DAG('mlb_daily',start_date=datetime(2024,1,1),schedule='@daily',catchup=True,max_active_runs=1) as dag:
 ingest=BashOperator(task_id='ingest',bash_command='cd "$PROJECT_DIR" && python ingest.py --date {{ ds }}')
 transform=BashOperator(task_id='spark_transform',bash_command='cd "$PROJECT_DIR" && python spark_transform.py --date {{ ds }}')
 warehouse=BashOperator(task_id='dbt_build',bash_command='cd "$PROJECT_DIR/dbt" && dbt build --profiles-dir .')
 ingest >> transform >> warehouse
