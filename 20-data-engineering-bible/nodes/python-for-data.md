---
id: python-for-data
title: Python for Data Engineering
tier: 4
priority: must-know
sources: [obenner/python.md, devinterview, cookbook]
---

# Python for Data Engineering

## Say it in one line
Python is the glue of a data platform — it extracts, reshapes, orchestrates and tests, while the heavy compute is pushed down to SQL engines or Spark.

## Must be able to recite
- **Mutable vs immutable** — lists, dicts and sets can be changed in place; tuples, strings, ints and frozensets cannot, so only immutable objects are safe as dict keys or default arguments.
- **Comprehension** — a single expression that builds a list, dict or set from an iterable, faster than an append loop and the idiomatic way to filter or dedupe (`{r.id for r in rows}`).
- **Generator vs list** — a generator yields one item at a time and holds one row in memory while a list materialises everything, and because anything with `__iter__`/`__next__` works in a `for` loop, file handles, DB cursors and `read_csv(chunksize=...)` all stream the same way.
- **Decorator** — a function that wraps another function to add behaviour without editing it, used for retries, timing and logging on pipeline tasks.
- **Context manager** — `with` guarantees setup and teardown via `__enter__`/`__exit__`, so files, connections and Spark sessions close even when the body raises.
- **`*args` / `**kwargs`** — `*args` collects extra positional arguments as a tuple, `**kwargs` collects extra keyword arguments as a dict; both let a wrapper pass arguments through blindly.
- **Shallow vs deep copy** — `copy.copy` copies the outer container and shares the inner objects, `copy.deepcopy` recursively copies everything, so a shallow copy of a nested config still leaks mutations.
- **GIL** — CPython lets only one thread execute bytecode at a time, so threads and asyncio help IO-bound work (APIs, disk, DB) while CPU-bound work needs `multiprocessing` or native libraries that release the lock.
- **Virtual environment and pinning** — an isolated interpreter plus a lockfile with exact versions and hashes; without pinning, the same code builds differently in CI and production.
- **merge vs join vs concat** — `merge` joins on columns (SQL-style), `join` is the same on the index, `concat` stacks frames along an axis with no key matching; using `concat` where you meant `merge` silently produces nulls.
- **groupby-agg** — `groupby(keys).agg(...)` collapses to one row per key; `transform` returns a value per original row, which is the pandas equivalent of a window function.
- **apply vs vectorised** — `apply` and `iterrows` run a Python loop per row, vectorised operations run in C over the whole column, usually one to two orders of magnitude faster.
- **Chunked reads and dtypes** — `read_csv(chunksize=..., usecols=..., dtype=...)` bounds memory; declaring `category` and small int types instead of inferred `object`/`int64` often halves the footprint.
- **pandas vs PySpark** — pandas is single-machine and limited by RAM, PySpark distributes over a cluster and is lazy; the switch point is roughly when the data no longer fits in memory with room to spare.
- **Structured logging** — log JSON with a run id, table name and input/output row counts at INFO, errors with context, and never secrets or PII.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Why is Python used so heavily in data engineering when the compute runs elsewhere? — Because it is productive glue for extraction, transformation, orchestration and integration, and every engine exposes a Python client; the heavy lifting still happens in Spark or the warehouse.
- ★ How would you process a 50 GB CSV on a machine with 16 GB of RAM? — Stream it in chunks or line by line, select only the columns you need, write results incrementally, and convert to Parquet or move to a distributed engine if this becomes routine.
- ★ How do iterators and generators help with large data? — They stream data instead of materialising it, so memory stays flat and long ETL jobs stop dying on large inputs.
- ★ What is the GIL and why does it matter? — It permits one thread of Python bytecode at a time, so threading gives no CPU speedup; most pipeline work is IO-bound, which is why threads still help there.
- Threads, multiprocessing or async IO — when do you use each? — Threads or asyncio for IO-bound fan-out such as hundreds of API calls, multiprocessing for CPU-bound work such as parsing or compression, and neither if the right answer is to push the work into SQL or Spark.
- ★ How do you implement retries with exponential backoff? — Retry only transient errors (timeouts, 429, 5xx) with a doubling delay plus jitter, cap the total attempts and elapsed time, and make the write idempotent so a retry cannot duplicate rows.
- ★ How do you test data transformations in Python? — Small fixture inputs with asserted golden outputs, property tests for invariants such as uniqueness and non-negative amounts, and separate integration tests for real connectors and schemas.
- ★ What logging and monitoring practices matter in a pipeline? — Structured logs carrying run id, source, row counts in and out, and timings, shipped somewhere searchable, with alerts on failure and on row-count anomalies rather than only on exceptions.
- ★ How do you ensure data quality inside a Python job? — Assert contracts at the boundary (not-null keys, ranges, uniqueness, row counts), fail loudly or quarantine bad rows, and record the check results rather than just logging them.
- How do you manage dependencies and reproducible environments? — Pin every dependency in a lockfile, pin the Python version, isolate with a virtualenv or container image, and have CI build from the same definition as production.
- How do you structure a Python project for pipelines? — Separate reusable library code from thin job entrypoints, keep configuration out of code, inject external clients so they can be faked, and standardise logging and error handling in one place.
- How do you profile and optimise slow Python code? — Profile first to find the hotspot, then vectorise, cut data copies, choose better structures, or offload to a native or distributed engine; optimise only what the profile shows.
- How do you read and write Parquet efficiently in Python? — Use `pyarrow`, project only the columns you need, write reasonably sized row groups and files, and avoid producing thousands of tiny files.
- How do you clean data with pandas? — `dropna`/`fillna` for missing values, `drop_duplicates` for repeats, explicit `astype` casting, plus outlier and range handling; the point is that every step is explicit and testable.
- Write the skeleton of an ETL job that pulls a REST API and loads a table. — `requests.get(url).json()` into `pd.DataFrame`, cast types and `drop_duplicates` in a pure transform function, then `to_sql` or a bulk copy through SQLAlchemy in a separate load function.
- How would you optimise a slow SQL query issued from a Python ETL job? — Read the execution plan, index or partition for the predicate, simplify joins and subqueries, refresh statistics, and cache or materialise repeated results; the fix is in the database, not the Python.
- Explain immutability and which Python types are immutable. — An immutable object cannot change after creation (`str`, `tuple`, `int`, `frozenset`); it makes objects hashable and safe to share across threads and cached calls.
- What is the difference between `*args` and `**kwargs`? — `*args` is a tuple of extra positional arguments, `**kwargs` is a dict of extra keyword arguments; use them for pass-through wrappers, not to avoid declaring a real signature.
- What is the difference between an object and a class? — A class is the template describing state and behaviour, an object is one instance of it with its own data.
- What is the difference between a library, a framework and a package? — A package is a distributable unit of modules, a library is code you call, a framework calls your code and dictates the structure.
- OOP or functional style for transformation code? — Prefer pure functions taking and returning DataFrames because they are trivially testable; use classes for stateful things like clients and connections.
- merge vs join vs concat in pandas? — `merge` matches on columns, `join` matches on the index, `concat` glues frames together without matching keys. *(not in sources, but standard)*
- What is a decorator, and what is a context manager? — A decorator wraps a function to add cross-cutting behaviour such as retry or timing; a context manager guarantees cleanup around a block with `with`. *(not in sources, but standard)*
- Shallow vs deep copy? — Shallow copies the container and shares nested objects, deep copies the whole tree; mutating a shallow copy's nested dict changes the original. *(not in sources, but standard)*

## Traps
- Reaching for `apply`, `iterrows` or a Python loop when a vectorised column expression or a `groupby` would do — interviewers treat this as the single tell of a weak pandas user.
- Answering "how do you handle big data in Python" with pandas alone; state the RAM ceiling and name the exit (chunking, Parquet, Spark, or pushing the aggregation into SQL).
- Using threads for CPU-bound work — the GIL means no speedup; say `multiprocessing` or a native library.
- Mutable default arguments (`def f(rows=[])`) — the list is created once and shared across calls; default to `None` and build inside.
- Bare `except:` that swallows the error, and `print` instead of `logging` — both hide failures from the orchestrator and from the on-call engineer.
- An unpinned `requirements.txt`; say lockfile plus pinned Python version, otherwise the honest answer is "it works on my machine".

## Graph
- **Needs first:** —
- **Leads to:** [[pipeline-design]], [[dsa-coding]]
- **Asked together with:** [[apis-rest]], [[linux-shell]]
