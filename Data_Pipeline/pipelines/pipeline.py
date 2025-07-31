# optimized_etl.py - Simplified and unified ETL pipeline

from typing import Dict, List, Any, Optional, Iterator
import pandas as pd
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import yaml
from pymongo.collection import Collection
from sqlalchemy import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# 1. UNIFIED DATA STRUCTURES
# =====================================================

@dataclass
class FieldMapping:
    source: str
    target: str
    data_type: Optional[str] = None
    default_value: Any = None
    required: bool = False

@dataclass
class TableConfig:
    name: str
    fields: List[FieldMapping]
    source_path: Optional[str] = None  # For nested objects
    foreign_key: Optional[str] = None  # Foreign key column name
    junction_table: Optional[str] = None  # For many-to-many
    junction_left_key: Optional[str] = None
    junction_right_key: Optional[str] = None

# =====================================================
# 2. SIMPLIFIED DATA EXTRACTOR
# =====================================================

class DataExtractor:
    def extract(self, doc: Dict, path: str) -> Any:
        """Extract data from nested document using dot notation"""
        try:
            if not path:
                return doc

            # Handle array notation: genres[].id -> genres, then extract id from each item
            if '[]' in path:
                array_path, field_path = path.split('[]', 1)
                array_data = self._get_nested_value(doc, array_path)

                if not isinstance(array_data, list):
                    return []

                if field_path.startswith('.'):
                    field_path = field_path[1:]

                if not field_path:  # Just the array itself
                    return array_data

                # Extract specific field from each array item
                results = []
                for item in array_data:
                    if isinstance(item, dict):
                        value = self._get_nested_value(item, field_path)
                        if value is not None:
                            results.append(value)
                return results

            return self._get_nested_value(doc, path)

        except Exception as e:
            logger.warning(f"Failed to extract '{path}': {e}")
            return None

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get value from nested object using dot notation"""
        if not path:
            return obj

        keys = path.split('.')
        current = obj

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None

        return current

# =====================================================
# 3. UNIFIED TRANSFORMER
# =====================================================

class UnifiedTransformer:
    def __init__(self):
        self.extractor = DataExtractor()

    def transform_batch(self, df: pd.DataFrame, config: Dict) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Transform a batch of documents"""
        main_table = config['main_table']
        main_results = []
        related_results = {}

        # Parse configurations
        configs = self._parse_configs(config)

        for _, row in df.iterrows():
            doc = row.to_dict()

            # Transform main table
            main_row = self._transform_simple_fields(doc, configs['simple'])
            if not main_row:
                continue

            main_df = pd.DataFrame([main_row])
            main_results.append(main_df)
            main_id = main_row.get('movie_id')  # Assume movie_id is primary key

            # Transform related tables
            for table_type, table_configs in configs.items():
                if table_type == 'simple':
                    continue

                for table_config in table_configs:
                    try:
                        if table_type == 'one_to_one':
                            result = self._transform_one_to_one(doc, table_config, main_id)
                        elif table_type == 'nested_objects':
                            result = self._transform_nested_objects(doc, table_config, main_id)
                        elif table_type == 'arrays':
                            result = self._transform_arrays(doc, table_config, main_id)
                        else:
                            continue

                        # Collect results
                        for table_name, df_data in result.items():
                            if table_name not in related_results:
                                related_results[table_name] = []
                            if not df_data.empty:
                                related_results[table_name].append(df_data)

                    except Exception as e:
                        logger.error(f"Error transforming {table_config.name}: {e}")

        # Combine results
        main_df = pd.concat(main_results, ignore_index=True) if main_results else pd.DataFrame()
        final_related = {
            name: pd.concat(dfs, ignore_index=True)
            for name, dfs in related_results.items()
            if dfs
        }

        return main_df, final_related

    def _parse_configs(self, config: Dict) -> Dict[str, List[TableConfig]]:
        """Parse YAML config into structured TableConfig objects"""
        configs = {'simple': [], 'one_to_one': [], 'nested_objects': [], 'arrays': []}

        mappings = config.get('mappings', {})

        # Simple fields
        simple_fields = [FieldMapping(**field) for field in mappings.get('simple_fields', [])]
        configs['simple'] = simple_fields

        # One-to-one relationships
        for name, cfg in mappings.get('one_to_one', {}).items():
            fields = [FieldMapping(**field) for field in cfg.get('fields', [])]
            table_config = TableConfig(
                name=cfg.get('table', name),
                fields=fields,
                foreign_key='movie_id'  # Standard foreign key
            )
            configs['one_to_one'].append(table_config)

        # Nested objects
        for name, cfg in mappings.get('nested_objects', {}).items():
            fields = [FieldMapping(**field) for field in cfg.get('fields', [])]
            table_config = TableConfig(
                name=cfg.get('table', name),
                fields=fields,
                source_path=cfg.get('source_path'),
                foreign_key='movie_id'
            )
            configs['nested_objects'].append(table_config)

        # Arrays (many-to-many)
        for name, cfg in mappings.get('arrays', {}).items():
            fields = [FieldMapping(**field) for field in cfg.get('fields', [])]
            relation_keys = cfg.get('relation_keys', {})
            table_config = TableConfig(
                name=cfg.get('table', name),
                fields=fields,
                junction_table=cfg.get('junction_table'),
                junction_left_key=relation_keys.get('left_key', 'movie_id'),
                junction_right_key=relation_keys.get('right_key')
            )
            configs['arrays'].append(table_config)

        return configs

    def _transform_simple_fields(self, doc: Dict, fields: List[FieldMapping]) -> Dict:
        """Transform simple fields for main table"""
        result = {}
        for field in fields:
            value = self.extractor.extract(doc, field.source)
            if value is not None:
                # Special handling for _id
                if field.source == '_id' or field.source == 'id':
                    value = str(value)
                result[field.target] = value
            elif field.default_value is not None:
                result[field.target] = field.default_value
        return result

    def _transform_one_to_one(self, doc: Dict, config: TableConfig, main_id: Any) -> Dict[str, pd.DataFrame]:
        """Transform one-to-one relationships"""
        result = {}
        has_data = False

        for field in config.fields:
            value = self.extractor.extract(doc, field.source)
            if value is not None:
                result[field.target] = value
                has_data = True
            elif field.default_value is not None:
                result[field.target] = field.default_value

        if has_data:
            if config.foreign_key:
                result[config.foreign_key] = main_id
            return {config.name: pd.DataFrame([result])}

        return {}

    def _transform_nested_objects(self, doc: Dict, config: TableConfig, main_id: Any) -> Dict[str, pd.DataFrame]:
        """Transform nested objects (one-to-many)"""
        if not config.source_path:
            return {}

        nested_items = self.extractor.extract(doc, config.source_path)
        if not isinstance(nested_items, list):
            return {}

        results = []
        for item in nested_items:
            if not isinstance(item, dict):
                continue

            row = {}
            for field in config.fields:
                # Extract field name from source (remove path prefix)
                field_name = field.source.split('.')[-1]
                value = item.get(field_name)

                if value is not None:
                    row[field.target] = value
                elif field.default_value is not None:
                    row[field.target] = field.default_value

            if row:
                if config.foreign_key:
                    row[config.foreign_key] = main_id
                results.append(row)

        if results:
            return {config.name: pd.DataFrame(results)}
        return {}

    def _transform_arrays(self, doc: Dict, config: TableConfig, main_id: Any) -> Dict[str, pd.DataFrame]:
        """Transform arrays (many-to-many relationships)"""
        results = {}

        # Get the array path from the first field (remove [].field_name part)
        if not config.fields:
            return results

        first_field = config.fields[0]
        if '[]' not in first_field.source:
            return results

        array_path = first_field.source.split('[]')[0]
        array_items = self.extractor.extract(doc, array_path)

        if not isinstance(array_items, list):
            return results

        main_results = []
        junction_results = []

        for item in array_items:
            if not isinstance(item, dict):
                continue

            row = {}
            primary_key_value = None

            # Extract all fields for this item
            for field in config.fields:
                field_name = field.source.split('[].')[-1] if '[].' in field.source else field.source.split('[]')[-1]
                value = item.get(field_name)

                if value is not None:
                    row[field.target] = value

                    # Track primary key for junction table
                    if field.target == config.junction_right_key:
                        primary_key_value = value
                elif field.default_value is not None:
                    row[field.target] = field.default_value
                elif field.required:
                    # Skip this item if required field is missing
                    logger.debug(f"Skipping item in {config.name}: missing required field {field.target}")
                    row = {}
                    break

            # Only add if we have valid data and all required fields
            if row and primary_key_value is not None:
                main_results.append(row)

                # Create junction table entry
                if config.junction_table and config.junction_left_key and config.junction_right_key:
                    junction_results.append({
                        config.junction_left_key: main_id,
                        config.junction_right_key: primary_key_value
                    })

        if main_results:
            results[config.name] = pd.DataFrame(main_results).drop_duplicates()

        if junction_results and config.junction_table:
            results[config.junction_table] = pd.DataFrame(junction_results).drop_duplicates()

        return results

