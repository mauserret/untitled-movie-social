from films.models import Genre


def sync_genres(client):
    data = client.get_genres()
    objs = [Genre(tmdb_id=g["id"], name=g["name"]) for g in data["genres"]]
    Genre.objects.bulk_create(
        objs,
        update_conflicts=True,
        unique_fields=["tmdb_id"],
        update_fields=["name"],
    )