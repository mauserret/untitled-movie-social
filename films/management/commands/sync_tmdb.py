from django.core.management.base import BaseCommand

from films.ingestion import sync_genres, upsert_movie
from films.tmdb import TMDBClient, TMDBError
import time
from datetime import timedelta
from django.utils import timezone
from films.models import Movie


class Command(BaseCommand):
    help = "Sync popular movies from TMDB"

    def add_arguments(self, parser):
        parser.add_argument("--pages", type=int, default=1)

    def handle(self, *args, **options):
        client = TMDBClient()
        sync_genres(client)

        start = time.monotonic()
        cutoff = timezone.now() - timedelta(days=150)
        ok, skipped, failed = 0, 0, 0
        http_time = db_time = 0.0   # seconds spent waiting on TMDB / on the database

        for page in range(1, options["pages"] + 1):
            popular = client.get_popular(page)
            if not popular:
                break

            ids = [item["id"] for item in popular["results"]]
            fresh = set(
                Movie.objects.filter(tmdb_id__in=ids, tmdb_synced_at__gte=cutoff)
                .values_list("tmdb_id", flat=True)
            )

            for item in popular["results"]:
                if item["id"] in fresh:
                    skipped += 1
                    continue

                t0 = time.monotonic()
                try:
                    data = client.get_movie(item["id"])
                except TMDBError:
                    data = None
                http_time += time.monotonic() - t0

                if data is None:
                    failed += 1
                    self.stderr.write(f"movie {item['id']}: not found or TMDB kept failing")
                    continue

                t0 = time.monotonic()
                try:
                    upsert_movie(data)
                except Exception as exc:
                    failed += 1
                    self.stderr.write(f"movie {item['id']}: save failed: {exc!r}")
                else:
                    ok += 1
                finally:
                    db_time += time.monotonic() - t0

        elapsed = time.monotonic() - start
        per_minute = ok / elapsed * 60 if elapsed else 0
        self.stdout.write(
            f"ok={ok} skipped={skipped} failed={failed} "
            f"in {elapsed:.1f}s ({per_minute:.0f} movies/min) "
            f"[tmdb={http_time:.1f}s db={db_time:.1f}s]"
        )