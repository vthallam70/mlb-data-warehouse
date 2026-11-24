# MLB data warehouse

Daily batch project: `ingest.py` fetches MLB schedules and player box scores into local raw JSON and, when configured, S3. `spark_transform.py` transforms daily schedule data to parquet. dbt builds a DuckDB star schema: an incremental `stg_games` staging model, `dim_teams`, `dim_venues` and `dim_dates` dimensions, and a game-grain `fct_games` fact table, with 28 tests (keys, relationships, accepted values and a custom score check). The Airflow DAG orchestrates daily runs and supports catchup; `backfill.py` rebuilds the warehouse after ingesting any historical range. Player box scores are retained as raw JSON, but only game-level data is currently modeled.

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

### Dimensional model (added Nov 24, 2026)

```
dim_dates (date_key) ─┐
dim_teams (team_id) ──┼── fct_games (game_id; date_key, home_team_id, away_team_id, venue_id,
dim_venues (venue_id) ┘              game_state, scores, home_run_differential, winning_team_id)
```

- Backfill of April 1–14 plus an Airflow run for April 15: 199 games in `fct_games` (195 completed, 4 postponed), 30 teams, 30 venues, 15 dates. `dbt build`: PASS=28.
- A second data-quality catch: MLB reports postponed games with abstract status `Final` and no score. The custom test `assert_completed_games_have_valid_scores` failed on 4 rained-out games, so `stg_games` now derives `game_state` (completed, postponed, scheduled) from the detailed status, and winners and run differentials are computed only for completed games.

Example question the schema answers:

```sql
select t.team_name, count(*) as weekend_wins
from fct_games f
join dim_teams t on t.team_id = f.winning_team_id
join dim_dates d using (date_key)
where d.is_weekend
group by 1 order by 2 desc;
```
