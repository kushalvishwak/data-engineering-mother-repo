---
id: sql-ddl-dml-transactions
title: DDL, DML and Transactions
tier: 0
priority: must-know
sources: [obenner/sql.md, obenner/dwha.md, obenner/cdc.md, devinterview, cookbook]
---

# DDL, DML and Transactions

## Say it in one line
DDL defines structure, DML changes rows, DCL grants access and TCL bounds a unit of work — and the line to know cold is that DELETE is filterable row-by-row DML, TRUNCATE wipes every row by deallocating pages, and DROP removes the object itself.

## Must be able to recite
- **DDL** — `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`, `COMMENT`; defines objects, acts on the whole object, takes no WHERE clause.
- **DML** — `INSERT`, `UPDATE`, `DELETE`, `MERGE` (with `SELECT` often split out as DQL); acts on rows, supports WHERE, always runs inside a transaction.
- **DCL and TCL** — DCL is `GRANT`/`REVOKE` (plus `DENY` in SQL Server); TCL is `COMMIT`, `ROLLBACK`, `SAVEPOINT` and `SET TRANSACTION`.
- **DELETE** — DML, row at a time, WHERE-filterable, logs every row, fires row triggers, rolls back anywhere, leaves the identity counter and the allocated space untouched.
- **TRUNCATE** — removes all rows by deallocating the data pages, so it logs almost nothing and runs in near-constant time whatever the row count, and it has no WHERE clause.
- **DROP** — removes the rows, the definition, indexes, triggers, constraints and grants in one statement; the table simply ceases to exist.
- **TRUNCATE and rollback** — transactional and roll-back-able in SQL Server and PostgreSQL; an implicit commit in Oracle and MySQL, where it is unrecoverable.
- **TRUNCATE and identity** — SQL Server and MySQL reset the counter to the seed, PostgreSQL only with `RESTART IDENTITY`, Oracle keeps counting; `DELETE` never resets it.
- **TRUNCATE and foreign keys** — refused while another table's FK points at it in Oracle, MySQL and SQL Server (even if the child table is empty), while PostgreSQL wants `CASCADE` or every referencing table named.
- **Constraints** — `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `CHECK` and `DEFAULT`; declarative rules the engine enforces so you never need a trigger for integrity.
- **Key vocabulary** — a candidate key uniquely identifies a row, the chosen one is the primary key, the losers are alternate keys, a multi-column key is composite, a system-generated one is surrogate.
- **Referential actions** — `NO ACTION`/`RESTRICT` blocks the parent change, `CASCADE` propagates the delete or update, `SET NULL`/`SET DEFAULT` blanks the child column.
- **ACID** — atomicity is all-or-nothing via undo, consistency means every constraint still holds at commit, isolation hides other transactions' uncommitted work, durability means a committed change survives a crash.
- **Isolation levels, weakest first** — read uncommitted, read committed, repeatable read, serializable; each removes one more anomaly and gives up concurrency to do it.
- **The anomalies** — dirty read (reading uncommitted data), non-repeatable read (a re-read row changed), phantom read (a re-run query gains rows), and write skew (two snapshots jointly break a rule).

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ **Difference between DELETE, TRUNCATE and DROP?** — DELETE is DML that removes selected rows and can be rolled back; TRUNCATE is DDL that removes all rows by deallocating pages, keeping the empty table; DROP is DDL that removes the table itself along with its indexes, triggers, constraints and grants.
- ★ **Can TRUNCATE be rolled back?** — In SQL Server and PostgreSQL yes, inside an explicit transaction, because it logs page deallocations; in Oracle and MySQL no, because the statement forces an implicit commit. *(the sources contradict each other here — one says it can never be rolled back, another says "of course it can"; both are half right, so always name the engine)*
- ★ **Why is TRUNCATE faster than DELETE?** — DELETE writes an undo and redo record per row and maintains every index; TRUNCATE just deallocates the pages and resets the high-water mark, so its cost barely moves with table size.
- ★ **What happens to a table's unique/identity id after TRUNCATE versus DELETE?** — TRUNCATE resets the counter in SQL Server and MySQL (PostgreSQL only with `RESTART IDENTITY`, Oracle not at all); DELETE always leaves the next value where it was, so ids continue after the gap.
- ★ **Why does TRUNCATE fail on a table that has a foreign key pointing at it?** — The engine cannot check per-row referential integrity when it is deallocating whole pages, so it refuses outright; you drop or disable the referencing constraint, or truncate the child first (PostgreSQL will do that for you with `CASCADE`).
- **Does TRUNCATE fire triggers?** — No row-level DELETE triggers fire, which is exactly why audit trails silently miss truncates; PostgreSQL is the exception, with statement-level `ON TRUNCATE` triggers.
- **Which privilege does each need?** — DELETE needs the DELETE privilege on the table, while TRUNCATE needs schema-level rights (ALTER on the table in SQL Server, DROP in MySQL, owner or DROP ANY TABLE in Oracle) because it is DDL.
- **Does DELETE give the space back?** — No; PostgreSQL leaves dead tuples until VACUUM, Oracle leaves the high-water mark where it was, and SQL Server can leave empty pages allocated — only TRUNCATE or DROP releases the extents.
- ★ **My DELETE fails with a foreign key constraint error — what do you do?** — Delete or reassign the child rows first, or declare the relationship `ON DELETE CASCADE` so dependents go with the parent. *(the source suggests setting `foreign_key_checks=0`; that hides the error and leaves orphan rows, so treat it as a last resort in a controlled migration only)*
- **What does DROP take with it, and what happens to views that used the table?** — Data, structure, indexes, triggers, constraints and permissions all go; dependent views and procedures survive as broken objects that fail at run time, unless you use `DROP ... CASCADE` in PostgreSQL or `CASCADE CONSTRAINTS` in Oracle.
- **Can you recover a truncated or dropped table?** — Only from a backup, from an Oracle recycle bin `FLASHBACK TABLE ... TO BEFORE DROP`, or by rolling back if the engine made the statement transactional; assume you cannot and take a backup first.
- **When would you use ORDER BY in a DELETE?** — MySQL allows `DELETE ... ORDER BY ts LIMIT n` so you delete a deterministic slice — the oldest rows first — which is also how you chunk a huge delete.
- **How would you delete 50 million rows in production?** — Delete in bounded batches with a commit per batch to keep the log and lock footprint small, or copy the rows you are keeping to a new table, TRUNCATE, and swap.
- **Is DDL transactional?** — In PostgreSQL and SQL Server yes, so `CREATE`/`ALTER`/`DROP` can be rolled back; in Oracle and MySQL each DDL statement commits implicitly. *(the sources state flatly that DDL cannot be rolled back — that is only true for Oracle and MySQL)*
- ★ **What is the difference between DDL and DML?** — DDL defines the structure, works on the whole object, has no WHERE and (in Oracle/MySQL) commits itself; DML manipulates rows, supports WHERE, fires triggers and is committed or rolled back by you.
- ★ **Name the SQL command families.** — DDL (structure), DML (rows), DQL (`SELECT`), DCL (`GRANT`/`REVOKE`) and TCL (`COMMIT`/`ROLLBACK`/`SAVEPOINT`).
- **How do you add, drop or rename a column, and rename a table?** — `ALTER TABLE t ADD col type`, `ALTER TABLE t DROP COLUMN col`, `ALTER TABLE t RENAME COLUMN a TO b`, `ALTER TABLE t RENAME TO t2` (`sp_rename` in SQL Server).
- ★ **What are constraints, and which ones exist?** — Declarative rules the RDBMS enforces on insert, update and delete without you writing triggers: NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, CHECK, plus DEFAULT.
- ★ **Primary key versus unique key?** — One primary key per table, never NULL, and it is the row's identifier; many unique keys per table, each allowing NULL (one NULL in SQL Server, any number in Oracle and PostgreSQL) and each only preventing duplicates.
- **Define candidate key, alternate key and composite key.** — Any column set that uniquely identifies a row is a candidate key, the one you pick becomes the primary key, the remaining candidates are alternate keys, and a key spanning two or more columns is composite.
- **What does a foreign key actually enforce?** — That every non-NULL value in the child column exists as a key value in the parent table, which is why inserts into the child and deletes from the parent can both be rejected.
- ★ **What referential actions can a foreign key take, and what is CASCADE for?** — `NO ACTION`/`RESTRICT` rejects the change, `CASCADE` applies the delete or update to the children, `SET NULL`/`SET DEFAULT` clears the child column — all so referential integrity holds without application code. *(the sources list only RESTRICT and DELETE CASCADE; the standard defines all five)*
- ★ **How do you implement one-to-one, one-to-many and many-to-many?** — One-to-one as one table or two sharing a key, one-to-many as a foreign key on the many side, many-to-many as a junction table whose composite primary key is the two foreign keys.
- **What is an identity column or sequence, and why do the numbers have gaps?** — A generator that hands out unique values per insert (`IDENTITY`, `SEQUENCE`, `AUTO_INCREMENT`, `SERIAL`); it is not transactional, so rolled-back inserts burn numbers permanently, and hitting the column's maximum makes every later insert fail until you widen it to BIGINT.
- ★ **What is MERGE, and how do you upsert?** — One statement that matches a source to a target and inserts, updates or deletes accordingly: standard `MERGE INTO` in Oracle, SQL Server and PostgreSQL 15+, `INSERT ... ON CONFLICT DO UPDATE` in PostgreSQL, `INSERT ... ON DUPLICATE KEY UPDATE` in MySQL. It needs a unique key on the target and a de-duplicated source, or the engine errors on matching one target row twice.
- ★ **What is a transaction, and what are the ACID properties?** — A logical unit of work in which every step happens or none does; atomicity, consistency, isolation and durability are the guarantees that make that safe under concurrency and crashes.
- **When does a transaction end?** — At `COMMIT` or `ROLLBACK` (or an implicit commit from a DDL statement, or a disconnect, which rolls back).
- **What do COMMIT and ROLLBACK actually do?** — COMMIT makes the changes permanent and visible to transactions that start afterwards; ROLLBACK reverses every change in the transaction using the undo log.
- **What is a savepoint, and what is the difference between ROLLBACK TO and RELEASE SAVEPOINT?** — A named marker inside a transaction; `ROLLBACK TO sp` undoes work back to that point but keeps the transaction open, while `RELEASE SAVEPOINT sp` just discards the marker and keeps all the work.
- ★ **What are the isolation levels?** — Read uncommitted, read committed, repeatable read and serializable; read committed is the default in SQL Server, PostgreSQL and Oracle, while MySQL/InnoDB defaults to repeatable read and Oracle does not offer read uncommitted or repeatable read at all.
- **Which anomaly does each isolation level prevent?** — Read uncommitted prevents nothing, read committed stops dirty reads, repeatable read also stops non-repeatable reads, and serializable additionally stops phantoms; PostgreSQL's repeatable read is snapshot isolation, so it blocks phantoms but still allows write skew. *(not in sources, but standard — the source's own description of repeatable read as "a separate phantom row" is garbled)*
- **How do you get a consistent read across several queries?** — Run them in one transaction at `SERIALIZABLE`, or in Oracle use `SET TRANSACTION READ ONLY`, so every query in it sees the same point-in-time snapshot.
- ★ **What is a deadlock, and what is a livelock?** — A deadlock is a cycle in which each transaction holds a lock the other needs, so the engine detects it and kills a victim; a livelock is work that keeps moving but never finishes, such as a transaction perpetually starved of a lock.
- **How do you prevent deadlocks?** — Touch objects in the same order everywhere, keep transactions short, index the columns you filter and join on so fewer rows are locked, and retry the victim on the deadlock error code. *(not in sources, but standard)*
- ★ **What is blocking, and how do you troubleshoot it?** — One session waits because another holds a conflicting lock, which resolves itself when the first commits; you find the blocker in `sys.dm_exec_requests`, `pg_locks` joined to `pg_stat_activity`, or `SHOW ENGINE INNODB STATUS`, then fix the long transaction rather than killing sessions. *(the source's `sp_lock`/`sp_who2` answer is dated but still works)*
- **What is lock escalation?** — When one statement accumulates too many row or page locks (around 5,000 on one object in SQL Server), the engine swaps them for a single table lock to save memory — which turns a row-level operation into a table-level blocker.
- **What is the write-ahead log, and what is a checkpoint?** — Every change is written to the log and flushed before the data pages and before COMMIT is acknowledged, which is what makes durability possible; a checkpoint hardens dirty pages so that restart recovery only replays from there, in three phases — analysis, redo, then undo of whatever was still uncommitted.
- **What is two-phase commit?** — For a transaction spanning databases: the coordinator asks every participant to prepare, and only if all of them promise does it tell them all to commit — otherwise all roll back.
- **What is a trigger, and when does it fire?** — A stored block bound to a table that runs before or after an INSERT, UPDATE or DELETE, per row or per statement; useful for audit trails, and easy to abuse as hidden business logic.
- **How do privileges work, and what are the DCL commands?** — `GRANT` and `REVOKE` (plus `DENY` in SQL Server) on system privileges (create/alter/drop objects) and object privileges (SELECT, INSERT, UPDATE, DELETE, EXECUTE, REFERENCES), usually bundled into roles rather than granted per user.

## Traps
- Saying flatly "TRUNCATE cannot be rolled back" — it can in SQL Server and PostgreSQL; name the engine and you turn a wrong answer into a strong one.
- Describing TRUNCATE as "DELETE without a WHERE, but faster" — it skips row triggers, skips per-row logging, resets identity in some engines, needs higher privileges and fails while a foreign key references the table.
- Saying DROP "deletes the data and keeps the table" — that is TRUNCATE; DROP takes the definition, indexes, constraints and grants with it.
- Reciting the four ACID letters but being unable to name one anomaly or the default isolation level of the database on your CV.
- Calling blocking a deadlock — blocking clears itself when the first transaction commits, a deadlock never does and must be broken by the engine.
- Forgetting that TRUNCATE produces no row-level change events, so downstream CDC consumers and audit tables keep rows the source no longer has.

## Graph
- **Needs first:** [[sql-semantics]]
- **Leads to:** [[sql-performance-indexing]]
- **Asked together with:** [[relational-modeling]], [[cdc-ingestion]]
