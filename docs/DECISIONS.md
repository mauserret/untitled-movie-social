# Models
- tmdb_sync_at will be set at ingestion, after a succesful fetch instead of defaulting to timezone.now because it will only apply when created and not on updates
- Filter will be made at ingestion 

# tmdb.py
- 404 return None skipping that movie and keeping the catched copy

# ingestion.py
- Genre.objects.filter(tmdb_id__in=tmdb_ids) is used instead of creating the genres from the movie’s data because the genres are created once and each movie only links to the rows that already exist, a renamed genre updates in one place, although if TMDB adds a new genre the filter(tmdb_id__in=...) will skip it. But thats why sync_genres() runs at every ingestion job and its costs almost nothing.
- A detail about the guard: if credits: is True for any non-empty dict, even {"cast": [], "crew": []}. So it only protects against the case where the credits key is missing entirely (your data.get("credits", {}) then passes {}). It doesn’t protect against TMDB sending the key with empty lists. That’s probably the right behavior, since an explicit empty list means TMDB really has no credits for the movie. Write that in
- Sequential, no concurrency (yet). Measured 180 movies in 23.9 s (~451 movies/min): ~74% waiting on TMDB, ~22% in Postgres (~10 statements per movie, 12 with transaction control), ~3% other. Parallel requests could cut the run time by up to ~4x, but a sequential job already loads 5,000 movies in about 11 minutes, so the added complexity isn’t justified. Conditions: local Postgres, one run, ~7.5 req/s (well under TMDB’s rate limit). Re-measure after deploying to AWS, where the database share will grow.
- `finally` keyword: without it, a save that fails would skip the line that adds its time, and db_time would undercount exactly the slow, failing cases.