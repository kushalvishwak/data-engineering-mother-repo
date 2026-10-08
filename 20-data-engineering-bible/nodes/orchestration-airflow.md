---
id: orchestration-airflow
title: Orchestration with Airflow
tier: 1
priority: must-know
sources: [obenner/airflow, obenner/dbt, obenner/system-design, cookbook]
---

# Orchestration with Airflow

## Say it in one line
Airflow is a Python-defined scheduler that runs a DAG of tasks with dependencies, retries, backfills and a UI — it orchestrates work, it does not process the data itself.

## Must be able to recite
- **DAG** — A directed acyclic graph of tasks with dependencies and no cycles; it declares order and nothing about the data itself.
- **Operator vs task vs task instance** — An operator is the template (Bash, Python, SQL, transfer), a task is that operator placed in a DAG, a task instance is one dated run of it.
- **Sensor** — A task that waits for an external condition such as a file or partition; use `reschedule` mode or a deferrable sensor so it does not occupy a worker while waiting.
- **Hook** — A reusable client wrapper for an external system (Postgres, S3, Hive) that operators call, with credentials taken from an Airflow Connection.
- **Executor** — Decides where tasks run: Sequential (one at a time, testing only), Local (parallel on one machine), Celery (fixed worker pool with Redis/RabbitMQ), Kubernetes (one pod per task).
- **Architecture** — Scheduler decides what to run, workers execute, webserver serves the UI, and the metadata database holds every DAG run, task state, connection and variable.
- **Logical date** — The timestamp of the data interval, not the wall clock; the daily run labelled 3 September starts once that interval has ended.
- **catchup and backfill** — `catchup=True` makes the scheduler create every missed run since `start_date`; a backfill re-runs a chosen historical range on demand.
- **XCom** — A small key/value message passed between tasks via the metadata database; push a file path or table name, never a DataFrame.
- **Task idempotency** — Airflow re-runs tasks by design, so each task must be safe to run twice and should write to a deterministic partition.
- **Trigger rules** — Per-task condition on upstream state (`all_success` by default, `all_done`, `one_failed`), which is how you attach cleanup and alert branches.
- **Dynamic DAGs** — Generating DAGs or tasks from configuration in Python at parse time; keep parsing cheap because the scheduler re-parses the files continuously.
- **Dynamic task mapping** — `.expand()` fans a task out into N instances from an upstream list at runtime (Airflow 2.3+); this is the right answer for "an unknown number of files".
- **Pools and concurrency limits** — Pools cap parallel tasks hitting a shared resource, while `max_active_runs` and `max_active_tasks` cap the DAG itself.
- **Airflow 2/3 versus 1** — Airflow 2 added highly available schedulers, the TaskFlow API, separate provider packages, a full REST API and deferrable operators; Airflow 3 adds DAG versioning, a task-execution API so task code never touches the metadata database, assets with event-driven scheduling, and `catchup` off by default.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Explain the Airflow architecture and its components. — Webserver (UI), scheduler (decides what to run, with the executor deciding where), workers (run tasks), and the metadata database holding DAG, run, task, connection and role state (the source lists four components; Airflow 2 also runs a triggerer for deferrable tasks, and Airflow 3 splits out an API server and DAG processor).
- ★ What is a DAG in the context of Airflow or Luigi? — A directed acyclic graph of independent tasks combined into one logical workflow, where the graph shape is the control flow and branches can be taken or skipped.
- ★ What are the executor types and which do you use in production? — Sequential for local testing, Local for development, Celery for a fixed distributed worker pool, Kubernetes for a pod per task with per-task CPU/memory; production is Celery or Kubernetes.
- ★ How do you schedule a DAG? — Pass a cron expression, a timedelta or a preset such as `@daily` (Airflow 2.4+ names the parameter `schedule`, and `schedule_interval` from the source is removed in Airflow 3); Airflow 2.2+ also allows a custom timetable for schedules cron cannot express.
- ★ What are operators, and what is a hook? — Operators are task templates that do one unit of work; hooks are the reusable connection layer to external systems that operators use, so credentials stay in Connections rather than in code.
- ★ What problems does Airflow solve that cron does not? — Dependencies between tasks expressed as Python, retries, backfills, an audit trail of every run, and a UI for state; cron gives you none of that without external scaffolding.
- Why must Airflow tasks be idempotent? — Because Airflow will run a task more than once (retry, backfill, manual clear), so a task must produce the same result each time without unintended side effects.
- What is XCom and how does `xcom_pull` work? — XCom passes small values between tasks; a task pushes explicitly or auto-pushes its return value under `return_value`, and `xcom_pull(task_ids='...')` reads it, optionally by key.
- How do you use XCom inside a Jinja template? — Reference it in the templated field, for example `SELECT * FROM {{ task_instance.xcom_pull(task_ids='foo', key='table_name') }}`.
- What are Jinja templates in Airflow used for? — Rendering runtime values such as the data interval or an upstream XCom into task fields, so one task definition works for every run date.
- How is dbt different from Airflow, and how do they work together? — Airflow schedules and coordinates tasks of any kind; dbt only builds and tests SQL transformations, and in practice Airflow runs dbt as one step between ingestion and publishing.
- Your DAG is scheduled daily at 08:30 — when does the run for 3 September actually execute? — After the 3 September data interval closes, so the run labelled with that logical date starts on 4 September at 08:30; the label is the interval, not the clock (not in sources, but standard).
- How do you backfill three months of history, and what does `catchup` do? — Trigger a bounded backfill over the date range with the tasks written idempotently per partition; `catchup=True` instead makes the scheduler auto-create every missed interval since `start_date` (not in sources, but standard).
- Explain the cron expression `30 8 * * 1-5`. — Minute 30, hour 8, any day of month, any month, Monday to Friday, so 08:30 on weekdays only.
- How do you branch inside a DAG? — Use a branching operator or `@task.branch` that returns the task ids to follow; the unchosen branch is skipped, and downstream joins need a trigger rule such as `none_failed_min_one_success`.
- What are the pros and cons of the CeleryExecutor? — It scales horizontally and replaces dead workers, but needs a Redis/RabbitMQ broker plus a result backend to operate and monitor (the source calls that broker "redundant with what Airflow already supports"; that is wrong — Airflow has no built-in queue).
- What are the pros and cons of the KubernetesExecutor? — Per-task pods give resource isolation, per-task CPU/memory sizing and no idle workers, at the cost of pod start-up latency and Kubernetes operational skill.
- What is wrong with the SequentialExecutor and LocalExecutor in production? — Sequential runs one task at a time and Local runs only on the scheduler's machine, so neither scales and both make that machine a single point of failure.
- How do you make a custom Python module available to Airflow under Docker Compose? — Build a custom image containing the dependency, or mount it onto the `PYTHONPATH` of scheduler and every worker, since all of them import the DAG file.
- How does Airflow resume after the whole system was down? — It restarts from the last unfinished task instance using state in the metadata database, which is why every task must be re-runnable.
- What runs a task — the scheduler or the executor? — The scheduler decides and queues; the executor and its workers actually run the task, which is why worker capacity and not scheduler speed is usually the bottleneck.
- Where are connections, variables and DAG run state stored? — In the metadata database, which the webserver reads for display and the scheduler writes to; losing it loses all run history.
- You must process an unknown number of files that only exists at runtime — how? — Dynamic task mapping with `.expand()` over the upstream file list, giving one task instance per file with independent retries (not in sources, but standard).

## Traps
- Doing the heavy processing inside a PythonOperator on the worker; Airflow should submit work to Spark or the warehouse, not be the compute.
- Using `datetime.now()` or `days_ago()` for `start_date`, which makes the data interval non-deterministic and backfills irreproducible (`days_ago` from the source example is deprecated and gone in Airflow 3).
- Assuming a run labelled 3 September ran on 3 September; the logical date is the start of the interval and execution happens after it ends.
- Pushing DataFrames or files through XCom, which writes them into the metadata database and eventually breaks the scheduler.
- Enabling `catchup` on a DAG whose `start_date` is a year back and flooding the cluster with hundreds of concurrent runs.
- Answering "SubDAG" for grouping; SubDAGs are removed in Airflow 3, so say TaskGroups for structure and dynamic task mapping for fan-out.

## Graph
- **Needs first:** [[pipeline-design]]
- **Leads to:** [[observability]]
- **Asked together with:** [[containers-kubernetes]]
