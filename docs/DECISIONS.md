# Models
- tmdb_sync_at will be set at ingestion, after a succesful fetch instead of defaulting to timezone.now because it will only apply when created and not on updates
- Filter will be made at ingestion 

# tmdb.py
- 404 return None skipping that movie and keeping the catched copy

# ingestion.py
- Genre.objects.filter(tmdb_id__in=tmdb_ids) is used instead of creating the genres from the movie’s data because the genres are created once and each movie only links to the rows that already exist, a renamed genre updates in one place, although if TMDB adds a new genre the filter(tmdb_id__in=...) will skip it. But thats why sync_genres() runs at every ingestion job and its costs almost nothing.