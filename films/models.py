from django.db import models

class Genre(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True) 
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Movie(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    original_language = models.CharField(max_length=10, blank=True)
    overview = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True, db_index=True) # index to search
    runtime_minutes = models.PositiveSmallIntegerField(default=None, null=True, blank=True)
    poster_path = models.CharField(max_length=255, default="", blank=True)
    backdrop_path = models.CharField(max_length=255, default="", blank=True)
    tmdb_synced_at = models.DateTimeField(null=True, blank=True, db_index=True) # TMDB limits cache up to 6 months
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True) # m2m: a movie has different genres and a genre has different movies

    def __str__(self):
        return self.title

class Person(models.Model):
    tmdb_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255, db_index=True) # index to search
    profile_path = models.CharField(max_length=255, default=None, blank=True) # Photo
    tmdb_synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class Credit(models.Model):
    class Kind(models.TextChoices):
        CAST = "cast", "Cast" # For actors (character and cast_order)
        CREW = "crew", "Crew" # For team (department and job)

    tmdb_credit_id = models.CharField(max_length=32, unique=True) 
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="credits") # delete because no movie = no credit
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="credits") # delete because no person = no credit
    kind = models.CharField(max_length=4, choices=Kind.choices) 
    character = models.CharField(max_length=255, blank=True)
    cast_order = models.PositiveSmallIntegerField(null=True, blank=True)
    department = models.CharField(max_length=64, blank=True)
    job = models.CharField(max_length=64, blank=True)

    class Meta:
        indexes = [models.Index(fields=["movie", "cast_order"])]

    def __str__(self):
        return f"{self.person}: {self.movie} - {self.kind}"



