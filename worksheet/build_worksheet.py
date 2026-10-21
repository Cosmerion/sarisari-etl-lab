"""Fill the supplied worksheet with an honest draft; screenshots must be real."""
from datetime import date
from pathlib import Path
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path.home() / 'Downloads' / 'Student Lab Worksheet.docx'
OUTPUT = ROOT / 'worksheet' / 'Tuazon_Ramon_ETL-Lab_DRAFT.docx'

doc = Document(TEMPLATE)
doc.tables[0].cell(1, 0).text = 'Ramon Tuazon [confirm name]'
doc.tables[0].cell(1, 1).text = '[add section]'
doc.tables[0].cell(1, 2).text = str(date.today())

content = [
    (
        'Docker is not installed on this Windows installation, so this checkpoint cannot yet be supported by the required terminal screenshot. I prepared a Compose project in compose.yaml and a Dockerfile based on Airflow 2.10.5, but neither file proves that the daemon starts. After enabling WSL 2 and Docker Desktop, I need to run docker compose version and docker run --rm hello-world twice in my own terminal. Only a live output that includes the client version and the greeting can verify the setup; until then, this evidence is pending.',
        'On the first run Docker may download hello-world because its image is absent from the local image cache. On the second run the image is already cached, so the pull notice should not appear. This needs confirmation in the checkpoint 1 terminal screenshot.',
    ),
    (
        'I defined five persistent services in compose.yaml: an Airflow metadata PostgreSQL database, a separate warehouse PostgreSQL database, the webserver, the scheduler, and the triggerer. airflow-init waits for both database health checks, migrates Airflow metadata, and creates an administrator before the webserver and scheduler start. It is a one-shot initialization service, so it should exit successfully instead of remaining in the list of running services. Since Docker is unavailable here, I have not seen a real docker compose ps result and must capture that result after installing the runtime.',
        'The Airflow database stores scheduling metadata, task states, users, and logs-related state; the warehouse stores business facts and dimensions. Separating them makes backups, permissions, performance tuning, and warehouse resets safer without disrupting the scheduler. The screenshot must show both database health states.',
    ),
    (
        'I wrote dags/sarisari_sales_etl.py with four TaskFlow tasks named extract, transform, load, and quality_check. The expression check_task().set_upstream(load_task(transform_task(extract_task()))) establishes the dependency chain: passing each earlier task output to the next creates three arrows, and set_upstream creates the final load-to-quality_check arrow. extract and transform exchange only paths; the actual CSV and Parquet data are stored in the mounted data lake. The Graph view at localhost:8080 still needs to be captured after a successful run; a Python syntax check alone cannot establish green task states.',
        'Airflow XCom is a metadata channel, not bulk storage. Passing a small file path is cheaper and less fragile than serializing a pandas DataFrame into the metadata database; the downstream task reads the file from the shared volume. The Graph screenshot should show the four-task order.',
    ),
    (
        'The starter data/landing/sales_2026-10.csv contains 16 data lines. The local parser test in tests/test_pipeline.py confirms 13 clean records and three rejections, but the actual Airflow transform log still needs a screenshot. S014 has a missing price, the second S005 duplicates a sale_id, and S015 has a negative quantity. dags/pipeline.py rejects these cases, logs each file name, line number, and reason, and summarizes the counts as Rows in: 16, rows kept: 13, rejected: 3. The test is useful supporting evidence, not a replacement for the requested task log.',
        'For a real store, I would quarantine rejected lines when the cost of losing a sale is high or when staff need to correct source data later. A quarantine table would preserve the original row, batch, rejection reason, and time without allowing bad rows into dw.fact_sales.',
    ),
    (
        'The extract function copies each landing CSV byte-for-byte into datalake/raw under a run-specific directory and refuses to overwrite a changed raw file on a retry. The transform function validates receipt lines and writes only accepted records to datalake/staged under a matching run directory as sales.parquet. These are two different data-lake zones: raw is source evidence, while staged is clean, columnar input for loading. A local test checks raw-copy behavior and writes and reads a temporary Parquet file. It does not establish an Airflow-managed lake listing; a terminal screenshot of find datalake -type f is still required.',
        'Keeping raw input makes the pipeline auditable and replayable: if the business rules change, I can rebuild the staged file and warehouse from the unchanged source. It also helps investigate whether a bad total came from a store export or a later transformation.',
    ),
    (
        'The warehouse schema in sql/01_schema.sql defines store and product dimensions with surrogate keys and a sales fact whose grain is one unique sale_id receipt line. Based on the 13 valid starter CSV rows, my independent calculation yields Aling Nena PHP 456, Mang Ben PHP 253, and Kuya Jo PHP 328. Their sum is PHP 1,037. Those are calculated expectations, not a claimed PostgreSQL result: I must run the row-count, grouped-sales, and grand-total queries in README.md against the actual warehouse and capture their output. If the numbers differ, I will investigate before submission.',
        'A customer or basket dimension, with anonymized buyer or receipt identifiers, would help distinguish many independent Sunday rice purchases from one large basket. The current receipt-line grain can show date and quantity, but without a buyer or basket key it cannot reliably distinguish those explanations.',
    ),
    (
        'The SQL fact table gives sale_id a UNIQUE constraint. The load function inserts dimensions using their natural-key uniqueness and inserts facts with ON CONFLICT (sale_id) DO UPDATE only when a fact actually changes. These are the two load protections against repeated dimensions and repeated receipt lines. The local test checks that retrying extraction keeps the same raw bytes, but it does not test actual database re-runs. I still need two successful Airflow Grid runs and a second row-count query showing 13 fact rows to demonstrate end-to-end idempotency as the worksheet requires.',
        'Without the UNIQUE constraint, the ON CONFLICT (sale_id) clause would not be valid in PostgreSQL and the load would fail rather than silently triple the counts. If both uniqueness and the conflict clause were removed, three full loads would create 39 fact rows and triple each store total.',
    ),
    (
        'I prepared data/exercise1/sales_2026-10b.csv with eight lines from Tindahan ni Ramon in Barangay San Isidro. Six lines are valid. S022 has no unit_price, and a second S018 repeats a sale_id; the shared transform rejects both and logs their reasons. The local parser test confirms 19 accepted and five rejected across both batches, including the starter batch’s three rejections. After copying the exercise CSV into data/landing and triggering a live run, the expected warehouse has four stores and 19 facts, with the first 13 totaling PHP 1,037. These database results and log lines still need screenshots.',
        'A missing price is more plausible than a repeated entire receipt line because manual encoding or an incomplete price list can leave a blank cell. I would require price entry and a valid numeric amount in the point-of-sale form before exporting the batch; the transform check remains a backup.',
    ),
    (
        'I added a fifth quality_check assertion in dags/pipeline.py requiring every unit_price to be at most PHP 10,000. To demonstrate it, append S023 to the exercise landing CSV at PHP 12,000, trigger a new DAG run, then change that same sale_id to PHP 120 and trigger another new run. The local unit test uses a fake database response to confirm the check raises and then passes, but no red or green Airflow task is claimed here. The failed run’s load would already have committed S023; the correcting upsert repairs it on the next run. Both real screenshots are mandatory.',
        'For this lab, a failed check should mark the DAG red and alert the owner, because a price above PHP 10,000 probably indicates an entry error. Since this check runs after load, it does not undo the insert; a production design should block publication or quarantine before consumers see it. The store owner and data owner should agree on the threshold and decide which failures stop delivery versus alert only.',
    ),
]

for number, (explanation, discussion) in enumerate(content, start=1):
    words = len(explanation.split())
    assert 50 <= words <= 150, (number, words)
    base = 1 + (number - 1) * 3
    if number == 9:
        for index, state in [(25, 'FAILED'), (26, 'FIXED')]:
            doc.tables[index].cell(1, 0).text = (
                f'[REAL {state} SCREENSHOT REQUIRED: Airflow URL and task log/status visible. '
                'Do not submit this placeholder.]')
        base = 27
    else:
        doc.tables[base].cell(1, 0).text = (
            '[REAL SCREENSHOT REQUIRED: capture this checkpoint on your own machine, '
            'showing your username/terminal prompt or Airflow URL. Do not submit this placeholder.]')
    doc.tables[base + (0 if number == 9 else 1)].cell(1, 0).text = explanation
    doc.tables[base + (1 if number == 9 else 2)].cell(1, 0).text = discussion

header = doc.paragraphs[0]
notice = header.insert_paragraph_before('DRAFT — NOT SUBMISSION READY: real screenshots, name, section, live Docker runs and Git URL still required.')
notice.runs[0].bold = True
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
print('explanation word counts:', [len(text.split()) for text, _ in content])
