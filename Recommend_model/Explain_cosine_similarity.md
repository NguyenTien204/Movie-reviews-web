# 🎬 Movie Recommender System: Content-Based Filtering with Cosine Similarity (FAISS + PostgreSQL)

This Python module implements a **content-based movie recommendation system** using **TF-IDF vectorization** and **cosine similarity**, accelerated by **FAISS** for efficient nearest-neighbor search. The recommendations are stored in a **PostgreSQL** database.

---

## 📁 File: `Cosine_similarity.py`

### 🧠 Core Functionalities

#### 1. **Database Connection**
- Uses `psycopg2` to connect to a PostgreSQL database that contains structured movie information.

#### 2. **Load Movie Data**
- Executes a complex SQL query joining multiple tables:
  - `movies`, `genres`, `production_companies`, `release_calendar`, etc.
- Extracts columns like:
  - `title`, `overview`, `tagline`, `release_date`, `genres`, `production_companies`.

#### 3. **Text Preprocessing**
- Concatenates textual attributes into a single `text_data` field to be used for vectorization.

#### 4. **TF-IDF Vectorization**
- Applies `TfidfVectorizer` from `scikit-learn` to convert `text_data` into a numeric matrix.

#### 5. **Cosine Similarity with FAISS**
- Normalizes vectors for cosine similarity.
- Uses FAISS `IndexFlatIP` for fast inner product search (cosine similarity).
- Finds the top-K most similar movies for each movie.

#### 6. **Save to PostgreSQL**
- Stores top-K movie recommendations with similarity scores in a table named `cosine_similarity_results`.

#### 7. **Retrieve Top 10 Similar Movies**
- Provides a method to get top 10 similar movies for a given `movie_id`.

#### 8. **Main Execution Flow**
- Executes the full pipeline:
  - Loads data → preprocesses → vectorizes → computes similarity → saves to DB → prints top 10 similar movies.

---

## 🔧 Setup & Dependencies

### 🐍 Required Python Packages:
```bash
pip install numpy pandas psycopg2 scikit-learn faiss-cpu
