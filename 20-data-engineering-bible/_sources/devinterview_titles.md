# Devinterview "Top 100" — coverage checklist

The GitHub README for this source publishes only 15 of its 100 questions. The rest are on
devinterview.io with the answers gated; the **question titles** for items 1–69 are readable and
are listed below (normalised phrasing, not verbatim). Items 70–100 were not retrievable.

Answers are not reproduced here — they are gated. Each row instead points at the node in this
knowledgebase that answers it. Use this as a self-test index: cover the node column, read the
question, say the answer.

| # | Question | Answered in |
|---|---|---|
| 1 | What is data modeling and why does it matter | [[relational-modeling]] |
| 2 | Conceptual vs logical vs physical data models | [[relational-modeling]] |
| 3 | Key steps in the data modeling process | [[relational-modeling]] |
| 4 | Relationship types in a relational database | [[relational-modeling]] |
| 5 | Normalization and its role in database design | [[relational-modeling]] |
| 6 | OLTP vs OLAP systems | [[oltp-vs-olap]] |
| 7 | Star schema and when to use it | [[dimensional-modeling]] |
| 8 | Slowly changing dimensions | [[scd-history]] |
| 9 | Fact table vs dimension table | [[dimensional-modeling]] |
| 10 | Purpose of surrogate keys | [[dimensional-modeling]] · [[relational-modeling]] |
| 11 | Data warehouse and its key characteristics | [[warehouse-architecture]] |
| 12 | The ETL process and its stages | [[etl-vs-elt]] |
| 13 | Common ETL challenges | [[pipeline-design]] |
| 14 | Full load vs incremental load | [[pipeline-design]] |
| 15 | Data staging and why it matters | [[warehouse-architecture]] |
| 16 | Data lineage and its significance | [[data-governance]] |
| 17 | Benefits of a data warehouse | [[warehouse-architecture]] |
| 18 | Data quality's role in ETL | [[data-quality]] |
| 19 | Handling SCDs in ETL | [[scd-history]] · [[dbt-transformations]] |
| 20 | Data warehouse vs data mart | [[warehouse-architecture]] |
| 21 | Hadoop and its core components | [[hadoop-hdfs]] |
| 22 | Hadoop vs Spark | [[spark-core]] · [[mapreduce]] |
| 23 | MapReduce and how it works | [[mapreduce]] |
| 24 | HDFS's role in Hadoop | [[hadoop-hdfs]] |
| 25 | Hive in big data processing | [[hive-impala]] |
| 26 | Data partitioning in Hadoop | [[partitioning-layout]] |
| 27 | Kafka and its data engineering use cases | [[kafka-messaging]] |
| 28 | Batch vs stream processing | [[batch-vs-streaming]] |
| 29 | Cassandra and its key features | [[nosql-stores]] |
| 30 | Data replication in Hadoop | [[hadoop-hdfs]] · [[distributed-systems]] |
| 31 | Data processing and its stages | [[pipeline-design]] |
| 32 | Batch vs real-time processing | [[batch-vs-streaming]] |
| 33 | Common data transformation techniques | [[etl-vs-elt]] · [[dbt-transformations]] |
| 34 | Data cleansing's role | [[data-quality]] |
| 35 | Data enrichment and its importance | [[etl-vs-elt]] |
| 36 | Data aggregation and use cases | [[sql-aggregation]] |
| 37 | Data deduplication and how it is done | [[sql-query-patterns]] · [[batch-vs-streaming]] |
| 38 | Data filtering vs data sorting | [[sql-semantics]] |
| 39 | Data normalization as a transformation | [[relational-modeling]] |
| 40 | Purpose of data validation | [[data-quality]] |
| 41 | Data integration and its challenges | [[pipeline-design]] |
| 42 | ETL vs ELT | [[etl-vs-elt]] |
| 43 | Common data integration patterns | [[pipeline-design]] |
| 44 | Role of data pipelines | [[pipeline-design]] |
| 45 | Data lake vs data warehouse | [[warehouse-architecture]] · [[table-formats-lakehouse]] |
| 46 | Data ingestion and its methods | [[cdc-ingestion]] · [[pipeline-design]] |
| 47 | Change data capture and use cases | [[cdc-ingestion]] |
| 48 | Batch vs streaming integration | [[batch-vs-streaming]] |
| 49 | Data replication techniques | [[distributed-systems]] |
| 50 | Data orchestration in pipelines | [[orchestration-airflow]] |
| 51 | DBMS and its types | [[oltp-vs-olap]] |
| 52 | SQL vs NoSQL databases | [[nosql-stores]] |
| 53 | Data partitioning strategies | [[partitioning-layout]] |
| 54 | Data indexing and its benefits | [[sql-performance-indexing]] |
| 55 | Data sharding and when to use it | [[distributed-systems]] |
| 56 | Vertical vs horizontal scaling | [[cloud-fundamentals]] |
| 57 | Data replication types | [[distributed-systems]] |
| 58 | Caching in data retrieval | [[distributed-systems]] · [[warehouse-engines]] |
| 59 | Data lake architecture | [[table-formats-lakehouse]] |
| 60 | Data archiving and its importance | [[cost-optimization]] · [[data-governance]] |
| 61 | Data governance and its key components | [[data-governance]] |
| 62 | Data governance vs data management | [[data-governance]] |
| 63 | Common data governance frameworks | [[data-governance]] |
| 64 | Data lineage's role in governance | [[data-governance]] |
| 65 | Data quality and its dimensions | [[data-quality]] |
| 66 | Data stewardship and its responsibilities | [[data-governance]] |
| 67 | Data security best practices | [[data-governance]] |
| 68 | Authentication vs authorization | [[data-governance]] |
| 69 | Data encryption and its types | [[data-governance]] |

Coverage: all 69 retrievable titles map onto existing nodes — the taxonomy needed no additions.
Items 70–100 are unknown; judging by the section pattern they continue into governance, security
and cloud, which nodes 61–69 and the Tier-2 cloud nodes already cover.

