from django.db import transaction
from django.utils import timezone

from films.models import Genre, Movie, Credit, Person


def sync_genres(client):
    data = client.get_genres()
    objs = [Genre(tmdb_id=genre["id"], name=genre["name"]) for genre in data["genres"]]
    Genre.objects.bulk_create(
        objs,
        update_conflicts=True,
        unique_fields=["tmdb_id"],
        update_fields=["name"],
    )

MAX_CAST = 15
CREW_JOBS = {"Director", "Writer", "Screenplay"}

def _upsert_credits(movie, credits):
    cast = sorted(credits.get("cast", []), key=lambda c: c.get("order", 999))[:MAX_CAST] # Sort by cast_order
    crew = [c for c in credits.get("crew", []) if c["job"] in CREW_JOBS]
    
    people = {}
    for c in cast + crew:
        people[c["id"]] = Person(
            tmdb_id=c["id"],
            name=c["name"],
            profile_path=c.get("profile_path"),
        )

    Person.objects.bulk_create(
        list(people.values()),
        update_conflicts=True,
        unique_fields=["tmdb_id"],
        update_fields=["name", "profile_path"],
    )

    saved = {p.tmdb_id: p for p in Person.objects.filter(tmdb_id__in=list(people))}

    credit_objs = []
    for c in cast:
        credit_objs.append(Credit(
            tmdb_credit_id=c["credit_id"],
            movie=movie,
            person=saved[c["id"]],
            kind=Credit.Kind.CAST,
            character=c.get("character") or "",
            cast_order=c.get("order"),
        ))
    for c in crew:
        credit_objs.append(Credit(
            tmdb_credit_id=c["credit_id"],
            movie=movie,
            person=saved[c["id"]],
            kind=Credit.Kind.CREW,
            department=c.get("department") or "",
            job=c.get("job") or "",
        ))
    Credit.objects.bulk_create(
        credit_objs,
        update_conflicts=True,
        unique_fields=["tmdb_credit_id"],
        update_fields=["character", "cast_order", "department", "job"],
    )
    if credits:
        movie.credits.exclude(tmdb_credit_id__in=[credit.tmdb_credit_id for credit in credit_objs]).delete()

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

    _upsert_credits(movie, data.get("credits", {}))
    return movie