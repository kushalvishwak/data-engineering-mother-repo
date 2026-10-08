FROM --platform=$BUILDPLATFORM apache/airflow:3.3.0-python3.10

RUN pip install --no-cache-dir astronomer-cosmos==1.15.0 \
                               dbt-core==1.12.0 \
                               dbt-postgres==1.11.0 \
                               dbt-bigquery==1.12.0
