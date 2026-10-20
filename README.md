# untitled-movie-social
A better social media for movies and series

## <How to run locally>
1. Copy .env.example to your .env file and fill the keys with your data
2. On terminal (windows) run "docker compose up -d"
3. Migrate with "manage.py migrate"
4. Run "python manage.py sync_tmdb


## <Stats>
- 437 movies/min, sequential, local Postgres, including ~10 DB statements per movie.
![alt text](docs/image-1.png)

This product uses the TMDB API but is not endorsed or certified by TMDB
![alt text](docs/image.png)