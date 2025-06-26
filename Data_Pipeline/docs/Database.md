# 📊 Movie Review Application Database Design

---

## 1. Overview

The database is optimized for a movie review and recommendation application, supporting both user behavior analytics and rich movie metadata storage. The system uses PostgreSQL with a star schema, combining dimension (descriptive) and fact (transactional) tables to ensure query performance, scalability, and seamless integration with both batch and streaming data pipelines.

---

## 2. Data Model Summary

- **Users**: Registration, authentication, following, rating, commenting on movies.
- **Movies**: Detailed metadata, genres, production companies, countries, languages, trailers, collections.
- **Interactions**: Watch history, ratings, comments, comment votes, watchlist, behavioral events.
- **Analytics support**: Event logs (fact_user_event), user sessions (dim_session).

---

## 3. Main Tables & Explanations

### 3.1. Users & Relationships

- **users**: Account info, security, creation/update timestamps.
- **follows**: User-to-user following (social graph).
- **dim_session**: User session info, device/browser metadata.

### 3.2. Movies & Metadata

- **movies**: Core movie info (title, description, language, poster, etc.).
- **genres** & **movie_genres**: Movie genres and many-to-many mapping.
- **production_companies**, **movie_production_companies**: Companies and their movie links.
- **production_countries**, **movie_production_countries**: Production countries.
- **spoken_languages**, **movie_spoken_languages**: Movie languages.
- **release_calendar**: Release dates by country and type.
- **trailers**: Trailer, teaser, and clip info.
- **collections**, **movie_collection**: Movie collections (franchise, series).

### 3.3. User Interactions

- **watch_history**: User's movie watch history.
- **ratings**: User ratings (score) for movies.
- **comments**: User comments on movies (threaded).
- **comment_votes**: Upvote/downvote on comments.
- **watchlist**: User's movie watchlist, status (watching, completed, planned, dropped).

### 3.4. Events & Analytics

- **fact_user_event**: Behavioral event logs (click, view, like, share, comment, watch), with extensible metadata.
- **dim_session**: Session info, linked to events.

---

## 4. Enums & Reference Tables

- **watchlist_status_enum**: Watchlist status (`watching`, `completed`, `planned`, `dropped`).
- **trailer_type_enum**: Trailer type (`Trailer`, `Teaser`, `Clip`, `Featurette`).
- **site_enum**: Trailer video source (`YouTube`, `Vimeo`).
- **event_type_enum**: Event types (`click`, `view`, `like`, `share`, `comment`, `watch`).

---

## 5. Relationships & Constraints

- **Foreign keys**: Ensure data integrity between tables (user, movie, session, etc.).
- **Many-to-many link tables**: movie_genres, movie_production_companies, movie_production_countries, movie_spoken_languages, movie_collection.
- **Unique constraints**: username, email (users); (user_id, movie_id) (watchlist); (user_id, comment_id) (comment_votes).
- **CHECK**: Prevent users from following themselves (follows).

---

## 6. Indexes

- **idx_ratings_movie_id**: Speeds up rating queries by movie.
- **idx_watch_history_user_id**: Speeds up watch history queries by user.
- **idx_fact_user_event_type**: Speeds up event analytics by type.
- **idx_comments_movie_id**: Speeds up comment queries by movie.
- **idx_trailers_movie_id**: Speeds up trailer queries by movie.

---

## 7. Design Notes & Extensibility

- **UUID**: Used for comment and event IDs to support distributed and streaming integration.
- **JSONB**: Metadata field in fact_user_event allows flexible, extensible event data.
- **Soft Delete**: `is_deleted` fields allow hiding data instead of physical deletion.
- **Star Schema**: Suited for analytics, BI, and aggregation queries.
- **Batch & Streaming**: Designed for both batch (Pandas) and streaming (Spark) pipelines.
- **Extensible**: Easy to add new dimensions (e.g., directors, actors) or new fact tables for additional behaviors.

---

## 8. Entity Relationship Diagram (ERD) - Textual Description

- **users** (1) --- (N) **watch_history**, **ratings**, **comments**, **watchlist**, **fact_user_event**, **dim_session**
- **movies** (1) --- (N) **watch_history**, **ratings**, **comments**, **watchlist**, **fact_user_event**, **trailers**, **release_calendar**
- **movies** (N) --- (N) **genres**, **production_companies**, **production_countries**, **spoken_languages**, **collections** (via link tables)
- **comments** (1) --- (N) **comment_votes**
- **users** (N) --- (N) **follows** (mutual following)
- **dim_session** (1) --- (N) **fact_user_event**

---

## 9. Common Query Examples

- Get top movies by average rating.
- Query a user's watch history.
- Aggregate views, comments, ratings by movie.
- Analyze user behavior by event type.
- Filter movies by genre, country, or production company.

---

## 10. References & Contact

- **Full schema**: See `database/schema.sql`
- **Pipeline design**: See `README.md`, `Design.md`
- **Technical contact**: Nguyễn Văn Tiến (vantiennguyen1424@gmail.com)

---
