# 08 · AWS data platform

Use S3 as durable object storage and evaluate compute/catalog/query choices such as Glue, Athena, and managed Spark against workload needs. Organize data for pruning and lifecycle management without encoding mutable business logic into opaque paths.

Cover IAM role assumption, bucket policies, KMS, encryption in transit, CloudTrail, VPC endpoints, Glue Catalog, Athena scan cost, and S3 consistency/notification design. Prefer workload roles and scoped policies over long-lived access keys.

Exercise: propose a least-privilege batch pipeline from an external landing bucket to curated Parquet, including quarantine, catalog update, query-cost controls, replay, and lifecycle policy.
