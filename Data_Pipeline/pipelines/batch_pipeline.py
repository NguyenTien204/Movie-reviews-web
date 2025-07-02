import os
import sys
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import Table, MetaData

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Data_Pipeline.config.mongo_config import MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION
from Data_Pipeline.config.postgres_config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT


class BatchPipeline:
    def __init__(self, mongo_collection, mongo_uri, mongo_db, postgres_db, postgres_user, postgres_password, postgres_host, postgres_port):
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db
        self.mongo_collection_name = mongo_collection
        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port

        self.main_id_col = None  # Thêm thuộc tính này để lưu tên cột id chính

        self._connect_mongo()
        self._connect_postgres()

    def _connect_mongo(self):
        self.mongoclient = MongoClient(self.mongo_uri)
        self.mongo_db = self.mongoclient[self.mongo_db_name]
        self.mongo_collections = self.mongo_db[self.mongo_collection_name]

    def _connect_postgres(self):
        postgres_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        self.pg_engine = create_engine(postgres_url)

    def _load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def extract(self):
        data = list(self.mongo_collections.find())
        df = pd.DataFrame(data)
        return df

    def get_nested_field(self,doc, path):
        """Truy cập giá trị lồng qua path như 'a.b.c' hoặc 'a[].b'"""
        keys = path.replace("[]", ".[]").split(".")
        current = doc
        for k in keys:
            if isinstance(current, list):
                if k == "[]":
                    return current  # Trả về mảng để xử lý bên ngoài
                else:
                    # Tự động lấy tất cả giá trị k từ list
                    return [item.get(k) for item in current if k in item]
            elif isinstance(current, dict):
                current = current.get(k)
            else:
                return None
        return current


    def transform(self, df, config):
        main_table_fields = config['mappings']['simple_fields']
        one_to_one_mappings = config['mappings'].get('one_to_one', {})
        nested_objects = config['mappings'].get('nested_objects', {})
        arrays = config['mappings'].get('arrays', {})

        main_df_data = []
        related_dfs = {}

        for _, row in df.iterrows():
            row_dict = row.to_dict()
            main_row = {}

            # ✅ Simple fields → bảng chính
            for field in main_table_fields:
                value = self.get_nested_field(row_dict, field['source'])
                if field['source'] == "_id":
                    value = str(value)
                main_row[field['target']] = value

            movie_id = main_row.get('movie_id')
            main_df_data.append(main_row)

            # ✅ One-to-One: release_calendar, belongs_to_collection
            for key, mapping in one_to_one_mappings.items():
                table = mapping['table']
                local_row = {}
                for field in mapping['fields']:
                    value = self.get_nested_field(row_dict, field['source'])
                    local_row[field['target']] = value

                # thêm khóa ngoại từ movie
                rel = mapping['relation']
                local_row[rel['foreign_key']] = movie_id

                related_dfs.setdefault(table, []).append(local_row)

            # ✅ Nested objects: trailers,...
            for key, mapping in nested_objects.items():
                source_path = mapping['source_path']
                sub_items = self.get_nested_field(row_dict, source_path)
                if not isinstance(sub_items, list):
                    continue

                table = mapping['table']
                for item in sub_items:
                    new_row = {}
                    for field in mapping['fields']:
                        new_row[field['target']] = item.get(field['source'])
                    # thêm khóa ngoại
                    rel = mapping['relation']
                    new_row[rel['foreign_key']] = movie_id
                    related_dfs.setdefault(table, []).append(new_row)

            # ✅ Arrays: genres, companies,...
            for key, mapping in arrays.items():
                field_defs = mapping['fields']
                junction_table = mapping['junction_table']
                table = mapping['table']
                sub_items = self.get_nested_field(row_dict, field_defs[0]['source'].split("[]")[0])
                if not isinstance(sub_items, list):
                    continue

                for item in sub_items:
                    item_row = {}
                    for field in field_defs:
                        source_field = field['source'].split("[]")[-1].lstrip(".")  
                        item_row[field['target']] = item.get(source_field)
                    related_dfs.setdefault(table, []).append(item_row)

                    # junction
                    left_key = mapping['relation_keys']['left_key']
                    right_key = mapping['relation_keys']['right_key']
                    junction_row = {
                        left_key: movie_id,
                        right_key: item_row.get(right_key)
                    }
                    related_dfs.setdefault(junction_table, []).append(junction_row)

        # Chuyển về DataFrame
        main_df = pd.DataFrame(main_df_data)
        for table_name in related_dfs:
            related_dfs[table_name] = pd.DataFrame(related_dfs[table_name])

        return main_df, related_dfs

    def insert_on_conflict_do_nothing(self, df, table_name, engine, primary_key):
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)

        with engine.begin() as conn:
            for _, row in df.iterrows():
                stmt = pg_insert(table).values(row.to_dict())
                stmt = stmt.on_conflict_do_nothing(index_elements=[primary_key])
                conn.execute(stmt)


    def load(self, main_df, related_dfs, main_table):
        # Bảng chính
        main_df.to_sql(main_table, self.pg_engine, if_exists='append', index=False)

        main_tables_first = [
            "genres", 
            "production_companies", 
            "production_countries", 
            "spoken_languages", 
            "collections"
        ]

        primary_keys = {
            "genres": "genre_id",
            "production_companies": "company_id",
            "production_countries": "iso_3166_1",
            "spoken_languages": "iso_639_1",
            "collections": "collection_id"
        }

        junction_tables = [
            "movie_genres", 
            "movie_production_companies", 
            "movie_production_countries", 
            "movie_spoken_languages",
            "movie_collections"
        ]

        # Bảng chính phụ (1-nhiều, nhiều-nhiều)
        for table_name in main_tables_first:
            if table_name in related_dfs:
                df = related_dfs[table_name].drop_duplicates(subset=[primary_keys[table_name]])
                self.insert_on_conflict_do_nothing(df, table_name, self.pg_engine, primary_keys[table_name])

        # Bảng nối (junction) - cần foreign key đã tồn tại
        for table_name in junction_tables:
            if table_name in related_dfs:
                df = related_dfs[table_name].drop_duplicates()
                if not df.empty:
                    try:
                        df.to_sql(table_name, self.pg_engine, if_exists='append', index=False)
                    except Exception as e:
                        print(f"❌ Lỗi khi insert vào {table_name}: {e}")
    
    def run(self, config_path):
        config = self._load_config(config_path)
        main_table = config['main_table']

        df = self.extract()
        #test
        #print('⚠️',df.columns)
        #print('⚠️',df.head(1).to_dict())
        main_df, related_dfs = self.transform(df, config)
        self.load(main_df, related_dfs, main_table)


pipeline = BatchPipeline(
    mongo_collection=MOVIE_COLLECTION,
    mongo_uri=MONGO_URI,
    mongo_db=MONGO_DB_NAME,
    postgres_db=POSTGRES_DB,
    postgres_user=POSTGRES_USER,
    postgres_password=POSTGRES_PASSWORD,
    postgres_host=POSTGRES_HOST,
    postgres_port=POSTGRES_PORT
)
pipeline.run("Data_Pipeline/config/transform_config.yaml")
