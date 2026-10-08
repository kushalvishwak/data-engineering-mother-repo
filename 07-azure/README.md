# 07 · Azure data platform

Practice platform design across ADLS Gen2, Azure Data Factory, Azure Synapse, Event Hubs, Blob Storage, and Key Vault. Select services by workload, operational ownership, latency, and existing platform constraints.

Design topics: managed identity and least privilege, private networking, encryption, secret references, storage lifecycle, partition layout, event retention, retry behavior, deployment promotion, and diagnostic routing. Avoid embedding keys in linked service configuration or notebooks.

Exercise: design ingestion of daily files plus order events into a governed lakehouse. Specify identity path, network boundary, replay, schema validation, alert ownership, and cost drivers. Keep resource names and pricing in an environment-specific deployment plan.
