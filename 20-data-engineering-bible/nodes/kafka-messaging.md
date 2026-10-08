---
id: kafka-messaging
title: Kafka and Message Queues
tier: 1
priority: should-know
sources: [obenner/kafka, obenner/flume, obenner/flink, obenner/cdc, obenner/data-quality, cookbook]
---

# Kafka and Message Queues

## Say it in one line
Kafka is a distributed, partitioned, replicated commit log: producers append to topic partitions, each consumer reads at its own offset, and records stay for a configured retention so they can be replayed.

## Must be able to recite
- **Topic and partition** — A topic is a named stream split into partitions; the partition is the unit of ordering, parallelism and storage.
- **Offset** — The monotonic position of a record inside a partition; consumers track it, so reading is a pointer move rather than a removal.
- **Broker** — A server in the cluster holding partitions and serving all reads and writes; adding brokers is how the cluster scales out.
- **Key to partition** — The producer hashes the key to choose a partition, so the same key always lands in the same partition and keeps its order; with no key you get round-robin and no order.
- **Consumer group** — Consumers sharing a group id, where each partition is assigned to exactly one member; one group behaves like a queue, several groups each get the whole topic like pub/sub.
- **Rebalancing** — Partitions are reassigned when a member joins, leaves or times out; the pause is why you keep the poll loop short and prefer cooperative sticky assignment.
- **Leader and follower** — Each partition has one leader serving reads and writes plus followers that replicate it, and a follower is promoted if the leader dies.
- **ISR and acks** — In-sync replicas are followers caught up within `replica.lag.time.max.ms`; `acks=all` with `min.insync.replicas=2` means a write is acknowledged only once enough in-sync replicas hold it.
- **Retention** — Records are deleted by age or size (`retention.ms`, `retention.bytes`) regardless of whether anyone read them, so a slow consumer plus short retention equals data loss.
- **Log compaction** — Keeps only the newest value per key so the topic becomes a changelog snapshot; a null value is a tombstone that removes the key.
- **Idempotent producer** — `enable.idempotence=true` makes retried sends deduplicate per partition using a producer id and sequence number.
- **Transactions** — A `transactional.id` with begin/commit/abort gives atomic writes across partitions, and consumers must read with `isolation.level=read_committed` to benefit.
- **Consumer lag** — Log end offset minus committed offset per partition; it is the single metric that tells you whether consumption is keeping up.
- **Kafka Connect** — A worker framework of source and sink connectors (JDBC, Debezium, S3, Elasticsearch) with managed offsets and converters, so ingestion needs configuration rather than code.
- **Schema registry** — A central store of Avro/Protobuf/JSON schemas with compatibility rules (backward, forward, full) enforced when producing, which is what stops a producer breaking every consumer.

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ What is a topic, and what are partitions for? — A topic is a stream of messages of the same type; partitions split it so it can be spread over brokers and consumed in parallel, and each partition is independently ordered.
- ★ What is a consumer group, and how does Kafka give both queueing and publish-subscribe? — Within a group each partition goes to exactly one consumer, which is queue behaviour; adding another group gives it an independent copy of the whole topic, which is publish-subscribe.
- ★ How do you guarantee ordering or FIFO in Kafka? — Order exists only within a partition, so send everything that must stay ordered with the same key (usually the entity id) and keep that key's partition count fixed.
- ★ What is ISR, and when does a broker leave it? — In-sync replicas have replicated everything the leader has acknowledged; a replica leaves when it falls behind `replica.lag.time.max.ms`, when its broker fails, or on manual removal (the source also cites `replica.lag.max.messages`, which was removed years ago — only the time-based setting exists now).
- ★ How do you get exactly-once when producing to Kafka? — Enable producer idempotence, use the transactional API with a `transactional.id` and begin/commit/abort, set `acks=all` with retries, and have consumers read `read_committed`.
- ★ What is the role of the offset? — It uniquely identifies a record's position in a partition and is what consumers commit, so they resume exactly where they stopped after a restart or failure.
- ★ What is ZooKeeper's role, and can Kafka run without it? — ZooKeeper historically held cluster metadata and ran leader election; KRaft replaces it with a built-in Raft quorum and is now the default, and ZooKeeper support was removed in Kafka 4.0.
- ★ What are brokers, and what is the purpose of replication? — Brokers are the servers storing partitions and serving traffic; replication copies each partition to several brokers so a broker loss costs neither availability nor data.
- ★ What is Kafka and what is it used for? — A distributed, partitioned, replicated log used as a durable buffer and transport between producers and consumers, giving high throughput, decoupling and replay.
- ★ What are the benefits of Kafka over a traditional message queue? — Horizontal scale-out, disk-based batched throughput, replication for durability, producer/consumer decoupling, and replay from retained history, which classic queues lose on consumption.
- ★ What is a schema registry and which compatibility mode do you pick? — A central schema store enforcing a compatibility policy at produce time; backward compatibility (new schema can read old data) is the usual default so consumers can upgrade after producers.
- How are messages consumed — push or pull? — Pull: the consumer polls the broker, reads in partition order and tracks its own offset, which is what makes replay and per-consumer pacing possible.
- How do you know whether all messages in a topic have been consumed? — Compare the log end offset with the group's committed offset per partition; zero lag on every partition means fully consumed.
- What is a producer, and what does the Producer API do? — It publishes records to topics, choosing the partition by key, batching for throughput and returning the offset metadata for each acknowledged send (the source's SyncProducer/AsyncProducer split is from the old Scala client; the modern Java producer is asynchronous with a `Future`/callback).
- How do you define a partitioning key? — Set the key on the record; the default partitioner hashes it to a partition id, and a custom partitioner is only needed for deliberate placement such as tenant isolation.
- How do you increase throughput for a slow or remote consumer? — Add partitions and consumers to raise parallelism, increase fetch and batch sizes, compress, use an efficient serialisation format, and process outside the poll loop.
- What happens if the preferred replica is not in the ISR? — It cannot be made leader without risking data loss, so leadership stays elsewhere until it catches up; forcing it means an unclean election and dropped records.
- How do you reduce ISR churn? — Stabilise the network between brokers, tune `replica.lag.time.max.ms`, make sure no broker is starved of CPU, memory or disk I/O, and separate replication traffic where possible.
- What does it mean if a replica stays out of the ISR for a long time? — It cannot keep up with the leader because of network, hardware or load problems, so it neither counts towards acknowledgement nor can be promoted, which weakens durability.
- What is the maximum message size Kafka accepts? — About 1 MB by default, controlled by the broker's `message.max.bytes` and the topic's `max.message.bytes`; raise both plus consumer fetch size, or store the payload externally and send a reference.
- Can you get a message's offset after producing it? — Yes, the producer's acknowledgement returns metadata including the partition and offset.
- When does the producer raise a queue-full error? — When the application sends faster than the broker and the client's buffer fills; the fix is more brokers or partitions, or slowing/batching the producer, not a bigger buffer alone.
- What is the difference between Kafka, Storm and Flink? — Kafka is transport and storage, Storm is record-at-a-time compute, Flink is a stateful stream processor with event-time semantics that also does batch.
- What are the similarities and differences between Flume and Kafka? — Both move event data reliably, but Flume pushes to configured sinks in a source-channel-sink agent, while Kafka stores partitioned topics that consumers pull from and can replay (Flume is legacy for new builds).
- What is log compaction, and when do you use it instead of time retention? — Compaction keeps the latest value per key forever, so the topic can act as the current-state changelog for CDC or configuration data, while time retention is for event streams (not in sources, but standard).
- What is Kafka Connect and when would you use it? — A managed connector framework for source and sink integrations with offset handling and converters built in, used instead of writing bespoke producer/consumer services for ingestion (not in sources, but standard).
- How many partitions should a topic have? — Enough for peak consumer parallelism plus headroom, since consumers beyond the partition count idle; more partitions cost metadata, open files and longer rebalances, and cannot be reduced later (not in sources, but standard).

## Traps
- Describing Kafka as a queue that deletes on read; records stay until retention expires and consumption only advances an offset.
- Claiming Kafka preserves global ordering; ordering is per partition, so more partitions means less ordering unless you key correctly.
- Adding more consumers than partitions and expecting more throughput — the extras sit idle.
- Doing long work inside the poll loop without tuning `max.poll.interval.ms`, which triggers a rebalance and reprocessing of the batch.
- Answering "exactly-once" with only `enable.idempotence`; you also need transactions on the producer and `read_committed` on the consumer.
- Naming ZooKeeper as a requirement; KRaft is the default and ZooKeeper is gone in Kafka 4.0, so mention it only as history.

## Graph
- **Needs first:** [[batch-vs-streaming]]
- **Leads to:** [[lambda-kappa]]
- **Asked together with:** [[distributed-systems]]
