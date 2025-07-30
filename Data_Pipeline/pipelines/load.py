import pandas as pd
from typing import Dict, List
import logging
from sqlalchemy import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresLoader:
    _PRIMARY_KEYS = {
        "movies": "movie_id",
        "genres": "genre_id",
        "production_companies": "company_id",
        "production_countries": "iso_3166_1",
        "spoken_languages": "iso_639_1",
        "collections": "collection_id"
    }

    _JUNCTION_TABLES = {
        "movie_genres", "movie_production_companies",
        "movie_production_countries", "movie_spoken_languages", "movie_collections"
    }

    _LOAD_ORDER: List[str] = [
        "movies", "collections", "genres", "production_companies",
        "production_countries", "spoken_languages", "release_calendar",
        "trailers", "movie_genres", "movie_production_companies",
        "movie_production_countries", "movie_spoken_languages", "movie_collections"
    ]

    def __init__(self, engine):
        self.engine = engine
        self._processed_ids = {table: set() for table in self._PRIMARY_KEYS}
        self._load_existing_ids()

    def _load_existing_ids(self):
        for table, pk in self._PRIMARY_KEYS.items():
            try:
                query = f"SELECT DISTINCT {pk} FROM {table} WHERE {pk} IS NOT NULL"
                existing = pd.read_sql(query, self.engine)[pk].dropna().unique()
                self._processed_ids[table] = set(existing)
                logger.info(f"Loaded {len(existing)} existing IDs for {table}")
            except Exception as e:
                logger.warning(f"Could not load existing IDs for {table}: {e}")

    def _filter_valid_columns(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        cols = {col['name'] for col in inspect(self.engine).get_columns(table)}
        return df[[c for c in df.columns if c in cols]]

    def _filter_new_records(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        if table in self._JUNCTION_TABLES:
            return self._filter_junction_table(df, table)

        pk = self._PRIMARY_KEYS.get(table)
        if not pk or pk not in df.columns:
            return df.drop_duplicates()

        df_clean = df[df[pk].notna()].drop_duplicates(subset=[pk])
        new_ids = set(df_clean[pk]) - self._processed_ids[table]
        self._processed_ids[table].update(new_ids)
        return df_clean[df_clean[pk].isin(new_ids)]

    def _filter_junction_table(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        df_clean = df.dropna().drop_duplicates()
        if df_clean.empty:
            return df_clean

        try:
            existing = pd.read_sql(f"SELECT * FROM {table}", self.engine)
            if existing.empty:
                return df_clean
            key_cols = list(df_clean.columns)
            df_clean["__key__"] = df_clean[key_cols].astype(str).agg("_".join, axis=1)
            existing["__key__"] = existing[key_cols].astype(str).agg("_".join, axis=1)
            new_records = df_clean[~df_clean["__key__"].isin(existing["__key__"])]
            return new_records[key_cols]
        except Exception as e:
            logger.warning(f"Could not check existing records for {table}: {e}")
            return df_clean

    def _insert_data(self, df: pd.DataFrame, table: str) -> None:
        if df.empty:
            return
        try:
            df.to_sql(table, self.engine, if_exists="append", index=False, method="multi")
            logger.info(f"Inserted {len(df)} records into {table}")
        except Exception as e:
            logger.error(f"Batch insert failed for {table}: {e}")
            for i, row in df.iterrows():
                try:
                    pd.DataFrame([row]).to_sql(table, self.engine, if_exists="append", index=False)
                except Exception as e:
                    logger.warning(f"Row {i} failed in {table}: {e}")

    def load(self, main_df: pd.DataFrame, related_dfs: Dict[str, pd.DataFrame], main_table: str) -> None:
        main_new = self._filter_new_records(main_df, main_table)
        if main_new.empty:
            logger.info("No new records to insert")
            return

        self._insert_data(self._filter_valid_columns(main_new, main_table), main_table)
        movie_ids = set(main_new[self._PRIMARY_KEYS[main_table]])

        # Những bảng không nên lọc theo movie_id
        independent_tables = {"genres", "spoken_languages", "production_countries", "collections"}

        related_new = {}
        for tbl, df in related_dfs.items():
            if df is None or df.empty:
                continue

            # 🎯 Nếu là bảng từ điển → giữ nguyên
            if tbl in independent_tables:
                df_filtered = df

            # 🎯 Nếu là bảng collections → xử lý đặc biệt
            elif tbl == "collections":
                related_new["collections"] = self._filter_new_records(df, "collections")
                if {"movie_id", "collection_id"}.issubset(df.columns):
                    df_mc = df[["movie_id", "collection_id"]]
                    related_new["movie_collections"] = self._filter_new_records(df_mc, "movie_collections")

                continue  # tránh xử lý lại ở dưới

            # 🎯 Còn lại → lọc theo movie_id nếu có
            else:
                df_filtered = df[df["movie_id"].isin(movie_ids)] if "movie_id" in df.columns else df

            related_new[tbl] = self._filter_new_records(df_filtered, tbl)

        for tbl in self._LOAD_ORDER:
            if tbl != main_table and tbl in related_new:
                self._insert_data(self._filter_valid_columns(related_new[tbl], tbl), tbl)

