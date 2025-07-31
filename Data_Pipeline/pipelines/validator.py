from typing import Dict, List
import logging
import yaml
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, engine: Engine = None):
        self.engine = engine
        self._duplicate_cache = {}

    def validate_config(self, config: Dict) -> None:
        """Validate configuration structure and required fields"""
        required_keys = ['main_table', 'mappings']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        mappings = config['mappings']
        if 'simple_fields' not in mappings:
            raise ValueError("Missing simple_fields in mappings")

        for field in mappings['simple_fields']:
            if 'source' not in field or 'target' not in field:
                raise ValueError(f"Invalid field mapping: {field}")

    def check_duplicates(self, df: pd.DataFrame, table_name: str, key_columns: List[str]) -> pd.DataFrame:
        """Check for duplicates based on specified columns"""
        if df.empty:
            return df

        # Create cache key
        cache_key = f"{table_name}_{','.join(key_columns)}"

        # Check if we need to update cache
        if cache_key not in self._duplicate_cache and self.engine is not None:
            try:
                query = f"SELECT DISTINCT {', '.join(key_columns)} FROM {table_name}"
                existing = pd.read_sql(query, self.engine)
                self._duplicate_cache[cache_key] = existing[key_columns].to_dict('records')
                logger.info(f"Cached {len(existing)} existing records for {table_name}")
            except Exception as e:
                logger.warning(f"Could not load existing records for {table_name}: {e}")
                self._duplicate_cache[cache_key] = []

        # Remove duplicates within the current DataFrame
        df = df.drop_duplicates(subset=key_columns, keep='first')

        # Remove duplicates against cached data
        if cache_key in self._duplicate_cache:
            existing_records = self._duplicate_cache[cache_key]
            if existing_records:
                df = df[~df[key_columns].apply(tuple, axis=1).isin(
                    [tuple(x[col] for col in key_columns) for x in existing_records]
                )]

        return df

    def validate_required_fields(self, df: pd.DataFrame, required_fields: List[str]) -> pd.DataFrame:
        """Remove rows with missing required fields"""
        if not df.empty and required_fields:
            return df.dropna(subset=required_fields)
        return df

def load_and_validate(path: str, validator: DataValidator = None) -> Dict:
    """Load config and validate it"""
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if validator:
        validator.validate_config(cfg)
    return cfg

