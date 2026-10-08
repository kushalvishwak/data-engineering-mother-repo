# 02 · Python for data engineering

Focus on production Python: explicit schemas, typing, modular design, streaming I/O, API clients, bounded concurrency, logging, configuration, packaging, and tests. Keep transformations deterministic and isolate side effects at boundaries.

## Practical rules

- Parse and validate at system boundaries; represent money/time deliberately.
- Use context managers and iterators for bounded memory. Avoid collecting unbounded data into lists.
- Set connect/read timeouts; retry only safe operations and honor rate limits.
- Keep credentials outside source and logs. Inject configuration rather than reading globals throughout the code.

Exercise: implement a paginated API reader that resumes from a cursor, handles 429/5xx with bounded backoff, detects repeated cursors, and writes records atomically. Test it with a fake transport.

## Runnable example

[`examples/api_client.py`](examples/api_client.py) demonstrates bounded retries, request timeouts, cursor-cycle detection, and injectable transport/sleep functions. Its tests use a fake page reader; they make no network calls. The example yields pages but deliberately does not persist a checkpoint or publish output: a production caller must durably archive a page before advancing its cursor.

```powershell
python -m unittest discover -s 02-python/tests -v
```
