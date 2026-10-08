---
id: file-formats
title: File Formats — Parquet, Avro, ORC
tier: 1
priority: must-know
sources: [obenner/avro, obenner/spark, obenner/hive, obenner/hadoop, obenner/greenplum, obenner/redshift, obenner/python, obenner/cost-optimization, devinterview, cookbook]
---

# File Formats — Parquet, Avro, ORC

## Say it in one line
A file format decides how records are laid out in bytes: row-oriented formats like Avro write and read whole records cheaply, while columnar formats like Parquet and ORC let an analytical query read only the columns and row groups it actually needs.

## Must be able to recite
- **Row-oriented** — keeps all fields of one record together, so appends and whole-record reads are cheap, but any query pays to read every column.
- **Columnar** — keeps each column's values contiguously, so a query touching 3 of 200 columns reads a fraction of the bytes and compresses far better because neighbouring values share a type and often a value.
- **Hybrid (PAX) layout** — Parquet and ORC are not purely columnar: they cut rows into row groups first and store columns within a group, which is exactly what keeps one large file splittable across a cluster.
- **Row group** — a horizontal slice of a Parquet file (commonly 128 MB) and the unit of read parallelism; ORC calls the equivalent a stripe.
- **Column chunk and page** — a column chunk is one column inside one row group and is the unit compression and column pruning act on; it splits into roughly 1 MB pages, the smallest unit a reader can decode or skip.
- **Footer statistics** — Parquet writes the schema plus per-row-group min, max and null count at the *end* of the file, which is why readers seek the footer first and why a truncated tail destroys the whole file.
- **Predicate pushdown** — the engine hands the filter to the reader, which tests it against row-group and page statistics and skips those that cannot match, without decompressing them.
- **Projection pushdown** — the reader fetches only the named column chunks; this is the single biggest win of Parquet over CSV and it vanishes the moment you write `SELECT *`.
- **Dictionary encoding** — repeated values in a column chunk become small integer codes plus one dictionary, so low-cardinality columns cost almost nothing; the writer falls back to plain encoding once the dictionary exceeds its size limit.
- **RLE and bit-packing** — runs of identical values (and Parquet's definition/repetition levels) collapse into counts and are packed into the minimum number of bits, so most of the size reduction happens before any codec runs.
- **Avro** — a row-oriented binary format that embeds its full JSON schema in the file header, so any language can decode the file with no external registry and no manually assigned field IDs.
- **Avro schema resolution** — reader and writer schemas are matched by field *name* using defaults, so adding a field with a default or dropping a defaulted field is compatible, while a rename without an alias is a breaking change.
- **ORC** — Hive's native columnar format: stripes, lightweight indexes and optional bloom filters inside the file, one output file per task, and historically the only format with Hive ACID support.
- **Splittability** — a worker must be able to start reading mid-file; Avro, Parquet and ORC compress per internal block so they split under any codec, whereas a gzipped CSV is one indivisible stream and gets one task.
- **Codec trade-off** — snappy is fast and the historical default, zstd gives roughly 20–40% smaller files at comparable CPU and is now the better default, gzip is for cold archives, lzo is effectively dead.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a Parquet file and what does it buy you? — A columnar format: the reader fetches only the columns named in the query and skips row groups whose statistics cannot match the filter, so scanned bytes, I/O and storage all drop.
- ★ What is the difference between a row store and a column store? — Row stores keep a whole record together and win on point lookups and inserts (OLTP); column stores keep a column together and win on aggregations over a few columns across many rows (OLAP).
- ★ How does predicate pushdown work? — The filter is pushed down into the reader or the source database so rows are eliminated before they cross the network; in Parquet the reader compares the predicate against row-group and page min/max statistics and skips what cannot match.
- ★ What file formats can you use in Hadoop or a data lake? — Text (CSV, TSV, JSON), SequenceFile, Avro, Parquet and ORC; production analytics tables are Parquet or ORC, while ingestion and streaming payloads are usually Avro or JSON.
- ★ How does schema evolution work in Avro? — The file carries the writer's schema and the reader supplies its own; Avro resolves them field by field using defaults, so old data can be read with a new schema and new data with an old one.
- ★ Why do we need serialisation, and what is Avro's advantage over Hadoop Writables? — Serialisation turns in-memory objects into bytes for the network or disk; Writables and SequenceFiles have a Java-only API, whereas Avro is readable from any language and carries its own schema.
- ★ Is the file splittable, and why does that matter? — Splittable means several tasks can read one file in parallel; Avro, Parquet and ORC compress per internal block so they split under any codec, while a single gzipped CSV forces one task and destroys parallelism.
- ★ What is ORC and why is it used in Hive? — Optimised Row Columnar: a columnar Hive format that emits one file per task (easing NameNode load), stores lightweight indexes and metadata in the file, supports complex types, and bounds read/write memory.
- What is Apache Avro? — A language-neutral serialisation system that stores data in compact binary form with the schema declared in JSON, used both for container files and for RPC.
- When would you prefer Avro over Parquet? — For streaming, ingest and transport, where you write record by record, consume whole records, and want the schema to travel with the data; Parquet only pays off once you are scanning columns of a large table.
- Why is CSV or JSON a poor choice for a large analytics table? — No embedded types, no statistics, no column pruning, expensive text parsing, and gzipped text is not splittable, so you pay to read every byte of every column.
- How does a columnar format achieve such good compression? — Values in one column share a type and often repeat, so dictionary encoding, run-length encoding and bit-packing shrink them before a codec such as snappy or zstd is applied at all.
- Which data types does Avro support? — Primitives (null, boolean, int, long, float, double, bytes, string) and six complex types: record, enum, array, map, union and fixed.
- How does Avro compare with Thrift and Protocol Buffers? — All three are compact cross-language binary formats, but Thrift and Protobuf need an IDL, generated code and assigned field numbers, whereas Avro can work dynamically from the schema shipped with the data.
- What are the disadvantages of Avro? — You cannot read or write a single byte without a schema, it is not human-readable, serialisation can be slower, and it gives you no column pruning for analytics.
- What is the difference between an HDFS block and an input split? — A block is a physical storage chunk on disk; a split is a logical unit of work handed to one mapper, and split boundaries follow record boundaries rather than block boundaries.
- What is `isSplitable()` and when would you set it to false? — It is the InputFormat flag deciding whether Hadoop may cut a file into splits; you set it false for data where a partial read is meaningless, so the whole file goes to one mapper.
- What is a SequenceFile? — Hadoop's older splittable binary key–value container, used mainly to pass data between MapReduce jobs; superseded by Avro for interchange and Parquet/ORC for analytics.
- Can a warehouse query Parquet or Avro files in place? — Yes, through external tables and lake engines: Redshift Spectrum over S3, BigQuery external tables, Greenplum external tables, Hive and Trino over HDFS or object storage.
- What happens if you write one small file per record or per micro-batch? — You hit the small-files problem: planning and metadata dominate, statistics become useless, compression has nothing to work with; target a few hundred MB per file and compact.
- What is a sort order in Avro? — Avro defines a standard ordering for every type so data written by one system can be sorted or compared by another without deserialising into objects.
- How do you read and write Parquet efficiently from Python? — Use pyarrow, select only the columns you need, write reasonably sized row groups and files, avoid thousands of tiny files, and move to a distributed engine once the data outgrows one machine.
- What are row groups, column chunks and pages in Parquet? — Rows are cut into row groups, each row group holds one column chunk per column, and each chunk is a sequence of pages; statistics exist at all three levels so readers skip work at the right granularity. (not in sources, but standard)
- How do you choose between snappy, gzip, zstd and lzo? — Snappy or zstd for hot analytics data (zstd for a better ratio at similar CPU), gzip only for cold archives, lzo is legacy; on columnar formats splittability does not enter the decision because compression is per block. (not in sources, but standard)
- What does the Parquet footer contain and why is it written last? — Schema, row-group offsets and per-column statistics, which are only known once all data has been written; readers therefore seek to the end of the file before reading any data. (not in sources, but standard)

## Traps
- Saying "Parquet is faster" with no mechanism. The interviewer wants two words: column pruning and row-group skipping via statistics.
- Calling Parquet a pure column store. It is row groups of column chunks, and that hybrid layout is precisely why one large file remains splittable.
- Assuming predicate pushdown always helps. Min/max statistics only skip data when the filter column correlates with physical order, so an unsorted high-cardinality filter still reads everything — that is what sorting and clustering are for.
- Concluding "gzip is not splittable, therefore Parquet+gzip is not splittable". Compression inside Parquet is per page, so the file still splits at row-group boundaries.
- Recommending Avro for the curated warehouse layer, or Parquet for a Kafka topic. The line is row-oriented for ingest and transport, columnar for analytical scans.
- Answering "Avro supports schema evolution" and stopping. State the rule: matching is by field name with defaults, so a new field without a default breaks old readers and a rename without an alias breaks everything.

## Graph
- **Needs first:** —
- **Leads to:** [[partitioning-layout]], [[table-formats-lakehouse]]
- **Asked together with:** [[spark-tuning]]
