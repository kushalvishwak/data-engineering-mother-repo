# AWS interview practice

## How would you control Athena query cost?

**Short answer:** reduce scanned bytes through columnar formats, partition/filter design, compression, and workgroup limits, while measuring actual scans.

**Deep explanation:** partitioning should match common selective predicates without creating excessive small partitions. Parquet projection and predicate pruning help only when queries and metadata support them. Enforce workgroup budgets/output location and monitor scan metrics.

**Example:** store curated events as compressed Parquet partitioned by a low-cardinality date key used by most queries; benchmark before adding secondary layout complexity.

**Common mistake:** partitioning by a unique identifier and creating huge numbers of tiny objects.

**Senior follow-up:** when is a different engine warranted? When concurrency, latency, transformation, governance, or cost requirements cannot be met with current query patterns; compare measured workloads.

## How do you grant S3 access safely?

**Short answer:** use assumed workload roles and narrowly scoped identity/resource policies with encryption and audit controls.

**Deep explanation:** evaluate IAM policy, bucket policy, KMS key policy, network conditions, and object ownership together. Avoid long-lived access keys, wildcard resources, and unreviewed cross-account trust.

**Example:** a Glue job role gets read access to a landing prefix and write access only to its curated output prefix.

**Common mistake:** broad bucket-wide grants that unintentionally expose raw sensitive data.

**Senior follow-up:** how do you verify least privilege? Exercise allow/deny cases, inspect CloudTrail access, and review effective permissions and role assumption boundaries.
