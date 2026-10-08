"""Platform-dependent Spark plan inspection; requires a compatible PySpark runtime."""
from pyspark.sql import DataFrame
from pyspark.sql.functions import broadcast, col


def inspect_join_plans(events: DataFrame, customers: DataFrame) -> None:
    """Compare plans only; inspect runtime metrics before choosing a strategy."""
    projected_events = events.select("customer_id", "event_date", "amount").where(
        col("event_date").isNotNull()
    )
    projected_customers = customers.select("customer_id", "segment")

    projected_events.join(projected_customers, "customer_id").explain("formatted")
    projected_events.join(broadcast(projected_customers), "customer_id").explain(
        "formatted"
    )

    # Choosing repartition can incur a shuffle; coalesce can reduce parallelism.
    projected_events.repartition("customer_id").explain("formatted")
