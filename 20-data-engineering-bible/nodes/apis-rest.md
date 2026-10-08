---
id: apis-rest
title: APIs and REST for Ingestion
tier: 4
priority: should-know
sources: [obenner/python.md, obenner/hbase.md, obenner/system-design.md, obenner/cdc.md, devinterview, cookbook]
---

# APIs and REST for Ingestion

## Say it in one line
A REST API is a stateless, resource-oriented interface over HTTP — and to a data engineer it is a source that paginates, rate-limits, fails halfway and changes its schema without telling you.

## Must be able to recite
- **REST** — Representational State Transfer: resources addressed by URI, manipulated with standard HTTP methods, with the representation (usually JSON) separate from the resource itself.
- **Stateless** — every request carries everything the server needs, so no session is held between calls, which is what lets you retry a request and scale servers horizontally.
- **HTTP verbs** — `GET` reads, `POST` creates, `PUT` replaces, `PATCH` partially updates, `DELETE` removes; `GET` is also safe, meaning it must not change state.
- **Status codes** — 2xx success (200 OK, 201 Created, 204 No Content), 3xx redirect, 4xx your fault (400, 401, 403, 404, 409, 429), 5xx their fault (500, 502, 503, 504).
- **Idempotency** — the same request applied repeatedly leaves the same end state; `GET`, `PUT` and `DELETE` are idempotent, `POST` is not, which is why retried POSTs need an idempotency key.
- **Headers** — `Content-Type` and `Accept` negotiate format, `Authorization` carries the credential, `ETag`/`If-None-Match` enable conditional reads, `Retry-After` tells you how long to wait.
- **Auth** — an API key is a shared static token, Basic auth is base64 user:password, OAuth2 exchanges a client credential for a short-lived access token, and a JWT is a signed self-contained token carrying claims.
- **Pagination** — offset/limit and page/size are simple but drift when rows are being inserted; cursor or keyset pagination passes an opaque pointer to the last row and is the safe choice for large or live datasets.
- **Rate limiting and backoff** — the server caps requests per window and answers 429 when you exceed it; respect `Retry-After`, otherwise back off exponentially with jitter and cap total attempts.
- **Webhook vs polling** — polling means you ask repeatedly and mostly get nothing, a webhook means the provider POSTs to your endpoint when an event happens; webhooks are lower latency but need a public, authenticated, idempotent receiver.
- **REST vs SOAP** — REST is an architectural style over plain HTTP with JSON, SOAP is a protocol with XML envelopes and built-in standards for security and transactions; banks still run plenty of SOAP internally.
- **GraphQL vs gRPC** — GraphQL gives the client one endpoint and a query language so it fetches exactly the fields it needs, gRPC uses HTTP/2 with binary protobuf and generated stubs for fast service-to-service calls.
- **API gateway** — a single entry point in front of backend services handling routing, authentication, rate limiting, logging and protocol translation.
- **Versioning and schema drift** — versions go in the path (`/v1/…`), a query parameter or an `Accept` header; drift is handled by landing the raw payload, treating new fields as additive and alerting on removals rather than crashing.
- **Checkpointing** — store the high-water mark (last cursor, last `updated_at`, last page) with the write, so the next run resumes rather than repeating or skipping.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What does REST mean? — Representational State Transfer: a stateless style where resources are addressed by URI and acted on with standard HTTP methods, allowing generic clients and multiple message formats.
- ★ What is idempotency, and which HTTP methods are idempotent? — An operation whose repetition does not change the outcome; `GET`, `PUT` and `DELETE` are idempotent, `POST` is not because each call can create another resource.
- ★ How do you make API ingestion idempotent so retries do not duplicate rows? — Write with a deterministic key (natural key plus source version or event id) using upsert or merge, keep the raw landing zone append-only and rebuild derived tables from it, and commit the checkpoint together with the data.
- ★ What are the main HTTP status codes you would handle in a pipeline? — 200/201 success, 400 fix the request, 401/403 fix credentials or permissions, 404 gone or wrong path, 409 conflict, 429 back off, 5xx retry with backoff.
- ★ How do you handle pagination? — Offset/limit, page/size, or cursor-based; loop until an empty page or a null next-cursor, and prefer cursor pagination because offsets shift when the underlying data changes mid-pull.
- ★ What is rate limiting and throttling, and why do APIs do it? — A cap on requests per client per window, enforced to stop abuse, ensure fair use and protect the backend; the client's job is to stay under it and respect 429 rather than hammer through it.
- ★ How do you implement retries with exponential backoff? — Retry only transient failures (timeouts, 429, 5xx) with a doubling delay plus random jitter to avoid a thundering herd, cap the attempts and total time, and send everything that still fails to a dead-letter store.
- ★ How do you secure an API? — Authenticate (OAuth2, JWT or keys), authorise per action, force HTTPS, validate and sanitise input, rate limit, and log usage so abuse is visible.
- ★ How do you handle authentication and authorisation as a consumer? — Authentication proves who you are, authorisation decides what you may do; keep the credential in a secret manager, refresh OAuth2 tokens before expiry, and never commit it or log it.
- ★ What is a webhook, and how does it differ from calling an endpoint? — With a webhook the provider pushes to your URL when an event occurs instead of you polling; you must return quickly, verify the signature, and deduplicate because delivery is at-least-once.
- ★ What is an API and how does it work? — A contract of methods and data formats through which one system requests data or actions from another, usually over HTTP with a defined request and response shape.
- ★ REST versus SOAP — what is the difference? — REST is stateless, uses HTTP verbs and typically JSON; SOAP is an XML envelope protocol with built-in security and transaction standards and a WSDL contract, and is heavier.
- What are the principles of a RESTful service? — Statelessness, client-server separation, cacheable responses, and a uniform interface where resources are identified by URI and acted on by standard methods.
- What are the types of APIs? — Public/open, internal/private, partner, and composite (one call that fans out to several underlying requests).
- Write the extraction step for a pipeline that ingests a REST API. — `requests.get(url, headers=auth, params=page)` in a retry loop, page until exhausted, write the raw JSON to object storage, then transform to a DataFrame and load; keep extract, transform and load as separate functions so each is testable.
- ★ How do you handle schema changes from an API source? — Land the raw payload untouched, treat new fields as additive, validate against an expected schema and alert on removals or type changes, and use a format with schema evolution such as Avro or Parquet for the curated layer.
- How do you handle partial failures and late data in an API pull? — Checkpoint per page or per partition, make writes idempotent so the failed slice can be replayed, keep a dead-letter queue for records that never parse, and re-run affected partitions rather than the whole history.
- What is an API gateway and why is it used? — A single front door that routes requests to backend services and centralises authentication, rate limiting, logging, monitoring and request transformation.
- How is API versioning managed? — In the URI path (`/v1/resource`), as a query parameter, or via a content-negotiation header; the point is that old clients keep working while the new shape ships.
- Synchronous versus asynchronous API calls? — A synchronous call blocks until the response arrives; an asynchronous call returns immediately and the result is handled later via a callback, a poll or `async`/`await`, which is how you fan out thousands of requests.
- What is CORS and when does it matter? — A browser rule restricting requests to a different origin than the page; it is the server's `Access-Control-Allow-Origin` policy, and it never affects a server-side pipeline call.
- What is HATEOAS? — Responses carry hypermedia links to the actions available next, so a client can navigate without hard-coding URLs; almost no real API you ingest implements it fully.
- What should API documentation contain, and what tools do you use? — Purpose, auth, endpoints and methods, request and response shapes, error codes, examples, and rate limits — usually published as OpenAPI/Swagger and exercised with Postman or Insomnia.
- What are common REST frameworks? — Jersey and Spring on the JVM (as the source names), and FastAPI or Flask in Python, which is what you would actually write a small internal data API in.
- REST, GraphQL or gRPC — which would you choose to ingest from? — REST for breadth of support and cacheable, simple pulls; GraphQL when you need a few fields out of a deep object and want to avoid N calls; gRPC for high-volume internal service traffic where the schema is fixed and latency matters. *(not in sources, but standard)*
- The API has no `updated_at` and no cursor — how do you pull incrementally? — Fall back to a full pull with a hash or key-based diff against the previous snapshot, or pull by an immutable partition such as event date; state clearly that without a change marker you are trading cost for correctness. *(not in sources, but standard)*
- You must pull 10 million rows from a paginated API every night in a two-hour window — how? — Partition the keyspace or date range and pull in parallel within the rate limit, checkpoint each partition independently, write raw pages straight to object storage, and only then transform; a single sequential cursor loop cannot be parallelised or resumed cheaply. *(not in sources, but standard)*

## Traps
- Treating 429 as a failure and killing the run. It is a "slow down" instruction — honour `Retry-After`, back off with jitter, and design the schedule to fit inside the quota.
- Retrying a `POST` without an idempotency key. The first call may have succeeded before the timeout, so the retry creates a duplicate; use a client-generated key or an upsert on a deterministic key.
- Offset pagination against data that is being written. Rows shift between pages, so you silently skip and duplicate records; use a cursor or freeze on an immutable ordering.
- Landing only the flattened, parsed result. Keep the raw response so you can replay a bad transform without re-hitting the API, which may not even let you back that far.
- Assuming HTTP 200 means success. Plenty of APIs return an error object with a 200, so validate the payload shape and the record count, not just the status line.
- Credentials in code, notebooks or logs. Read them from a secret manager or environment, and redact tokens in any logged request.

## Graph
- **Needs first:** —
- **Leads to:** [[pipeline-design]]
- **Asked together with:** [[python-for-data]]
