
import os
import sys
import pandas as pd
from pymongo import MongoClient
from sqlalchemy import create_engine
import yaml
from typing import Dict, List, Any, Optional
import logging

# Import your new ETL components
from Data_Pipeline.pipelines.batch_pipeline import (
    ImprovedBatchPipeline, 
    TransformationEngine, 
    ConfigValidator,
    MappingType,
    FieldMapping,
    TableMapping
)

# Your existing config imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Data_Pipeline.config.mongo_config import MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION
from Data_Pipeline.config.postgres_config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT

class ModernETLPipeline:
    """Wrapper class để integrate với code cũ của bạn"""
    
    def __init__(self, mongo_collection, mongo_uri, mongo_db, postgres_db, 
                 postgres_user, postgres_password, postgres_host, postgres_port):
        # Setup logging
        self.logger = self._setup_logging()

        # MongoDB connection
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db]
        self.mongo_collection = self.mongo_db[mongo_collection]

        # PostgreSQL connection
        postgres_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        self.pg_engine = create_engine(postgres_url)

        # Initialize new ETL components
        self.transformer = TransformationEngine()
        self.validator = ConfigValidator()

        # ETL Metrics
        self.metrics = ETLMetrics()

        self.logger.info("ETL Pipeline initialized successfully")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('etl_pipeline.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def extract(self) -> pd.DataFrame:
        """Extract data from MongoDB"""
        try:
            self.logger.info("Starting data extraction from MongoDB...")
            data = list(self.mongo_collection.find())
            df = pd.DataFrame(data)
            self.logger.info(f"Successfully extracted {len(df)} records")
            return df
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise
    
    def load_and_validate_config(self, config_path: str) -> Dict:
        """Load và validate configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validate config structure
            self.validator.validate(config)
            self.logger.info("Configuration validated successfully")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading/validating config: {e}")
            raise
    
    def transform(self, df: pd.DataFrame, config: Dict) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Transform data using new strategy pattern"""
        try:
            self.logger.info("Starting data transformation...")
            
            # Parse config thành format mới
            parsed_config = self._parse_legacy_config(config)
            
            # Chạy transformation
            main_df, related_dfs = self.transformer.transform_batch(df, parsed_config)
            
            self.logger.info(f"Transformation completed. Main table: {len(main_df)} rows, "
                           f"Related tables: {len(related_dfs)}")
            return main_df, related_dfs
            
        except Exception as e:
            self.logger.error(f"Error during transformation: {e}")
            raise
    
    def _parse_legacy_config(self, config: Dict) -> Dict:
        """Convert config cũ sang format mới"""
        parsed = {
            'main_table': config['main_table'],
            'mappings': {}
        }

        # ✅ Không convert sang FieldMapping, giữ nguyên dict
        if 'simple_fields' in config['mappings']:
            parsed['mappings']['simple_fields'] = config['mappings']['simple_fields']

        for mapping_type in ['one_to_one', 'nested_objects', 'arrays']:
            if mapping_type in config['mappings']:
                parsed['mappings'][mapping_type] = config['mappings'][mapping_type]

        return parsed

    
    def load_with_proper_order(self, main_df: pd.DataFrame, 
                              related_dfs: Dict[str, pd.DataFrame], 
                              config: Dict):
        """Load data với proper order và error handling"""
        try:
            self.logger.info("Starting data loading...")
            
            with self.pg_engine.begin():
                # Load main table first
                main_table = config['main_table']
                main_df.to_sql(main_table, self.pg_engine, if_exists='append', index=False)
                self.logger.info(f"Loaded {len(main_df)} records to {main_table}")
                
                # Load related tables in proper order
                load_order = self._get_table_load_order()
                
                for table_name in load_order:
                    if table_name in related_dfs:
                        df = related_dfs[table_name]
                        if not df.empty:
                            # Handle duplicates
                            df_deduped = self._handle_duplicates(df, table_name)
                            
                            # Load with upsert logic
                            self._upsert_table(df_deduped, table_name)
                            self.logger.info(f"Loaded {len(df_deduped)} records to {table_name}")
                self.logger.info("All data loaded successfully!")
        except Exception as e:
            self.logger.error(f"Error during loading: {e}")
            raise
    
    def _get_table_load_order(self) -> List[str]:
        """Định nghĩa thứ tự load tables để tránh foreign key constraint"""
        return [
            # Master tables first (no foreign keys)
            "genres", 
            "production_companies", 
            "production_countries", 
            "spoken_languages", 
            "collections",
            
            # Then tables with foreign keys
            "release_calendar",
            "trailers",
            
            # Junction tables last
            "movie_genres", 
            "movie_production_companies", 
            "movie_production_countries", 
            "movie_spoken_languages",
            "movie_collections"
        ]
    
    def _handle_duplicates(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Handle duplicate records based on table type"""
        primary_keys = {
            "genres": "genre_id",
            "production_companies": "company_id",
            "production_countries": "iso_3166_1",
            "spoken_languages": "iso_639_1",
            "collections": "collection_id"
        }
        
        if table_name in primary_keys:
            key = primary_keys[table_name]
            return df.drop_duplicates(subset=[key])
        else:
            return df.drop_duplicates()
    
    def _upsert_table(self, df: pd.DataFrame, table_name: str):
        """Upsert data with ON CONFLICT handling"""
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy import Table, MetaData
        
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self.pg_engine)
        
        # Get primary key
        primary_keys = {
            "genres": "genre_id",
            "production_companies": "company_id", 
            "production_countries": "iso_3166_1",
            "spoken_languages": "iso_639_1",
            "collections": "collection_id"
        }
        
        if table_name in primary_keys:
            pk = primary_keys[table_name]
            
            with self.pg_engine.begin() as conn:
                for _, row in df.iterrows():
                    stmt = pg_insert(table).values(row.to_dict())
                    stmt = stmt.on_conflict_do_nothing(index_elements=[pk])
                    conn.execute(stmt)
        else:
            # For junction tables, just append
            df.to_sql(table_name, self.pg_engine, if_exists='append', index=False)
    
    def run(self, config_path: str):
        """Main execution method with ETL metrics"""
        try:
            self.logger.info("=== Starting ETL Pipeline ===")
            self.metrics.start_timing()
            # Step 1: Load and validate config
            config = self.load_and_validate_config(config_path)

            # Step 2: Extract data
            df = self.extract()
            self.metrics.records_processed = len(df)

            # Step 3: Transform data
            main_df, related_dfs = self.transform(df, config)

            # Step 4: Load data
            self.load_with_proper_order(main_df, related_dfs, config)

            # Thống kê số bản ghi từng bảng
            self.metrics.add_table_stat(config['main_table'], len(main_df))
            for table_name, rdf in related_dfs.items():
                self.metrics.add_table_stat(table_name, len(rdf))

            self.logger.info("=== ETL Pipeline completed successfully ===")
        except Exception as e:
            self.metrics.add_error(str(e))
            self.logger.error(f"=== ETL Pipeline failed: {e} ===")
            raise
        finally:
            self.metrics.end_timing()
            # Xuất báo cáo metrics ra log
            summary = self.metrics.get_summary()
            self.logger.info(f"ETL Metrics Summary: {summary}")
            # Cleanup connections
            self.mongo_client.close()
            self.pg_engine.dispose()

            
class EnhancedConfigValidator(ConfigValidator):
    """Enhanced validator with more comprehensive checks"""
    
    def validate(self, config: Dict) -> None:
        """Validate configuration with detailed checks"""
        super().validate(config)
        
        # Validate table dependencies
        self._validate_table_dependencies(config)
        
        # Validate field mappings
        self._validate_field_mappings(config)
        
        # Validate data types
        self._validate_data_types(config)
    
    def _validate_table_dependencies(self, config: Dict):
        """Check if foreign key relationships are properly defined"""
        mappings = config['mappings']
        
        # Check one-to-one relationships
        if 'one_to_one' in mappings:
            for key, mapping in mappings['one_to_one'].items():
                if 'relation' not in mapping:
                    raise ValueError(f"Missing relation config for {key}")
                
                relation = mapping['relation']
                if 'foreign_key' not in relation:
                    raise ValueError(f"Missing foreign_key in relation for {key}")
        
        # Check arrays (many-to-many)
        if 'arrays' in mappings:
            for key, mapping in mappings['arrays'].items():
                if 'junction_table' not in mapping:
                    raise ValueError(f"Missing junction_table for array {key}")
                
                if 'relation_keys' not in mapping:
                    raise ValueError(f"Missing relation_keys for array {key}")
    
    def _validate_field_mappings(self, config: Dict):
        """Validate field mapping consistency"""
        all_targets = []
        
        for mapping_type in ['simple_fields', 'one_to_one', 'nested_objects', 'arrays']:
            if mapping_type in config['mappings']:
                mapping = config['mappings'][mapping_type]
                
                if mapping_type == 'simple_fields':
                    targets = [field['target'] for field in mapping]
                    all_targets.extend(targets)
                elif mapping_type in ['one_to_one', 'nested_objects']:
                    for key, value in mapping.items():
                        targets = [field['target'] for field in value['fields']]
                        all_targets.extend(targets)
        
        # Check for duplicate targets
        duplicates = [target for target in set(all_targets) if all_targets.count(target) > 1]
        if duplicates:
            raise ValueError(f"Duplicate target fields found: {duplicates}")
    
    def _validate_data_types(self, config: Dict):
        """Validate data type specifications"""
        # Implementation for data type validation
        pass


class ETLMetrics:
    """Class để track ETL metrics"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.records_processed = 0
        self.errors = []
        self.table_stats = {}
    
    def start_timing(self):
        import time
        self.start_time = time.time()
    
    def end_timing(self):
        import time
        self.end_time = time.time()
    
    def get_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def add_table_stat(self, table_name: str, record_count: int):
        self.table_stats[table_name] = record_count
    
    def add_error(self, error: str):
        self.errors.append(error)
    
    def get_summary(self):
        return {
            'duration_seconds': self.get_duration(),
            'total_records': self.records_processed,
            'tables_processed': len(self.table_stats),
            'table_stats': self.table_stats,
            'error_count': len(self.errors),
            'errors': self.errors
        }
    
def main():
    """Main function để chạy ETL pipeline"""
    
    # Initialize pipeline với config cũ của bạn
    pipeline = ModernETLPipeline(
        mongo_collection=MOVIE_COLLECTION,
        mongo_uri=MONGO_URI,
        mongo_db=MONGO_DB_NAME,
        postgres_db=POSTGRES_DB,
        postgres_user=POSTGRES_USER,
        postgres_password=POSTGRES_PASSWORD,
        postgres_host=POSTGRES_HOST,
        postgres_port=POSTGRES_PORT
    )
    
    # Chạy pipeline
    pipeline.run("Data_Pipeline/config/transform_config.yaml")

if __name__ == "__main__":
    main()





