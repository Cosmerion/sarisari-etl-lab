# Sari-sari sales ETL lab

**Source note:** The course module and its original CSV were not available locally. The included 16-line starter CSV and schema are a compatible, newly authored recreation, **not** the module's original sample. The worksheet is a draft until you capture actual runs on this machine.

## Requirements

Docker Desktop with a working WSL 2 backend; Docker Compose v2.14+; about 4 GB free RAM; Git Bash or PowerShell. The only preparation for the stack itself is creating `.env` from `.env.example`. Do not commit `.env`.

```bash
cd sarisari-etl-lab
cp .env.example .env                # PowerShell: Copy-Item .env.example .env
# Replace the five example secrets/user values in .env.
docker compose version
docker run --rm hello-world
# Run hello-world again to show that the image is now cached.
docker compose up -d
docker compose ps                   # five long-running services; airflow-init exited 0
```

Airflow: http://localhost:8080; log in with `ADMIN_USER` and `ADMIN_PASSWORD` from `.env`. Allow time for the scheduler to discover `sarisari_sales_etl`; open the DAG and **Trigger DAG**. Each trigger snapshots available landing CSVs under `datalake/raw/<run_id>/` and stages `datalake/staged/<run_id>/sales.parquet`. The raw bytes are not altered. Airflow TaskFlow passes only paths through XCom. `airflow-init` migrates metadata and creates the admin account, then exits. The other five services are the metadata DB, warehouse DB, webserver, scheduler, and triggerer.

### Checkpoints 1–7: original batch

**Before adding exercise 1**, keep `data/exercise1/sales_2026-10b.csv` outside `data/landing`. Trigger twice. Both runs should be green, and the first transform log should say `Rows in: 16, rows kept: 13, rejected: 3`. Use the following queries and capture your own terminal with its prompt or the Airflow URL:

```bash
docker compose exec -T warehouse psql -U warehouse -d sarisari -c 'SELECT count(*) AS fact_rows FROM dw.fact_sales;'
docker compose exec -T warehouse psql -U warehouse -d sarisari -c 'SELECT s.store_name, sum(f.line_total) AS sales_php FROM dw.fact_sales f JOIN dw.dim_store s USING (store_key) GROUP BY s.store_name ORDER BY s.store_name;'
docker compose exec -T warehouse psql -U warehouse -d sarisari -c 'SELECT sum(line_total) AS grand_total_php FROM dw.fact_sales;'
find datalake -type f                # in Git Bash (one raw CSV + one Parquet per initial run)
```

Starter totals should be Aling Nena PHP 456, Mang Ben PHP 253, Kuya Jo PHP 328; grand total PHP 1,037. These figures are derived from **this project's** CSV, not from a live database until you verify them.

### Checkpoint 8: new store and two rejected rows

```bash
cp data/exercise1/sales_2026-10b.csv data/landing/sales_2026-10b.csv
# PowerShell: Copy-Item data/exercise1/sales_2026-10b.csv data/landing/sales_2026-10b.csv
```

Trigger a NEW run. The new CSV has eight data lines: six valid, S022 with an empty price, and a second S018 with a duplicate sale_id. Expected transform log: `Rows in: 24, rows kept: 19, rejected: 5` (includes the starter batch's three rejects). Query:

```bash
docker compose exec -T warehouse psql -U warehouse -d sarisari -c 'SELECT store_name, barangay FROM dw.dim_store ORDER BY store_name;'
docker compose exec -T warehouse psql -U warehouse -d sarisari -c "SELECT count(*) AS original_13, sum(line_total) AS original_php FROM dw.fact_sales WHERE sale_id IN ('S001','S002','S003','S004','S005','S006','S007','S008','S009','S010','S011','S012','S013');"
docker compose exec -T warehouse psql -U warehouse -d sarisari -c 'SELECT count(*) AS fact_rows FROM dw.fact_sales;'
```

Expect four stores, original 13 totaling PHP 1,037, and 19 facts. Take screenshots of the transform log and dimension query on this machine.

### Checkpoint 9: fail the fifth rule, then fix it

The fifth `quality_check` rule is `unit_price <= PHP 10,000`. Append **one new validly formed but overpriced** sale to `data/landing/sales_2026-10b.csv`:

```text
S023,2026-10-17,Tindahan ni Ramon,Barangay San Isidro,Premium Rice,Groceries,1,12000.00
```

Trigger a NEW run. The first four quality checks should pass and `quality_check` should turn red with `QUALITY CHECK FAILED: unit_price under or equal to PHP 10000`. Screenshot its **red task and log** while it is still visible. Edit **that same S023 line** to `...,1,120.00`, then trigger another NEW run. Screenshot the green run and passing quality log. An upsert corrects the S023 warehouse row; no old raw snapshot is modified. Final expected counts are four stores and 20 facts; the original 13 are unchanged. Note that the failing run has already committed its bad row because `quality_check` runs after `load`: it prevents a green DAG run, not ingestion. In production, place the check before publishing to consumers or add a quarantine/transactional publication step.

## Developer checks and submission

With local `pandas` and `pyarrow` installed, `python -m unittest discover -s tests -v` checks rejection counts, raw retry behavior, temporary staged Parquet, and fifth-rule failure/pass without Docker. It does **not** prove that Docker, Airflow, or PostgreSQL ran. The Docker image already has pandas, pyarrow, and psycopg2 for live runs.

Use `worksheet/` for your own screenshots and finished PDF, and fill in the name/section. If you publish the Git project, `git status --ignored` should show that `.env`, `logs/`, and all `datalake/` contents are ignored. Create a remote on your own Git account and paste its actual URL into the LMS comment; none is configured here.
