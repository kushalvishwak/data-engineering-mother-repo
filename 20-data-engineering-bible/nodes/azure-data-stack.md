---
id: azure-data-stack
title: Azure Data Stack
tier: 2
priority: should-know
sources: [obenner/azure, cookbook]
---

# Azure Data Stack

## Say it in one line
The Azure data stack is ADLS Gen2 as the lake, Data Factory for movement and orchestration, Databricks or Synapse Spark for processing, a Synapse dedicated SQL pool or Fabric warehouse for serving, and Event Hubs for streams.

## Must be able to recite
- **ADLS Gen2** — Blob Storage with a hierarchical namespace and POSIX-style ACLs turned on, which is what makes directory rename atomic and makes it a lake rather than a bucket.
- **Blob access tiers** — Hot, Cool, Cold and Archive, moved by lifecycle management rules; Archive needs an explicit rehydration that takes hours, so never tier data a pipeline still reads.
- **Block blob vs page blob** — Block blobs are written and committed as whole blocks and are what lakes and backups use; page blobs support random reads and writes and are how VM disks are stored.
- **Azure Data Factory** — The managed copy and orchestration service built from pipelines, activities, datasets, linked services and triggers; Mapping Data Flows are Spark under the covers for no-code transforms.
- **Self-hosted integration runtime** — The agent you install inside the corporate network so ADF can reach an on-premise source through the firewall, which is the piece every bank migration needs.
- **Synapse Analytics** — One workspace over three engines: a dedicated SQL pool (provisioned MPP), a serverless SQL pool (pay per terabyte scanned over the lake) and Spark pools.
- **DWU** — The billing and sizing unit bundling CPU, memory and IO for a dedicated SQL pool; scaling and pausing are explicit actions, and pausing is how you stop paying overnight.
- **Synapse distributions** — HASH to co-locate join keys, ROUND_ROBIN for even spread with no join locality, REPLICATE for small dimensions copied to every node, spread over 60 underlying distributions.
- **COPY INTO / PolyBase** — The parallel bulk-load path from the lake into a dedicated pool; row-by-row INSERT is the standard performance failure in Synapse.
- **Azure Databricks** — First-party managed Spark with Delta Lake and Unity Catalog, and in practice where most Azure transformation work actually happens.
- **Event Hubs** — The managed high-throughput event log with partitions, consumer groups and offsets, exposing a Kafka-protocol endpoint; Event Hubs Capture writes raw events straight into ADLS.
- **Event Hubs vs Service Bus vs Storage Queues** — Event Hubs for telemetry-scale streams, Service Bus for enterprise messaging with topics, ordering, transactions and dead-lettering, Storage Queues for a simple REST work queue.
- **Dead-letter queue** — Where Service Bus parks messages that expired, exceeded the max delivery count or failed a subscription filter; if nobody monitors it, data is lost silently.
- **Microsoft Fabric** — The SaaS repackaging where OneLake (one copy, Delta/Parquet) is the storage and Data Factory, Synapse workloads and Power BI sit on top, with Direct Lake letting Power BI read Delta files without an import.
- **Entra ID and managed identity** — The pipeline authenticates as a managed identity holding RBAC roles on the storage account and workspace, so no keys or connection strings live in code.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What are the service models in cloud computing, and where do Azure services sit? — IaaS is Azure VMs and networking, PaaS is App Service, ADF, Synapse and Event Hubs, SaaS is Office 365 and Fabric; each level up removes operational work and control together.
- ★ What is a blob, and what is the difference between a block blob and a page blob? — A blob is a binary object of any type and size; block blobs are assembled from committed blocks and suit whole-file writes and streaming, page blobs are collections of fixed pages that support random read/write and back VM disks.
- What is Table Storage in Azure? — A schemaless NoSQL key-value store where an entity is addressed by partition key plus row key, entities in the same partition are queried and updated together, and there is no cross-partition transaction — the same design lesson as any wide-column store.
- What is the difference between Azure Storage Queues and Service Bus queues? — Storage Queues are a simple REST get/put/peek queue inside the storage account; Service Bus is the broader messaging layer with publish/subscribe topics, ordering, sessions, transactions and dead-lettering.
- What is a dead-letter queue and when do messages land there? — A sub-queue that receives messages when they expire, when the maximum delivery count is exceeded, or when a subscription filter throws; you monitor and drain it, because it is where silent data loss hides.
- ★ What is autoscaling in Azure, and what is the difference from scaling up? — Scaling out adds instances and scaling up moves to a larger instance size; autoscaling applies rules so instance count follows load automatically, balancing performance against cost.
- How do you scale out compute programmatically? — Through the platform's autoscale rules and management API (the source's answer, the AutoScaling Application Block, belongs to the retired Cloud Services model; today it is VM Scale Sets, AKS autoscaling, Databricks autoscaling or a Synapse pool resize).
- ★ What is the difference between public cloud and private cloud, and what deployment models exist? — Public is shared multi-tenant capacity consumed over the internet, private is dedicated and bounded by your own firewall and administration; the four models are public, private, hybrid and community, and regulated Indian financial firms almost always run hybrid.
- ★ How many instances must you deploy to satisfy the Azure SLA? — Two, in different fault and update domains (this was the Cloud Services rule; the modern equivalent is availability zones or an availability set, and each managed service publishes its own SLA).
- ★ What are the main components of the Azure platform? — Compute, storage and networking, plus identity through Entra ID (the source's "Compute, Storage, AppFabric" is the 2010 answer; AppFabric no longer exists).
- What is ADLS Gen2 and how is it different from Blob Storage? — It is Blob Storage with the hierarchical namespace enabled, which adds real directories, atomic directory rename and POSIX ACLs on top of blob durability and tiering; you enable it at account creation and cannot bolt it on later without migrating (not in sources, but standard).
- When would you use Data Factory, Databricks and Synapse, and how do they fit together? — ADF moves data and orchestrates, Databricks or Synapse Spark transforms it into curated Delta/Parquet tables, and a Synapse SQL pool or Fabric warehouse serves modelled tables to Power BI (not in sources, but standard).
- How does a Synapse dedicated SQL pool distribute data, and how do you choose? — HASH on the fact table's join key so joins stay local, REPLICATE for small dimensions, ROUND_ROBIN for staging tables with no obvious key; a wrong choice shows up as data movement in the query plan (not in sources, but standard).
- ★ What is Windows Azure Diagnostics / how do you collect diagnostic data? — Diagnostic logs and metrics collected from the running service for debugging, performance measurement, capacity planning and auditing; the current service is Azure Monitor with Log Analytics and Application Insights.
- ★ What is the Fabric Controller? — The internal layer that provisions hardware, places and upgrades service instances and restarts what fails; it is an implementation detail of the platform and not something you configure any more.
- What are web roles, worker roles and VM roles? — The three compute roles of the original Cloud Services model: a web role ran IIS for front ends, a worker role ran background processing, a VM role ran a custom OS image. Cloud Services is retired; the modern equivalents are App Service, Functions or AKS for web and background work, and plain VMs for lift-and-shift.
- What is `cspack` and `csrun`? — Command-line tools that packaged a Cloud Services application into a `.cspkg` and ran it against the local compute emulator; both belong to the retired model, and today you deploy with ARM/Bicep, Terraform or the Azure CLI.
- What is a guest OS, and what is the compute emulator? — The operating system running inside the VM that hosts a role instance, and a local emulator used to test before deploying; the modern analogue is a container image plus running the container locally.
- What are the service definition and service configuration files? — The `.csdef` declared the roles, endpoints and instance sizes, and the `.cscfg` supplied the values and instance counts per environment; the current equivalents are ARM/Bicep or Terraform templates plus per-environment parameter files.
- What is a swap deployment (staging and production slots)? — Deploying to a staging slot, verifying it and then swapping it into production for a near-zero-downtime release; App Service deployment slots still work exactly this way.
- What are the instance sizes in Azure? — A ladder of VM sizes trading CPU, memory, local disk and IO throughput (the source's Extra Small to Extra Large table is from 2011; today you pick a family such as D, E or L and a size within it).
- What is minimal versus verbose monitoring? — Minimal collects a small set of platform metrics, verbose adds detailed application and instance counters at higher cost and volume; the trade-off is unchanged in Azure Monitor.
- What are the options for managing session state? — An external store rather than instance memory, so any instance can serve any request; this is the same statelessness requirement that makes horizontal scaling possible for data services.
- Which languages can you use on Azure? — .NET plus Java, Node.js, Python, Go and PHP, and for data work specifically Python and Scala on Databricks/Synapse Spark and T-SQL in the SQL pools.

## Traps
- Answering an Azure question with web roles, worker roles, `cspack` and the Fabric Controller: those describe the pre-2014 platform, and old Indian question banks are full of them, so recognise them and pivot to ADF, Databricks, Synapse and Fabric.
- Calling ADLS Gen2 a separate service from Blob Storage: it is the same service with the hierarchical namespace flag, and the flag can only be set when the account is created.
- Leaving a dedicated SQL pool running overnight: it bills per DWU-hour whether or not anyone queries, so you pause it and use the serverless pool for ad hoc work.
- Loading a dedicated pool with INSERT statements: use COPY INTO or PolyBase from the lake so all 60 distributions load in parallel.
- Calling Event Hubs a queue: it is a partitioned log where consumers track their own offsets and messages expire on retention rather than disappearing on read.
- Presenting Synapse and Fabric as competing choices: Fabric is the newer SaaS packaging of the same engines over OneLake, so a Synapse estate today is a Fabric migration conversation tomorrow.

## Graph
- **Needs first:** [[cloud-fundamentals]]
- **Leads to:** [[warehouse-engines]]
- **Asked together with:** [[pipeline-design]]
