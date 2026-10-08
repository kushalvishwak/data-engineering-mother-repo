# Table contract example

For `silver.orders`: grain is one current order record; primary key is `(source_system, order_id)`; `updated_at` is UTC; deletes are represented by a tombstone; amount is decimal with explicit currency; late changes are accepted for a defined correction window. Breaking schema changes require versioning and consumer coordination.
