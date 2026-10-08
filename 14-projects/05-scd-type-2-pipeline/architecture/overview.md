# Temporal model

Example columns: business key, descriptive attributes, `valid_from`, `valid_to`, `is_current`, source sequence, and load timestamp. For half-open intervals `[valid_from, valid_to)`, a record is effective when `valid_from <= t AND t < valid_to`. Use a far-future sentinel only if consumers understand it; null end timestamps are another valid choice.
