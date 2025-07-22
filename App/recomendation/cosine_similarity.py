import faiss
import numpy as np
import pandas as pd
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from psycopg2.extras import execute_values

class MovieSimilarity:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect_to_db(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def load_movies(self):
        conn = self.connect_to_db()
        query = """
            SELECT
                m.movie_id,
                m.title,
                m.overview,
                STRING_AGG(DISTINCT g.name, ', ') AS genres
            FROM movies m
            JOIN movie_genres mg ON m.movie_id = mg.movie_id
            JOIN genres g ON mg.genre_id = g.genre_id
            GROUP BY m.movie_id, m.title, m.overview
            ORDER BY m.movie_id;
        """
        movies_df = pd.read_sql(query, conn)
        conn.close()
        return movies_df

    def preprocess_data(self, movies_df):
        movies_df['text_data'] = movies_df['genres'].fillna('') + " " + movies_df['overview'].fillna('')
        return movies_df

    def compute_tfidf(self, movies_df):
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
        tfidf_matrix = vectorizer.fit_transform(movies_df['text_data'])
        return tfidf_matrix.astype(np.float32), vectorizer

    def compute_faiss_similarity(self, tfidf_matrix, top_k=10):
        tfidf_array = tfidf_matrix.toarray().astype(np.float32)

        # Đảm bảo là float32 và C_CONTIGUOUS
        tfidf_array = np.require(tfidf_array, dtype=np.float32, requirements=['C_CONTIGUOUS'])

        # Chuẩn hóa vector để dùng cosine similarity
        faiss.normalize_L2(tfidf_array)

        index = faiss.IndexFlatIP(tfidf_array.shape[1])
        index.add(tfidf_array)

        similarity_scores, indices = index.search(tfidf_array, top_k + 1)  # +1 để bỏ chính nó
        return similarity_scores, indices

    def save_to_db(self, similarity_scores, indices, movies_df, top_k=10):
        conn = self.connect_to_db()
        cursor = conn.cursor()
        similarity_data = []

        for i in range(len(movies_df)):
            movie_id_1 = int(movies_df['movie_id'].iloc[i])
            for j in range(1, top_k + 1):  # Bỏ qua chính nó
                movie_id_2 = int(movies_df['movie_id'].iloc[indices[i][j]])
                sim = float(similarity_scores[i][j])
                if sim > 0:
                    similarity_data.append((movie_id_1, movie_id_2, sim))

        if similarity_data:
            execute_values(cursor, """
                INSERT INTO cosine_similarity_results (movie_id_1, movie_id_2, similarity)
                VALUES %s
                ON CONFLICT (movie_id_1, movie_id_2) DO UPDATE SET similarity = EXCLUDED.similarity
            """, similarity_data)
            conn.commit()

        cursor.close()
        conn.close()

    def get_top_10_similar_movies(self, movie_id, similarity_scores, indices, movies_df, top_k=10):
        """Lấy top 10 phim tương đồng với một phim cụ thể theo movie_id."""
        if movie_id not in set(movies_df['movie_id']):
            raise ValueError(f"Movie ID {movie_id} không tồn tại trong dữ liệu!")

        movie_idx = movies_df.index[movies_df['movie_id'] == movie_id][0]

        top_10_indices = indices[movie_idx][1:top_k + 1]
        top_10_scores = similarity_scores[movie_idx][1:top_k + 1]

        top_10_movies = []
        for idx, score in zip(top_10_indices, top_10_scores):
            movie = movies_df.iloc[idx]
            top_10_movies.append({
                'movie_id': movie['movie_id'],
                'title': movie['title'],
                'similarity': score
            })

        return top_10_movies

    def process(self, top_k=10):
        movies_df = self.load_movies()
        movies_df = self.preprocess_data(movies_df)
        tfidf_matrix, _ = self.compute_tfidf(movies_df)
        sim_scores, indices = self.compute_faiss_similarity(tfidf_matrix, top_k=top_k)
        self.save_to_db(sim_scores, indices, movies_df, top_k=top_k)
        return sim_scores, indices, movies_df


def main():
    movie_sim = MovieSimilarity(dbname="movie_db", user="postgres", password="141124")
    sim_scores, indices, movies_df = movie_sim.process(top_k=10)

    movie_id = 5  # đảm bảo đây là movie_id hợp lệ trong bảng

    try:
        movie_title = movies_df[movies_df['movie_id'] == movie_id]['title'].values[0]
        print(f"\nTop 10 phim tương tự với phim '{movie_title}':")
        top_10 = movie_sim.get_top_10_similar_movies(movie_id=movie_id,
                                                     similarity_scores=sim_scores,
                                                     indices=indices,
                                                     movies_df=movies_df,
                                                     top_k=10)
        for movie in top_10:
            print(f"{movie['title']} - similarity: {movie['similarity']:.4f}")
    except IndexError:
        print(f"Không tìm thấy phim với movie_id = {movie_id}")

if __name__ == "__main__":
    main()
