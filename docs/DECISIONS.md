# Models
- tmdb_sync_at will be set at ingestion, after a succesful fetch instead of defaulting to timezone.now because it will only apply when created and not on updates
- Filter will be made at ingestion 