# =====================================================
# 4. SIMPLIFIED LOADER
# =====================================================

class OptimizedLoader:
    def __init__(self, engine):
        self.engine = engine
        self.existing_ids = {}
        self._load_existing_ids()

    def _load_existing_ids(self):
        """Load existing IDs to avoid duplicates"""
        tables_with_ids = {
            'movies': 'movie_id',
            'genres': 'genre_id',
            'production_companies': 'company_id',
            'production_countries': 'iso_3166_1',
            'spoken_languages': 'iso_639_1',
            'collections': 'collection_id'
        }

        for table, pk in tables_with_ids.items():
            try:
                existing = pd.read_sql(f"SELECT {pk} FROM {table}", self.engine)[pk].dropna()
                self.existing_ids[table] = set(existing)
                logger.info(f"Loaded {len(existing)} existing IDs for {table}")
            except Exception as e:
                logger.warning(f"Could not load existing IDs for {table}: {e}")
                self.existing_ids[table] = set()

    def load(self, main_df: pd.DataFrame, related_dfs: Dict[str, pd.DataFrame], main_table: str):
        """Load data with proper order and deduplication"""

        # Load order to respect foreign keys
        load_order = [
            'movies', 'collections', 'genres', 'production_companies',
            'production_countries', 'spoken_languages', 'release_calendar',
            'trailers', 'movie_genres', 'movie_production_companies',
            'movie_production_countries', 'movie_spoken_languages'
        ]

        # Load main table first
        if not main_df.empty:
            filtered_main = self._filter_duplicates(main_df, main_table)
            if not filtered_main.empty:
                self._insert_data(filtered_main, main_table)
                # Update existing IDs
                if main_table in self.existing_ids:
                    pk_col = 'movie_id'  # Assuming movies is main table
                    new_ids = set(filtered_main[pk_col].dropna())
                    self.existing_ids[main_table].update(new_ids)

        # Load related tables in order
        for table in load_order:
            if table != main_table and table in related_dfs:
                df = related_dfs[table]
                if not df.empty:
                    filtered_df = self._filter_duplicates(df, table)
                    if not filtered_df.empty:
                        self._insert_data(filtered_df, table)

    def _filter_duplicates(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        """Filter out existing records"""
        if table not in self.existing_ids:
            return df.drop_duplicates()

        # Get primary key column
        pk_cols = {
            'movies': 'movie_id',
            'genres': 'genre_id',
            'production_companies': 'company_id',
            'production_countries': 'iso_3166_1',
            'spoken_languages': 'iso_639_1',
            'collections': 'collection_id'
        }

        pk_col = pk_cols.get(table)
        if not pk_col or pk_col not in df.columns:
            return df.drop_duplicates()

        # Filter out existing IDs
        existing = self.existing_ids[table]
        mask = ~df[pk_col].isin(existing)
        filtered = df[mask].drop_duplicates(subset=[pk_col])

        logger.info(f"Filtered {len(df) - len(filtered)} duplicates from {table}")
        return filtered

    def _insert_data(self, df: pd.DataFrame, table: str):
        """Insert data into PostgreSQL"""
        try:
            # Filter valid columns
            valid_cols = {col['name'] for col in inspect(self.engine).get_columns(table)}
            df_filtered = df[[col for col in df.columns if col in valid_cols]]

            # Remove rows with null values in required columns
            required_columns = {
                'genres': ['name'],
                'production_companies': ['name'],
                'production_countries': ['name'],
                'spoken_languages': ['name'],
                'movies': ['title', 'original_title']
            }

            if table in required_columns:
                for col in required_columns[table]:
                    if col in df_filtered.columns:
                        initial_count = len(df_filtered)
                        df_filtered = df_filtered.dropna(subset=[col])
                        dropped_count = initial_count - len(df_filtered)
                        if dropped_count > 0:
                            logger.warning(f"Dropped {dropped_count} rows from {table} due to null {col}")

            if df_filtered.empty:
                logger.info(f"No valid data to insert into {table}")
                return

            df_filtered.to_sql(table, self.engine, if_exists='append', index=False, method='multi')
            logger.info(f"Inserted {len(df_filtered)} records into {table}")

        except Exception as e:
            logger.error(f"Failed to insert into {table}: {e}")
            # Try inserting row by row for better error isolation
            self._insert_row_by_row(df, table)

    def _insert_row_by_row(self, df: pd.DataFrame, table: str):
        """Insert data row by row when batch insert fails"""
        valid_cols = {col['name'] for col in inspect(self.engine).get_columns(table)}
        df_filtered = df[[col for col in df.columns if col in valid_cols]]

        success_count = 0
        for idx, row in df_filtered.iterrows():
            try:
                pd.DataFrame([row]).to_sql(table, self.engine, if_exists='append', index=False)
                success_count += 1
            except Exception as e:
                logger.warning(f"Failed to insert row {idx} into {table}: {e}")
                logger.debug(f"Failed row data: {row.to_dict()}")

        if success_count > 0:
            logger.info(f"Inserted {success_count} records into {table} (row-by-row)")
            # Try inserting row by row for better error isolation
            self._insert_row_by_row(df, table)

# =====================================================
# 5. SIMPLIFIED PIPELINE
# =====================================================

class SimplifiedETLPipeline:
    def __init__(self, mongo_collection: Collection, postgres_engine):
        self.mongo_collection = mongo_collection
        self.postgres_engine = postgres_engine
        self.transformer = UnifiedTransformer()
        self.loader = OptimizedLoader(postgres_engine)

    def run(self, config_path: str, batch_size: int = 1000):
        """Run the ETL pipeline"""
        logger.info("Starting ETL Pipeline")

        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Extract and process in batches
        cursor = self.mongo_collection.find().batch_size(batch_size)
        batch = []

        for doc in cursor:
            batch.append(doc)

            if len(batch) >= batch_size:
                self._process_batch(batch, config)
                batch = []

        # Process remaining batch
        if batch:
            self._process_batch(batch, config)

        logger.info("ETL Pipeline completed successfully")

    def _process_batch(self, batch: List[Dict], config: Dict):
        """Process a single batch"""
        df = pd.DataFrame(batch)
        main_df, related_dfs = self.transformer.transform_batch(df, config)
        self.loader.load(main_df, related_dfs, config['main_table'])

# =====================================================
# 6. USAGE EXAMPLE
# =====================================================

def main():
    from Data_Pipeline.config.connection import MongoConnection, PostgresConnection

    # Initialize connections
    mongo = MongoConnection("mongodb://localhost:27017", "tmdb_data", "raw_movies")
    postgres = PostgresConnection("movie_db", "postgres", "141124", "localhost", 5432)

    # Create pipeline
    pipeline = SimplifiedETLPipeline(mongo.coll, postgres.engine)

    try:
        pipeline.run("Data_Pipeline/config/transform_config.yaml")
    finally:
        mongo.close()
        postgres.dispose()

if __name__ == "__main__":
    main()
