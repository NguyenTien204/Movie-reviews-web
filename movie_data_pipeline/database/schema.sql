CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "username" VARCHAR(50) NOT NULL UNIQUE,
  "email" VARCHAR(320) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  "hashed_password" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "movies" (
  "movie_id" SERIAL PRIMARY KEY,
  "title" VARCHAR NOT NULL,
  "release_date" DATE,
  "overview" TEXT,
  "runtime" INTEGER CHECK (runtime >= 0),
  "language" VARCHAR(10),
  "poster_path" VARCHAR
);

CREATE TABLE "genres" (
  "genre_id" SERIAL PRIMARY KEY,
  "name" VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE "movie_genres" (
  "movie_id" INTEGER NOT NULL,
  "genre_id" INTEGER NOT NULL,
  PRIMARY KEY ("movie_id", "genre_id"),
  FOREIGN KEY ("movie_id") REFERENCES "movies" ("movie_id"),
  FOREIGN KEY ("genre_id") REFERENCES "genres" ("genre_id")
);


CREATE TABLE "watch_history" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "movie_id" INTEGER NOT NULL,
  "watched_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  FOREIGN KEY ("movie_id") REFERENCES "movies" ("movie_id")
);


CREATE TABLE "ratings" (
  "rating_id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "movie_id" INTEGER NOT NULL,
  "score" FLOAT NOT NULL CHECK (score >= 0 AND score <= 10),
  "timestamp" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  FOREIGN KEY ("movie_id") REFERENCES "movies" ("movie_id")
);



CREATE TABLE "follows" (
  "following_user_id" INTEGER NOT NULL,
  "followed_user_id" INTEGER NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("following_user_id", "followed_user_id"),
  FOREIGN KEY ("following_user_id") REFERENCES "users" ("id"),
  FOREIGN KEY ("followed_user_id") REFERENCES "users" ("id"),
  CHECK ("following_user_id" <> "followed_user_id")
);


CREATE TABLE "dim_session" (
  "session_id" VARCHAR PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "start_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "browser" VARCHAR,
  "os" VARCHAR,
  "screen_resolution" VARCHAR,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);


CREATE TABLE "fact_user_event" (
  "event_id" UUID PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "event_type" TEXT NOT NULL,
  "event_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "movie_id" INTEGER,
  "rating" FLOAT CHECK (rating >= 0 AND rating <= 10),
  "search_query" TEXT,
  "comment_id" UUID,
  "list_action" TEXT,
  "session_id" VARCHAR,
  "processed" BOOLEAN NOT NULL DEFAULT false,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  FOREIGN KEY ("movie_id") REFERENCES "movies" ("movie_id"),
  FOREIGN KEY ("session_id") REFERENCES "dim_session" ("session_id")
);


CREATE TABLE "comments" (
  id UUID PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  body TEXT NOT NULL, -- <-- đây là nơi chứa comment dài
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT false,
  FOREIGN KEY ("user_id") REFERENCES "users" ("id"),
  FOREIGN KEY ("movie_id") REFERENCES "movies" ("movie_id")
);

CREATE TABLE comment_votes (
  user_id INTEGER NOT NULL,
  comment_id UUID NOT NULL,
  vote_type SMALLINT NOT NULL CHECK (vote_type IN (-1, 1)), -- dislike = -1, like = 1
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, comment_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (comment_id) REFERENCES comments(id)
);

CREATE TABLE watchlist (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  movie_id INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL CHECK (status IN ('will_watch', 'watched')),
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  UNIQUE(user_id, movie_id)
);

CREATE TABLE release_calendar (
  id SERIAL PRIMARY KEY,
  movie_id INTEGER NOT NULL,
  country_code CHAR(2),
  release_date DATE NOT NULL,
  release_type VARCHAR(50), -- e.g., "theatrical", "digital", "streaming"
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE production_companies (
  company_id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,
  origin_country VARCHAR(2)
);

CREATE TABLE movie_production_companies (
  movie_id INTEGER NOT NULL,
  company_id INTEGER NOT NULL,
  PRIMARY KEY (movie_id, company_id),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (company_id) REFERENCES production_companies(company_id)
);

CREATE TABLE production_countries (
  iso_3166_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE movie_production_countries (
  movie_id INTEGER NOT NULL,
  iso_3166_1 CHAR(2) NOT NULL,
  PRIMARY KEY (movie_id, iso_3166_1),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (iso_3166_1) REFERENCES production_countries(iso_3166_1)
);

CREATE TABLE spoken_languages (
  iso_639_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE movie_spoken_languages (
  movie_id INTEGER NOT NULL,
  iso_639_1 CHAR(2) NOT NULL,
  PRIMARY KEY (movie_id, iso_639_1),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (iso_639_1) REFERENCES spoken_languages(iso_639_1)
);

CREATE TABLE trailers (
  id VARCHAR PRIMARY KEY, -- TMDB video ID
  movie_id INTEGER NOT NULL,
  name VARCHAR NOT NULL,
  site VARCHAR NOT NULL, -- e.g., YouTube
  key VARCHAR NOT NULL,  -- e.g., YouTube key
  type VARCHAR NOT NULL, -- Trailer, Teaser, Clip...
  official BOOLEAN,
  published_at TIMESTAMP,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);