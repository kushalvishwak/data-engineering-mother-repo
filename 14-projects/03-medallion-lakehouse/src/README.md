# Implementation outline

Separate ingestion, layer transformations, quality gates, and publication markers. Keep business transformations pure where possible. Platform-specific Delta, Auto Loader, and Unity Catalog code belongs in an explicitly versioned notebook or module with an environment setup guide.
