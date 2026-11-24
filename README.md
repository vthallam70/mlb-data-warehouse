# MLB data warehouse

Daily batch project: `ingest.py` fetches MLB schedules and player box scores into local raw JSON and, when configured, S3. `spark_transform.py` transforms daily schedule data to parquet. dbt loads an incremental DuckDB games table with uniqueness and non-null tests. The Airflow DAG orchestrates daily runs and supports catchup; `backfill.py` rebuilds the warehouse after ingesting any historical range. Player box scores are retained as raw JSON, but only game records are currently modeled in the warehouse.

```sh
pip install -r requirements.txt
python ingest.py --date 2024-04-01
python spark_transform.py --date 2024-04-01
cd dbt && dbt build --profiles-dir .
# from project root: python backfill.py --start 2024-04-01 --end 2024-04-03
```

For Airflow, set PROJECT_DIR to the absolute project path, add dags/mlb_daily.py to your Airflow DAGs directory, and ensure its environment contains the dependencies and Java needed by Spark. To mirror raw files to S3, configure standard AWS credentials and S3_BUCKET. dbt's incremental model refreshes the most recent seven days; historical changes require the full refresh in the backfill script. API, Spark, Airflow and dbt integration has not been verified in this environment.

## Verified locally (Nov 24, 2026)

- Python 3.12, Java 21, PySpark 3.5.10, dbt-core 1.9 with dbt-duckdb, Apache Airflow 2.10.5 (in its own venv, installed with the official constraints file). No S3 bucket was configured, so the S3 mirror was not exercised.
- `backfill.py --start 2024-04-01 --end 2024-04-14` followed by `airflow dags test mlb_daily 2024-04-15`: all three DAG tasks (ingest, spark_transform, dbt_build) succeeded.
- Warehouse result: 15 schedule days, 203 raw box-score files, 199 unique games in `data/mlb.duckdb`; dbt build PASS=6 (1 model, 5 tests).
- The dbt `unique` test caught postponed games that the MLB schedule lists on both the original and the makeup date with the same `game_id`; `games.sql` now keeps the latest scheduled date per game.
- Notes: dbt is pinned below 1.10 because newer releases download an extra parser from GitHub at install time. If Python reports `CERTIFICATE_VERIFY_FAILED`, set `SSL_CERT_FILE` to `python -c "import certifi; print(certifi.where())"`.
