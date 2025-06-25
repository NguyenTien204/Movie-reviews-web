CREATE TABLE "users" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(320) UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "movies" (
  movie_id SERIAL PRIMARY KEY,
  title VARCHAR NOT NULL,
  release_date DATE,
  overview TEXT,
  tagline TEXT,
  runtime INTEGER,
  language VARCHAR(10),
  poster_path VARCHAR
);

CREATE TABLE "genres" (
  genre_id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE "movie_genres" (
  movie_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL,
  PRIMARY KEY (movie_id, genre_id)
);

CREATE TABLE "watch_history" (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  watched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "ratings" (
  rating_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  score FLOAT NOT NULL,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "follows" (
  following_user_id INTEGER NOT NULL,
  followed_user_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (following_user_id, followed_user_id)
);

CREATE TABLE "dim_session" (
  user_id INTEGER NOT NULL,
  session_id VARCHAR PRIMARY KEY,
  start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  browser VARCHAR,
  os VARCHAR,
  screen_resolution VARCHAR
);

CREATE TABLE "fact_user_event" (
  event_id UUID PRIMARY KEY,
  user_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  session_id VARCHAR,
  movie_id INTEGER,
  metadata JSONB,
  processed BOOLEAN DEFAULT false
);

CREATE TABLE "comments" (
  id UUID PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT false
);

CREATE TABLE "comment_votes" (
  user_id INTEGER NOT NULL,
  comment_id UUID NOT NULL,
  vote_type SMALLINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, comment_id)
);

CREATE TABLE "watchlist" (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "release_calendar" (
  id SERIAL PRIMARY KEY,
  movie_id INTEGER NOT NULL,
  country_code CHAR(2),
  release_date DATE NOT NULL,
  release_type VARCHAR(50)
);

CREATE TABLE "production_companies" (
  company_id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,
  origin_country VARCHAR(2)
);

CREATE TABLE "movie_production_companies" (
  movie_id INTEGER NOT NULL,
  company_id INTEGER NOT NULL,
  PRIMARY KEY (movie_id, company_id)
);

CREATE TABLE "production_countries" (
  iso_3166_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE "movie_production_countries" (
  movie_id INTEGER NOT NULL,
  iso_3166_1 CHAR(2) NOT NULL,
  PRIMARY KEY (movie_id, iso_3166_1)
);

CREATE TABLE "spoken_languages" (
  iso_639_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE "movie_spoken_languages" (
  movie_id INTEGER NOT NULL,
  iso_639_1 CHAR(2) NOT NULL,
  PRIMARY KEY (movie_id, iso_639_1)
);

CREATE TABLE "trailers" (
  id VARCHAR PRIMARY KEY,
  movie_id INTEGER NOT NULL,
  name VARCHAR NOT NULL,
  site VARCHAR NOT NULL,
  key VARCHAR NOT NULL,
  type VARCHAR NOT NULL,
  official BOOLEAN,
  published_at TIMESTAMP
);

CREATE TABLE "collections" (
  id VARCHAR PRIMARY KEY,
  name VARCHAR,
  backdrop_path TEXT
);

CREATE TABLE "movie_collection" (
  movie_id INTEGER NOT NULL,
  collection_id VARCHAR NOT NULL,
  PRIMARY KEY (movie_id, collection_id)
);

CREATE UNIQUE INDEX ON "watchlist" (user_id, movie_id);

-- Add foreign keys
ALTER TABLE "movie_collection" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "movie_collection" ADD FOREIGN KEY (collection_id) REFERENCES "collections" (id);

ALTER TABLE "movie_genres" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "movie_genres" ADD FOREIGN KEY (genre_id) REFERENCES "genres" (genre_id);

ALTER TABLE "watch_history" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "watch_history" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);

ALTER TABLE "ratings" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "ratings" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);

ALTER TABLE "follows" ADD FOREIGN KEY (following_user_id) REFERENCES "users" (id);
ALTER TABLE "follows" ADD FOREIGN KEY (followed_user_id) REFERENCES "users" (id);

ALTER TABLE "dim_session" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);

ALTER TABLE "fact_user_event" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "fact_user_event" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "fact_user_event" ADD FOREIGN KEY (session_id) REFERENCES "dim_session" (session_id);

ALTER TABLE "comments" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "comments" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);

ALTER TABLE "comment_votes" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "comment_votes" ADD FOREIGN KEY (comment_id) REFERENCES "comments" (id);

ALTER TABLE "watchlist" ADD FOREIGN KEY (user_id) REFERENCES "users" (id);
ALTER TABLE "watchlist" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);

ALTER TABLE "release_calendar" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);

ALTER TABLE "movie_production_companies" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "movie_production_companies" ADD FOREIGN KEY (company_id) REFERENCES "production_companies" (company_id);

ALTER TABLE "movie_production_countries" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "movie_production_countries" ADD FOREIGN KEY (iso_3166_1) REFERENCES "production_countries" (iso_3166_1);

ALTER TABLE "movie_spoken_languages" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
ALTER TABLE "movie_spoken_languages" ADD FOREIGN KEY (iso_639_1) REFERENCES "spoken_languages" (iso_639_1);

ALTER TABLE "trailers" ADD FOREIGN KEY (movie_id) REFERENCES "movies" (movie_id);
