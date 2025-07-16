import os
import sys
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
import yaml
from typing import Dict, List, Any, Optional
import logging
import pandas as pd
from sqlalchemy import create_engine
from typing import Dict, List
from Data_Pipeline.pipelines.extract import DuplicateRemover

from Data_Pipeline.config.mongo_config import MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION
from Data_Pipeline.config.postgres_config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresLoader:
    def __init__(self, engine):
        self.engine = engine
        self.remover = DuplicateRemover(engine)
        self._init_cache()

    def _init_cache(self):
        """Khởi tạo và cập nhật cache"""
        # Định nghĩa primary keys cho tất cả các bảng
        self._PRIMARY_KEYS = {
            "movies": "movie_id",
            "genres": "genre_id",
            "production_companies": "company_id",
            "production_countries": "iso_3166_1",
            "spoken_languages": "iso_639_1",
            "collections": "collection_id"
        }
        
        # Khởi tạo cache rỗng cho mỗi bảng
        self._processed_ids = {table: set() for table in self._PRIMARY_KEYS.keys()}
        
        # Load dữ liệu hiện có vào cache
        self._load_existing_ids()

    def _load_existing_ids(self):
        """Load tất cả ID hiện có từ database vào cache"""
        for table, pk in self._PRIMARY_KEYS.items():
            try:
                query = f"SELECT DISTINCT {pk} FROM {table} WHERE {pk} IS NOT NULL"
                existing = pd.read_sql(query, self.engine)[pk]
                self._processed_ids[table] = set(existing.unique())
                logger.info(f"Loaded {len(self._processed_ids[table])} existing IDs for {table}")
            except Exception as e:
                logger.warning(f"Could not load existing IDs for {table}: {e}")
                self._processed_ids[table] = set()

    # ---------- helpers ----------
    _LOAD_ORDER: List[str] = [
        "movies",  # Load bảng chính trước
        "collections", # Sau đó load các bảng phụ thuộc
        "genres", "production_companies", "production_countries",
        "spoken_languages", "release_calendar", "trailers",
        "movie_genres", "movie_production_companies",
        "movie_production_countries", "movie_spoken_languages",
        "movie_collections"
    ]

    def _process_collections(self, collections_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Xử lý riêng bảng collections và tạo bảng movie_collections"""
        if collections_df is None or collections_df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Lọc ra các collection mới chưa tồn tại trong DB
        collections_df = collections_df[collections_df['collection_id'].notna()]
        if collections_df.empty:
            return pd.DataFrame(), pd.DataFrame()

        # Tạo DataFrame cho collections (loại bỏ movie_id và giữ các collection unique)
        collections_columns = ['collection_id', 'name', 'poster_path', 'backdrop_path']
        unique_collections = collections_df[collections_columns].drop_duplicates(subset=['collection_id'])
        
        # Lọc các collection đã tồn tại
        new_collections = self._filter_new_records(unique_collections, 'collections')
        
        # Tạo DataFrame cho movie_collections
        movie_collections = collections_df[['movie_id', 'collection_id']].drop_duplicates()
        
        return new_collections, movie_collections

    @staticmethod
    def _find_pk(df: pd.DataFrame) -> str:
        candidates = [c for c in df.columns if c.endswith("_id")]
        return candidates[0] if candidates else df.columns[0]

    def _filter_new_records(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        """Lọc ra các bản ghi chưa được xử lý dựa trên cache"""
        if table not in self._PRIMARY_KEYS:
            return df
        
        pk = self._PRIMARY_KEYS[table]
        if pk not in df.columns:
            return df
            
        # Lọc bỏ các bản ghi đã tồn tại trong cache và null
        mask = (~df[pk].isin(self._processed_ids[table])) & (df[pk].notna())
        new_records = df[mask]
        
        # Cập nhật cache với các ID mới
        if not new_records.empty:
            new_ids = set(new_records[pk].unique())
            self._processed_ids[table].update(new_ids)
            logger.debug(f"Added {len(new_ids)} new IDs to cache for {table}")
            
        return new_records

    # ---------- public API ----------
    def load(self,
             main_df: pd.DataFrame,
             related_dfs: Dict[str, pd.DataFrame],
             main_table: str) -> None:
        
        # Xác định và lọc bản ghi mới cho bảng chính
        main_pk = self._PRIMARY_KEYS[main_table]  # Sử dụng primary key đã định nghĩa
        main_new = self._filter_new_records(main_df, main_table)
        
        if main_new.empty:
            logger.info("No new records to insert in main table")
            return
            
        new_movie_ids = set(main_new[main_pk])
        logger.info(f"Processing {len(new_movie_ids)} new movies")

        # Xử lý collections riêng
        if 'collections' in related_dfs:
            new_collections, movie_collections = self._process_collections(related_dfs['collections'])
            if not new_collections.empty:
                related_dfs['collections'] = new_collections
            if not movie_collections.empty:
                related_dfs['movie_collections'] = movie_collections

        # Xử lý các bảng liên quan khác
        related_new = {}
        for tbl, df in related_dfs.items():
            if df is not None and not df.empty:
                if tbl != 'collections' and tbl != 'movie_collections':  # Bỏ qua collections vì đã xử lý
                    filtered_df = self._filter_new_records(df, tbl)
                    
                    # Lọc theo khóa ngoại từ bảng chính nếu có
                    if main_pk in filtered_df.columns:
                        filtered_df = filtered_df[filtered_df[main_pk].isin(new_movie_ids)]
                        
                    if not filtered_df.empty:
                        related_new[tbl] = filtered_df.drop_duplicates()
                else:
                    related_new[tbl] = df  # Giữ nguyên dữ liệu collections đã được xử lý

        with self.engine.begin():
            if not main_new.empty:
                main_new.to_sql(main_table, self.engine, if_exists="append", index=False)
                logger.info(f"Inserted {len(main_new)} records into {main_table}")

            for tbl in self._LOAD_ORDER:
                if tbl == main_table or tbl not in related_new:
                    continue
                    
                df_tbl = related_new[tbl]
                if df_tbl.empty:
                    continue

                logger.info(f"Inserting {len(df_tbl)} records into {tbl}")
                try:
                    df_tbl.to_sql(tbl, self.engine, if_exists="append", index=False)
                except Exception as e:
                    logger.error(f"Error inserting into {tbl}: {str(e)}")
                    raise