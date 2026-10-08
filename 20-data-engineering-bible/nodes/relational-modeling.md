---
id: relational-modeling
title: Relational Modelling
tier: 0
priority: must-know
sources: [obenner/dwha, obenner/data-modeling, devinterview, cookbook]
---

# Relational Modelling

## Say it in one line
Relational modelling is designing data as entities, attributes and key-enforced relationships, then normalising them so every fact is stored in exactly one place.

## Must be able to recite
- **Conceptual model** — entities and the relationships between them only, no attributes and no keys; it exists so business stakeholders can agree the scope before anyone writes DDL.
- **Logical model** — every entity, attribute, primary key and foreign key, normalised but still independent of any DBMS; this is where many-to-many relationships get resolved.
- **Physical model** — the logical model realised in one specific engine, adding data types, indexes, partitions and any deliberate denormalisation, so it differs per engine (a MySQL type is not a SQL Server type).
- **Entity, attribute, relationship** — an entity is a thing with independent existence, an attribute is a property that describes it, a relationship is an association between two or more entities.
- **Relationship cardinality** — 1:1, 1:M or M:N; M:N cannot be expressed with two tables and must be resolved by a junction table whose primary key is the pair of foreign keys.
- **Functional dependency** — X → Y means the value of X uniquely determines the value of Y, and normalisation is nothing more than removing dependencies that are not on a whole key.
- **1NF** — every column holds one atomic value and there are no repeating groups, so a comma-separated `phone_numbers` column breaks it.
- **2NF** — 1NF plus every non-key column depends on the *whole* composite key rather than part of it; it only bites when the key is composite.
- **3NF** — 2NF plus no transitive dependency, so a non-key column must not determine another non-key column (`postcode → city` has to move to its own table).
- **BCNF** — every determinant is a candidate key; stricter than 3NF and only relevant when a table has overlapping candidate keys.
- **Normal forms are cumulative** — 3NF implies 2NF implies 1NF; beyond that, 4NF removes independent multi-valued dependencies and 5NF removes join dependencies (name recognition only).
- **Denormalisation** — deliberately duplicating data to remove joins, buying read speed at the cost of storage, write amplification and update anomalies; you accept that in a warehouse and refuse it in an OLTP schema.
- **Natural key vs surrogate key** — a natural key is a business column (email, airport name), a surrogate key is a meaningless system-generated integer; surrogates survive business-key changes, which is why warehouse dimensions always use them.
- **Candidate, alternate, composite keys** — every uniquely identifying column set is a candidate key, the one you pick is the primary key, the rest are alternate keys, and a key spanning several columns is composite (compound).
- **Entity integrity vs referential integrity** — entity integrity says a primary key can never be NULL; referential integrity says a foreign key is either NULL or matches an existing primary key, and it also fixes what happens on delete (RESTRICT, CASCADE, SET NULL).

