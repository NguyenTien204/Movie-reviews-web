-- PostgreSQL optimized schema for a movie database

-- ========================
-- ENUM / REFERENCE TABLES
-- ========================

CREATE TYPE watchlist_status_enum AS ENUM ('watching', 'completed', 'planned', 'dropped');

CREATE TYPE trailer_type_enum AS ENUM ('Trailer', 'Teaser', 'Clip', 'Featurette','Behind the Scenes', 'Bloopers', 'Opening Scene', 'Ending Scene', 'Deleted Scene');

CREATE TYPE site_enum AS ENUM ('YouTube', 'Vimeo');

CREATE TYPE event_type_enum AS ENUM ('click', 'view', 'like', 'share', 'comment', 'watch');

-- ========================
-- USERS
-- ========================
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(320) UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================
-- MOVIES & RELATIONS
-- ========================
CREATE TABLE movies (
  movie_id INTEGER PRIMARY KEY,
  title VARCHAR NOT NULL,
  original_title VARCHAR NOT NULL,
  overview TEXT,
  tagline TEXT,
  runtime INTEGER,
  homepage VARCHAR,
  poster_path VARCHAR,
  popularity DOUBLE PRECISION,
  adult BOOLEAN,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE genres (
  genre_id INTEGER PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE movie_genres (
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  genre_id INTEGER NOT NULL REFERENCES genres(genre_id) ON DELETE CASCADE,
  PRIMARY KEY (movie_id, genre_id)
);

-- ========================
-- WATCH HISTORY, RATINGS, COMMENTS
-- ========================
CREATE TABLE watch_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE ratings (
  rating_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  score FLOAT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE comments (
  id UUID PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE comment_votes (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  comment_id UUID NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
  vote_type SMALLINT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, comment_id)
);

-- ========================
-- FOLLOWS
-- ========================
CREATE TABLE follows (
  following_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  followed_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (following_user_id, followed_user_id),
  CHECK (following_user_id != followed_user_id)
);

-- ========================
-- WATCHLIST
-- ========================
CREATE TABLE watchlist (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  status watchlist_status_enum NOT NULL,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, movie_id)
);

-- ========================
-- SESSIONS AND EVENTS
-- ========================
CREATE TABLE dim_session (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  session_id VARCHAR PRIMARY KEY,
  start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  browser VARCHAR,
  os VARCHAR,
  screen_resolution VARCHAR
);

CREATE TABLE fact_user_event (
  event_id UUID PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type event_type_enum NOT NULL,
  event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  session_id VARCHAR REFERENCES dim_session(session_id) ON DELETE SET NULL,
  movie_id INTEGER REFERENCES movies(movie_id) ON DELETE SET NULL,
  metadata JSONB,
  processed BOOLEAN DEFAULT FALSE
);

-- ========================
-- RELEASE CALENDAR
-- ========================
CREATE TABLE release_calendar (
  id SERIAL PRIMARY KEY,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  country_code CHAR(2),
  release_date DATE NOT NULL,
  release_type VARCHAR(50),
  status VARCHAR
);

-- ========================
-- COMPANIES, COUNTRIES, LANGUAGES
-- ========================
CREATE TABLE production_companies (
  company_id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,
  origin_country CHAR(2),
  logo_path VARCHAR
);

CREATE TABLE movie_production_companies (
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  company_id INTEGER NOT NULL REFERENCES production_companies(company_id),
  PRIMARY KEY (movie_id, company_id)
);

CREATE TABLE production_countries (
  iso_3166_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE movie_production_countries (
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  iso_3166_1 CHAR(2) NOT NULL REFERENCES production_countries(iso_3166_1),
  PRIMARY KEY (movie_id, iso_3166_1)
);

CREATE TABLE spoken_languages (
  iso_639_1 CHAR(2) PRIMARY KEY,
  name VARCHAR NOT NULL
);

CREATE TABLE movie_spoken_languages (
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  iso_639_1 CHAR(2) NOT NULL REFERENCES spoken_languages(iso_639_1),
  PRIMARY KEY (movie_id, iso_639_1)
);

-- ========================
-- TRAILERS
-- ========================
CREATE TABLE trailers (
  id VARCHAR PRIMARY KEY,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  site site_enum NOT NULL,
  key VARCHAR NOT NULL,
  type trailer_type_enum NOT NULL,
  official BOOLEAN,
  published_at TIMESTAMP,
  size INTEGER
);

-- ========================
-- COLLECTIONS
-- ========================
CREATE TABLE collections (
  collection_id VARCHAR PRIMARY KEY,
  movie_id INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
  name VARCHAR,
  backdrop_path TEXT,
  poster_path TEXT
);

CREATE TABLE cosine_similarity_results (
    id SERIAL PRIMARY KEY,
    movie_id_1 INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    movie_id_2 INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    similarity DOUBLE PRECISION NOT NULL,
    UNIQUE (movie_id_1, movie_id_2)
);

CREATE TABLE cosine_similarity_results (
    id SERIAL PRIMARY KEY,
    movie_id_1 INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    movie_id_2 INTEGER NOT NULL REFERENCES movies(movie_id) ON DELETE CASCADE,
    similarity DOUBLE PRECISION NOT NULL,
    UNIQUE (movie_id_1, movie_id_2)
);


-- ========================
-- Indexes for faster access
-- ========================
CREATE INDEX idx_ratings_movie_id ON ratings(movie_id);
CREATE INDEX idx_watch_history_user_id ON watch_history(user_id);
CREATE INDEX idx_fact_user_event_type ON fact_user_event(event_type);
CREATE INDEX idx_comments_movie_id ON comments(movie_id);
CREATE INDEX idx_trailers_movie_id ON trailers(movie_id);
