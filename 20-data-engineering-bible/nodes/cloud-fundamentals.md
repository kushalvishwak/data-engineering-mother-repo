---
id: cloud-fundamentals
title: Cloud Fundamentals
tier: 2
priority: must-know
sources: [obenner/aws, obenner/gcp, obenner/azure, obenner/bigquery, obenner/redshift, cookbook]
---

# Cloud Fundamentals

## Say it in one line
Cloud computing is renting a provider's data centre through an API and paying by the second, so platform capacity follows the workload instead of the workload waiting for capacity.

## Must be able to recite
- **Elasticity** — Capacity is added *and removed* automatically as load changes, so you pay for the workload rather than for its peak.
- **Elasticity vs scalability** — Scalability is the ability to serve a bigger load at all; elasticity is doing it automatically and giving the capacity back afterwards.
- **Vertical scaling (scale up)** — A bigger machine with more CPU and memory; no code change, but it hits a hardware ceiling and usually needs a restart.
- **Horizontal scaling (scale out)** — More machines behind a load balancer; effectively unlimited, but the work must be partitionable.
- **Autoscaling policy** — A rule that resizes a group on a target metric, in fixed steps, on a schedule, or on a forecast; cooldowns and lifecycle hooks stop it thrashing.
- **IaaS / PaaS / SaaS** — IaaS gives VMs, network and disks and you run the OS upward; PaaS runs the platform and you deploy code; SaaS is finished software you only configure.
- **Serverless** — Compute you never provision, size or patch, billed per invocation or per byte processed and able to scale to zero; you trade away cold-start latency, runtime limits and tuning control.
- **Region vs availability zone** — A region is a geography; an AZ is one or more isolated data centres inside it, so multi-AZ survives a data-centre failure and multi-region survives a regional outage.
- **Object vs block vs file storage** — Object is immutable blobs in a flat keyspace over HTTP (cheapest, effectively unlimited); block is a raw volume attached to one VM (lowest latency, for databases); file is a shared POSIX mount.
- **Storage classes** — Standard, Infrequent Access, then Archive; each step is cheaper per GB but adds retrieval fees and a minimum storage duration.
- **Lifecycle policy** — A bucket rule that transitions objects to a colder class or deletes them after N days, so cold data ages down without anyone remembering to do it.
- **Separation of storage and compute** — Data lives in object storage and stateless compute attaches on demand, which is what lets you resize, pause or point several engines at one copy.
- **Shared responsibility model** — The provider secures the infrastructure and the internals of managed services; you secure your data, identities, network configuration and, on IaaS, the OS.
- **IAM** — Identities (users, groups, roles, service accounts) plus least-privilege policies on named resources; pipelines assume a role rather than carrying long-lived keys.
- **VPC** — A logically isolated private network with your own IP ranges, public and private subnets, route tables, and security groups acting as stateful virtual firewalls.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is elasticity? — Capacity is added and removed automatically so supply tracks demand, which means you pay for the workload and not for the peak; the giveaway that you understand it is mentioning the *shrinking back* half (asked in the reader's own interview; the sources ask it as "What is autoscaling?").
- ★ How is elasticity different from scalability? — Scalability is the capability to grow to handle more load; elasticity is that growth happening automatically in both directions without a human resizing anything.
- ★ What is the difference between vertical and horizontal scaling? — Vertical means a bigger machine and is limited by the largest instance type available; horizontal means more machines and requires the workload to be splittable and mostly stateless.
- ★ What is the difference between IaaS, PaaS and SaaS? — IaaS hands you the raw infrastructure (EC2, Azure VMs, Compute Engine); PaaS runs the runtime and you supply code (App Engine, Elastic Beanstalk, Cloud Run); SaaS is a finished application (Office 365, Google Workspace). Each level up removes operational work and control in equal measure.
- ★ What is serverless? — A model where the provider allocates and releases the compute for you and bills per request or per byte processed, so there is nothing to size, patch or leave running idle; BigQuery, Lambda, Cloud Functions, Athena and Glue are the data-side examples.
- ★ What is the relation between an availability zone and a region? — A region is a geographic area containing several AZs, and an AZ is one or more physically separate data centres with independent power and networking. You spread replicas across AZs for availability and across regions for disaster recovery and data residency.
- ★ What is object storage, and how does it differ from block and file storage? — Object storage keeps whole immutable blobs under keys in a flat namespace accessed over HTTP; block storage is a raw disk attached to a single VM; file storage is a shared POSIX filesystem. Data lakes are built on object storage because it scales without limit and decouples from compute.
- ★ What storage classes are available and when do you use each? — Standard for actively queried data, Infrequent Access for data read monthly, Glacier/Archive for compliance retention read a few times a year (the source lists Standard, Standard-IA, Reduced Redundancy and Glacier; that is dated — Reduced Redundancy is deprecated and Intelligent-Tiering, Glacier Instant Retrieval and Deep Archive are the current options).
- ★ What is separation of storage and compute, and why does it matter? — Storage sits in the object store and compute clusters are attached only while needed, so you can resize or pause compute, run several engines on one copy, and stop paying for idle capacity. This is the architectural change that made cloud warehouses elastic.
- ★ What is a VPC? — A logically isolated virtual network inside the provider's cloud with your own IP range, subnets, internet and NAT gateways, route tables and firewall rules, so nothing is publicly reachable unless you say so.
- ★ What is a security group, and how does it differ from a stateless firewall? — A security group is a stateful rule-based virtual firewall, so allowing inbound traffic on a port implicitly allows the reply; a stateless firewall (a network ACL) requires you to write inbound and outbound rules separately.
- ★ What are the advantages of IAM? — Granular, least-privilege permissions per user, group, role and service account on individual resources, plus federated access so applications and external identities get scoped credentials without a permanent key.
- ★ How do you achieve high availability and fault tolerance in the cloud? — Run redundant instances in at least two availability zones behind a load balancer with health checks, and let autoscaling replace what fails (azure.md's "deploy two instances for the SLA" is the old Cloud Services rule; today you use availability zones or the managed service's own SLA).
- ★ How does a cloud provider handle disaster recovery? — Automated backups and snapshots, plus replication across zones and regions, sized by the RTO and RPO you have agreed with the business.
- What are RTO and RPO? — RTO is the maximum acceptable time the service can be down; RPO is the maximum acceptable amount of data you can afford to lose, which sets backup and replication frequency.
- ★ What is autoscaling and what policies can you set? — Rules that add or remove instances to hold a target metric (CPU, queue depth, request count), on fixed steps, on a schedule, or on a prediction; lifecycle hooks add wait time to a scale-in or scale-out event so instances can drain or warm up first.
- What is the difference between on-demand, reserved and spot instances? — On-demand is pay-per-hour with no commitment, reserved commits one to three years for a large discount, spot buys spare capacity at up to ~90% off but can be reclaimed at a few minutes' notice.
- What is the shared responsibility model? — The provider is responsible for security *of* the cloud (hardware, hypervisor, managed-service internals); you are responsible for security *in* the cloud (data classification, IAM, network rules, encryption choices, OS patching on IaaS) (not in sources, but standard).
- ★ How is data encrypted in the cloud? — At rest by default with provider-managed keys and optionally with customer-managed keys in a KMS, and in transit with TLS; the follow-up is always who holds and rotates the key.
- ★ How do you connect an on-premise system to the cloud privately? — A site-to-site VPN over the internet for modest bandwidth, or a dedicated circuit (Direct Connect, Cloud Interconnect, ExpressRoute) plus private endpoints/PrivateLink so traffic never crosses the public internet.
- What is the difference between stopping and terminating an instance? — Stopping shuts the OS down but keeps the persistent volumes, so it can be started again; terminating deletes the instance and, by default, its root volume, and cannot be undone.
- What is the difference between an instance store volume and a network-attached volume (EBS / persistent disk)? — Instance store is local ephemeral disk that is wiped when the instance stops; a network volume has an independent lifecycle, survives the instance and can be snapshotted.
- ★ What consistency models do cloud data stores offer? — Strong consistency guarantees every reader sees the latest write, at the cost of coordination latency; eventual consistency answers faster but a read shortly after a write can be stale.
- ★ How do you monitor cloud resources? — The provider's metrics and logging stack (CloudWatch, Cloud Monitoring, Azure Monitor) with dashboards, alarms on thresholds, and flow logs for network traffic; for data platforms you add freshness and row-count checks on top.
- How do you upload a file larger than 100 MB to object storage? — Multipart upload: split it into parts, upload them independently and in parallel, and let the service assemble the object; it also gives you resumable uploads.
- What are the cloud deployment models? — Public, private, hybrid and community; Indian banks and NBFCs typically run hybrid, keeping regulated data on-premise or in a sovereign region while analytics runs in the public cloud.
- What is edge computing, and how does it differ from cloud and on-premise? — Edge processes data close to where it is produced to cut latency and egress cost; cloud is elastic rented capacity; on-premise is capacity you own and must size for peak.
- What is a key pair used for? — Public/private key authentication to a VM instead of a password, where the private key never leaves your machine.
- How many subnets can you have per VPC? — 200 by default on AWS, and it is a raisable soft quota; the real point of the question is that VPC design is subnet and CIDR design.

## Traps
- Answering "elasticity means it can handle more load" — that is scalability; elasticity is the automatic, two-way version, and interviewers listen specifically for capacity being released again.
- Using "scale up" and "scale out" interchangeably: name them explicitly as bigger box versus more boxes, because the phrasing is what is being scored.
- Treating region and availability zone as the same thing: multi-AZ protects against a data-centre failure, multi-region protects against a regional outage and answers the regulator's data-residency question.
- Saying "serverless means there are no servers": say there are no servers *you* provision, size or patch, and then name the real limits (timeouts, concurrency quotas, cold starts).
- Calling object storage a filesystem: the keyspace is flat, "folders" are just prefixes, and there is no in-place edit — which is exactly why lake jobs are slow at commit time and why rename-based patterns break.
- Claiming the cloud is automatically cheaper: it is cheaper for spiky and short-lived work, and usually more expensive for a flat 24/7 workload unless you buy reserved or committed capacity.

## Graph
- **Needs first:** —
- **Leads to:** [[aws-data-stack]], [[gcp-bigquery]], [[azure-data-stack]]
- **Asked together with:** [[cost-optimization]], [[containers-kubernetes]]
