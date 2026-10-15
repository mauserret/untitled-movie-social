from django.db import transaction
from django.utils import timezone

from films.models import Genre, Movie


def sync_genres(client):
    data = client.get_genres()
    objs = [Genre(tmdb_id=genre["id"], name=genre["name"]) for genre in data["genres"]]
    Genre.objects.bulk_create(
        objs,
        update_conflicts=True,
        unique_fields=["tmdb_id"],
        update_fields=["name"],
    )


@transaction.atomic
def upsert_movie(data):
    movie, created = Movie.objects.update_or_create(
        tmdb_id=data["id"],
        defaults={
            "title": data["title"],
            "release_date": data.get("release_date") or None,
            "original_title": data.get("original_title") or "",
            "original_language": data.get("original_language") or "",
            "overview": data.get("overview") or "",   
            "runtime_minutes": data.get("runtime") or None,
            "poster_path": data.get("poster_path") or "",
            "backdrop_path": data.get("backdrop_path") or "",
            "tmdb_synced_at": timezone.now(),
        },
    )

    tmdb_ids = [genre["id"] for genre in data.get("genres", [])]
    genres = Genre.objects.filter(tmdb_id__in=tmdb_ids)
    movie.genres.set(genres)
    return movie