## Questions actually asked
Ordered hardest-to-fumble first. `★` = appears in more than one source, so expect it.
- ★ Explain conceptual, logical and physical data models. — Conceptual is entities and relationships with no attributes or keys; logical adds all attributes plus PKs and FKs and is normalised but DBMS-independent; physical is tables, data types, indexes and partitions in one specific engine.
- ★ What is normalisation and why do we do it? — Splitting data into related tables so each fact is stored once; it removes insert, update and delete anomalies and keeps data consistent, at the price of more joins.
- ★ Explain 1NF, 2NF, 3NF and BCNF. — 1NF: atomic values, no repeating groups. 2NF: no partial dependency on part of a composite key. 3NF: no transitive dependency between non-key columns. BCNF: every determinant is a candidate key.
- ★ Describe the types of relationships in a relational database. — 1:1 (a student and one health record), 1:M (a customer and their orders, the common case) and M:N (books and authors), which needs a junction table holding a composite key.
- ★ What is a surrogate key and why use one? — A system-generated meaningless identifier, normally an integer sequence, used instead of a business column because natural keys change (email, airport name) and wide text keys join slowly.
- ★ What is the difference between ER modelling and dimensional modelling? — ER modelling normalises for OLTP write integrity; dimensional modelling denormalises into facts and dimensions for OLAP read performance. (The source says dimensional modelling "has only a physical model"; that is wrong — you still do conceptual and logical work, you just do it in facts and dimensions.)
- ★ What is the difference between a view and a materialised view? — A view stores only SQL and re-executes it on every access; a materialised view stores the result set physically, so reads are fast but the data is only as fresh as the last refresh.
- ★ Why is data modelling important and what are the steps? — It is the blueprint that makes metrics consistent and queries cheap; the steps are requirements, conceptual model, logical model (keys, attributes, resolve M:N, normalise), then physical model in the target DBMS.
- ★ What is the datatype of a surrogate key? — No type is mandated; the requirement is uniqueness and the convention is an integer sequence (identity/sequence), because integers index and join more cheaply than text.
- ★ What are primary and foreign keys? — The primary key uniquely identifies a row in the parent table and the foreign key in the child table references it; that pair is how a relational database expresses a relationship.
- What is the difference between a logical and a conceptual model specifically? — The logical model has primary keys and all attributes and specifies relationships via PK/FK pairs; the conceptual model has neither keys nor attributes and merely states that two entities are related.
- What are the steps to design a logical model? — Specify primary keys, find the relationships, find all attributes per entity, resolve many-to-many relationships, then normalise.
- Why not use the natural primary key as the surrogate key? — Natural keys are entered by users and carry business meaning, so they change and can be reused; a surrogate is generated by the system, never reused, and insulates every foreign key from source changes.
- What are partial, alternate, artificial, compound and natural keys? — Partial key identifies a weak entity within its owner; alternate keys are the candidate keys you did not pick; artificial key is generated when no natural one exists; compound key spans several columns; natural key is a business column used as the PK.
- Describe referential integrity and the referential actions. — A foreign key value must exist in the referenced table; on delete or update of the parent you choose RESTRICT/NO ACTION (block), CASCADE (propagate) or SET NULL.
- What are the integrity constraint types? — NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY and CHECK: declarative business rules the engine enforces instead of your application code.
- Define the integrity rules. — Entity integrity: a primary key cannot be NULL. Referential integrity: a foreign key is NULL or equals a primary key value in the referenced relation.
- What is a functional dependency, and a fully functional dependency? — X → Y holds if equal X values force equal Y values; it is *fully* functional if removing any attribute from X breaks it, which is exactly the test 2NF applies.
- What is a multivalued dependency and what is 4NF? — A multivalued dependency exists when one key independently determines two separate sets of values; 4NF forbids two unrelated 1:M or M:N relationships in one table.
- What is the lossless join property? — A decomposition is lossless if re-joining the pieces reproduces the original rows exactly with no spurious extra rows; it is the correctness condition for splitting a table.
- What is join dependency and inclusion dependency? — Join dependency generalises multivalued dependency and is what 5NF addresses; inclusion dependency says one table's columns are contained in another's, and a foreign key constraint is the everyday example.
- What is data cardinality? — Two different meanings: relationship cardinality (1:1, 1:M, M:N) and column cardinality, meaning the number of distinct values (high = email, normal = surname, low = a 0/1 flag). Ask which one they mean.
- What is an ER diagram and what is it good for? — A conceptual notation of entities, attributes and relationships that maps almost mechanically onto relational tables, so it serves both to agree the design with users and to generate DDL.
- What is a data model? — A set of conceptual tools for describing data, data relationships, semantics and constraints.
- Describe the three levels of data abstraction. — Physical (how data is stored), logical (what is stored and how it relates) and view (the slice a given user sees).
- What is data independence? — Changing one level should not force changes in the level above: physical independence means storage changes do not touch the logical schema, logical independence means schema changes do not break existing views.
- Do views contain data, and how do views provide data independence? — A view stores only its defining query and no rows; because users query the view, you can restructure the base tables without breaking them.
- What is the main difference between an RDBMS schema and a data warehouse schema? — RDBMS/OLTP schemas are normalised and optimised for writes and integrity; warehouse schemas are denormalised star or snowflake models optimised for readable, fast analytical queries. (The source calls OLTP schemas "poorly modelled"; they are not — they are modelled for a different workload.)
- What is extension and intension? — Extension is the set of rows in a table right now and changes constantly; intension is the fixed definition: name, structure and constraints.
- What is the degree of a relation? — The number of attributes in its schema; the number of rows is its cardinality.
- What is DKNF? — Domain-key normal form: every constraint is implied by domain and key constraints alone, which makes the relation free of modification anomalies. Name recognition only.

## Traps
- Saying "3NF means no redundancy" and stopping — 3NF is defined by dependencies, so state the rule and give one example (`postcode → city` must move out); vague answers read as memorisation.
- Reciting the normal forms as a numbered list with no example — keep one worked table ready (order_id, product, customer_postcode, city) and walk it from 1NF to 3NF; that is what earns the mark.
- Confusing the two meanings of cardinality — relationship cardinality (1:M) and column cardinality (distinct values) share the word, so clarify before answering.
- Claiming a surrogate key replaces the natural key — you keep the business key as a column, otherwise you cannot match incoming source rows or debug anything.
- Resolving M:N by "joining the two tables" — that multiplies rows; use a junction table in OLTP and a bridge table in a star schema.
- Presenting denormalisation as laziness — it is a costed trade (read speed against write cost and anomaly risk), so say which side of the OLTP/OLAP line you are on and why.

## Graph
- **Needs first:** [[sql-ddl-dml-transactions]]
- **Leads to:** [[dimensional-modeling]]
- **Asked together with:** [[oltp-vs-olap]]
