import pandas as pd
from typing import Dict, List, Optional
import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresLoader:
    def __init__(self, engine):
        self.engine = engine
        self._init_cache()

    def _init_cache(self):
        """Khởi tạo cache cho các primary keys"""
        self._PRIMARY_KEYS = {
            "movies": "movie_id",
            "genres": "genre_id", 
            "production_companies": "company_id",
            "production_countries": "iso_3166_1",
            "spoken_languages": "iso_639_1",
            "collections": "collection_id"
        }
        
        self._processed_ids = {table: set() for table in self._PRIMARY_KEYS.keys()}
        self._load_existing_ids()

    def _load_existing_ids(self):
        """Load tất cả ID hiện có từ database vào cache"""
        for table, pk in self._PRIMARY_KEYS.items():
            try:
                query = f"SELECT DISTINCT {pk} FROM {table} WHERE {pk} IS NOT NULL"
                existing = pd.read_sql(query, self.engine)[pk]
                self._processed_ids[table] = set(existing.dropna().unique())
                logger.info(f"Loaded {len(self._processed_ids[table])} existing IDs for {table}")
            except Exception as e:
                logger.warning(f"Could not load existing IDs for {table}: {e}")
                self._processed_ids[table] = set()

    # Thứ tự load dữ liệu
    _LOAD_ORDER: List[str] = [
        "movies", "collections", "genres", "production_companies", 
        "production_countries", "spoken_languages", "release_calendar", 
        "trailers", "movie_genres", "movie_production_companies",
        "movie_production_countries", "movie_spoken_languages", "movie_collections"
    ]

    def _filter_new_records(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        """Lọc ra các bản ghi mới chưa tồn tại trong database"""
        if df is None or df.empty:
            return pd.DataFrame()
        if table not in self._PRIMARY_KEYS:
            return df.drop_duplicates()
        pk = self._PRIMARY_KEYS[table]
        if pk not in df.columns:
            return df.drop_duplicates()
            
        # Lọc bỏ null và duplicate trong chính DataFrame
        df_clean = df[df[pk].notna()].drop_duplicates(subset=[pk])
        new_records = df_clean[~df_clean[pk].isin(self._processed_ids[table])]
        
        # Cập nhật cache
        if not new_records.empty:
            new_ids = set(new_records[pk].unique())
            self._processed_ids[table].update(new_ids)  
        return new_records

    def _filter_new_records(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        """Lọc ra các bản ghi mới chưa tồn tại trong database"""
        if df is None or df.empty:
            return pd.DataFrame()
            
        # Xử lý đặc biệt cho các bảng junction không có single primary key
        if table in ['movie_genres', 'movie_production_companies', 
                     'movie_production_countries', 'movie_spoken_languages', 'movie_collections']:
            return self._filter_junction_table(df, table)
        if table not in self._PRIMARY_KEYS:
            return df.drop_duplicates()
        pk = self._PRIMARY_KEYS[table]
        if pk not in df.columns:
            return df.drop_duplicates()
            
        # Lọc bỏ null và duplicate trong chính DataFrame
        df_clean = df[df[pk].notna()].drop_duplicates(subset=[pk])
        new_records = df_clean[~df_clean[pk].isin(self._processed_ids[table])]
        
        # Cập nhật cache
        if not new_records.empty:
            new_ids = set(new_records[pk].unique())
            self._processed_ids[table].update(new_ids)
            
        return new_records

    def _filter_junction_table(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        """Xử lý các bảng junction có composite key"""
        df_clean = df.dropna().drop_duplicates()
        if df_clean.empty:
            return df_clean
            
        try:
            # Load existing records để so sánh
            existing = pd.read_sql(f"SELECT * FROM {table}", self.engine)
            if existing.empty:
                return df_clean
                
            # Tạo composite key cho cả existing và new data
            key_cols = list(df_clean.columns)
            df_clean['composite_key'] = df_clean[key_cols].astype(str).agg('_'.join, axis=1)
            existing['composite_key'] = existing[key_cols].astype(str).agg('_'.join, axis=1)
            
            # Lọc ra records mới
            new_records = df_clean[~df_clean['composite_key'].isin(existing['composite_key'])]
            return new_records[key_cols]  # Bỏ composite_key column
            
        except Exception as e:
            logger.warning(f"Could not check existing records for {table}: {e}")
            return df_clean

    def _insert_data(self, df: pd.DataFrame, table: str) -> None:
        """Insert dữ liệu với error handling tốt hơn"""
        if df.empty:
            return
            
        try:
            df.to_sql(table, self.engine, if_exists="append", index=False, method='multi')
            logger.info(f"Successfully inserted {len(df)} records into {table}")
        except Exception as e:
            logger.error(f"Error inserting into {table}: {str(e)}")
            # Thử insert từng record một nếu batch insert failed
            if len(df) > 1:
                logger.info(f"Trying individual inserts for {table}")
                success_count = 0
                for _, row in df.iterrows():
                    try:
                        pd.DataFrame([row]).to_sql(table, self.engine, if_exists="append", index=False)
                        success_count += 1
                    except Exception as row_error:
                        logger.warning(f"Failed to insert row in {table}: {row_error}")
                logger.info(f"Successfully inserted {success_count}/{len(df)} records into {table}")
            else:
                raise

    def load(self, main_df: pd.DataFrame, related_dfs: Dict[str, pd.DataFrame], main_table: str) -> None:
        """Load dữ liệu vào database"""
        
        # Lọc main table
        main_new = self._filter_new_records(main_df, main_table)
        
        if main_new.empty:
            logger.info("No new records to insert")
            return
            
        new_movie_ids = set(main_new[self._PRIMARY_KEYS[main_table]])
        logger.info(f"Processing {len(new_movie_ids)} new records for {main_table}")

        # Xử lý tất cả bảng liên quan một cách thống nhất
        related_new = {}
        for tbl, df in related_dfs.items():
            if df is None or df.empty:
                continue
                
            # Lọc theo movie_id nếu có
            if 'movie_id' in df.columns:
                df_filtered = df[df['movie_id'].isin(new_movie_ids)]
            else:
                df_filtered = df
                
            # Xử lý đặc biệt cho collections - tạo cả collections và movie_collections
            if tbl == 'collections':
                # Xử lý bảng collections
                new_collections = self._filter_new_records(df_filtered, 'collections')
                if not new_collections.empty:
                    related_new['collections'] = new_collections
                    
                # Tạo movie_collections từ cùng data
                if 'movie_id' in df_filtered.columns and 'collection_id' in df_filtered.columns:
                    movie_collections_df = df_filtered[['movie_id', 'collection_id']]
                    new_movie_collections = self._filter_new_records(movie_collections_df, 'movie_collections')
                    if not new_movie_collections.empty:
                        related_new['movie_collections'] = new_movie_collections
            else:
                # Xử lý tất cả bảng khác (kể cả junction tables) giống nhau
                new_records = self._filter_new_records(df_filtered, tbl)
                if not new_records.empty:
                    related_new[tbl] = new_records

        # Insert theo thứ tự
        self._insert_data(main_new, main_table)
        
        for tbl in self._LOAD_ORDER:
            if tbl != main_table and tbl in related_new:
                self._insert_data(related_new[tbl], tbl)