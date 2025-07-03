from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MappingType(Enum):
    SIMPLE = "simple_fields"
    ONE_TO_ONE = "one_to_one"
    NESTED_OBJECTS = "nested_objects"
    ARRAYS = "arrays"

@dataclass
class FieldMapping:
    source: str
    target: str
    data_type: Optional[str] = None
    default_value: Any = None

@dataclass
class TableMapping:
    table_name: str
    fields: List[FieldMapping]
    foreign_key: Optional[str] = None
    primary_key: Optional[str] = None

class DataExtractor(ABC):
    @abstractmethod
    def safe_extract(self, doc: Dict, path: str) -> Any:
        pass

class JSONPathExtractor(DataExtractor):
    """Improved JSON path extraction with error handling"""
    
    def safe_extract(self, doc: Dict, path: str) -> Any:
        try:
            return self._extract_nested_field(doc, path)
        except Exception as e:
            logger.warning(f"Failed to extract path '{path}': {e}")
            return None
    
    def _extract_nested_field(self, doc: Dict, path: str) -> Any:
        """Enhanced version with better array handling"""
        if not path or not isinstance(doc, dict):
            return doc
            
        keys = path.replace("[]", ".[]").split(".")
        current = doc
        
        for key in keys:
            if key == "[]":
                return current if isinstance(current, list) else []
            elif isinstance(current, list):
                return [item.get(key) for item in current if isinstance(item, dict) and key in item]
            elif isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        
        return current

class MappingStrategy(ABC):
    @abstractmethod
    def process(self, row_data: Dict, config: TableMapping, main_id: Any) -> Dict[str, List[Dict]]:
        pass

class SimpleFieldStrategy(MappingStrategy):
    def __init__(self, extractor: DataExtractor):
        self.extractor = extractor
    
    def process(self, row_data: Dict, config: TableMapping, main_id: Any) -> Dict[str, List[Dict]]:
        result = {}
        for field in config.fields:
            value = self.extractor.safe_extract(row_data, field.source)
            if field.source == "_id":
                value = str(value)
            result[field.target] = value
        # Nếu có foreign_key, gán main_id vào trường đó
        if config.foreign_key:
            result[config.foreign_key] = main_id
        return {config.table_name: [result]}

class NestedObjectStrategy(MappingStrategy):
    def __init__(self, extractor: DataExtractor):
        self.extractor = extractor
    
    def process(self, row_data: Dict, config: TableMapping, main_id: Any) -> Dict[str, List[Dict]]:
        source_path = getattr(config, 'source_path', '')
        sub_items = self.extractor.safe_extract(row_data, source_path)
        
        if not isinstance(sub_items, list):
            return {}
        
        results = []
        for item in sub_items:
            row = {}
            for field in config.fields:
                row[field.target] = item.get(field.source, field.default_value)
            
            if config.foreign_key:
                row[config.foreign_key] = main_id
            results.append(row)
        
        return {config.table_name: results}

class ArrayStrategy(MappingStrategy):
    def __init__(self, extractor: DataExtractor):
        self.extractor = extractor
    
    def process(self, row_data: Dict, config: TableMapping, main_id: Any) -> Dict[str, List[Dict]]:
        # Extract array items
        array_path = config.fields[0].source.split("[]")[0]
        sub_items = self.extractor.safe_extract(row_data, array_path)
        
        if not isinstance(sub_items, list):
            return {}
        
        main_results = []
        junction_results = []
        
        for item in sub_items:
            # Main table record
            row = {}
            for field in config.fields:
                source_field = field.source.split("[]")[-1].lstrip(".")
                row[field.target] = item.get(source_field, field.default_value)
            main_results.append(row)

            # Junction table record
            junction_config = getattr(config, 'junction_config', None)
            if junction_config:
                right_key = junction_config['right_key']
                junction_row = {
                    junction_config['left_key']: main_id,
                    right_key: row.get(right_key)
                }
                junction_results.append(junction_row)
        
        result = {config.table_name: main_results}
        if junction_results:
            junction_table = getattr(config, 'junction_table', f"{config.table_name}_junction")
            result[junction_table] = junction_results
        
        return result

class TransformationEngine:
    def __init__(self):
        self.extractor = JSONPathExtractor()
        self.strategies = {
            MappingType.SIMPLE: SimpleFieldStrategy(self.extractor),
            MappingType.ONE_TO_ONE: SimpleFieldStrategy(self.extractor),
            MappingType.NESTED_OBJECTS: NestedObjectStrategy(self.extractor),
            MappingType.ARRAYS: ArrayStrategy(self.extractor)
        }
    
    def transform_batch(self, df: pd.DataFrame, config: Dict) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """Vectorized transformation approach"""
        main_table_config = self._parse_main_table_config(config)
        related_configs = self._parse_related_configs(config)
        
        # Process main table - vectorized approach
        main_df = self._process_main_table_vectorized(df, main_table_config)
        
        # Process related tables
        related_dfs = {}
        for mapping_type, table_configs in related_configs.items():
            strategy = self.strategies[mapping_type]
            
            for table_config in table_configs:
                table_results = self._process_related_table(df, table_config, strategy, main_df)
                for table_name, data in table_results.items():
                    if table_name not in related_dfs:
                        related_dfs[table_name] = []
                    related_dfs[table_name].extend(data)
        
        # Convert to DataFrames
        for table_name in related_dfs:
            related_dfs[table_name] = pd.DataFrame(related_dfs[table_name])
        
        return main_df, related_dfs
    
    def _process_main_table_vectorized(self, df: pd.DataFrame, config: TableMapping) -> pd.DataFrame:
        """Use pandas vectorized operations instead of iterrows"""
        result_dict = {}
        
        for field in config.fields:
            if field.source == "_id":
                result_dict[field.target] = df['_id'].astype(str)
            elif '.' in field.source:
                # Handle nested fields
                result_dict[field.target] = df.apply(
                    lambda row: self.extractor.safe_extract(row.to_dict(), field.source), 
                    axis=1
                )
            else:
                result_dict[field.target] = df.get(field.source, field.default_value)
        
        return pd.DataFrame(result_dict)
    
    def _process_related_table(self, df: pd.DataFrame, config: TableMapping, 
                             strategy: MappingStrategy, main_df: pd.DataFrame) -> Dict[str, List[Dict]]:
        all_results = {}

        # Determine the main table primary key name from config
        # Try to get from config.foreign_key (for related table), else default to 'movie_id'
        # But best is to get from main table config
        main_table_pk = None
        if hasattr(main_df, 'columns'):
            # Try to get the first column that ends with '_id', else use the first column
            id_cols = [col for col in main_df.columns if col.endswith('_id')]
            if id_cols:
                main_table_pk = id_cols[0]
            else:
                main_table_pk = main_df.columns[0]
        else:
            main_table_pk = 'movie_id'

        for idx, row in df.iterrows():
            main_id = main_df.iloc[idx].get(main_table_pk)
            row_results = strategy.process(row.to_dict(), config, main_id)

            for table_name, records in row_results.items():
                if table_name not in all_results:
                    all_results[table_name] = []
                all_results[table_name].extend(records)

        return all_results
    
    def _parse_main_table_config(self, config: Dict) -> TableMapping:
        fields = []
        for field_config in config['mappings']['simple_fields']:
            # Map 'type' to 'data_type' for FieldMapping
            field_kwargs = {
                'source': field_config['source'],
                'target': field_config['target'],
                'data_type': field_config.get('type'),
                'default_value': field_config.get('default_value')
            }
            fields.append(FieldMapping(**field_kwargs))
        return TableMapping(table_name=config['main_table'], fields=fields)
    
    def _parse_related_configs(self, config: Dict) -> Dict[MappingType, List[TableMapping]]:
        mappings = config.get("mappings", {})
        related_configs = {}
    
        # Xử lý one_to_one
        if "one_to_one" in mappings:
            one_to_one = []
            for key, val in mappings["one_to_one"].items():
                fields = [
                    FieldMapping(
                        source=f['source'],
                        target=f['target'],
                        data_type=f.get('type'),
                        default_value=f.get('default_value')
                    ) for f in val["fields"]
                ]
                # Lấy foreign_key từ relation nếu có
                foreign_key = None
                if 'relation' in val and 'foreign_key' in val['relation']:
                    foreign_key = val['relation']['foreign_key']
                table = TableMapping(
                    table_name=val.get("table", key),
                    fields=fields,
                    foreign_key=foreign_key,
                    primary_key=val.get("primary_key")
                )
                # Gắn thêm source_path nếu cần (one_to_one thường không cần)
                one_to_one.append(table)
            related_configs[MappingType.ONE_TO_ONE] = one_to_one

        if "nested_objects" in mappings:
            nested = []
            for key, val in mappings["nested_objects"].items():
                # Map 'type' to 'data_type' for each field
                fields = [
                    FieldMapping(
                        source=f['source'],
                        target=f['target'],
                        data_type=f.get('type'),
                        default_value=f.get('default_value')
                    ) for f in val["fields"]
                ]
                # Lấy foreign_key từ relation nếu có
                foreign_key = None
                if 'relation' in val and 'foreign_key' in val['relation']:
                    foreign_key = val['relation']['foreign_key']
                table = TableMapping(
                    table_name=val.get("table_name", key),
                    fields=fields,
                    foreign_key=foreign_key,
                    primary_key=val.get("primary_key")
                )
                # Gắn thêm source_path để extractor dùng
                setattr(table, "source_path", val.get("source_path", key))
                nested.append(table)
            related_configs[MappingType.NESTED_OBJECTS] = nested

        if "arrays" in mappings:
            arrays = []
            for key, val in mappings["arrays"].items():
                # Map 'type' to 'data_type' for each field
                fields = [
                    FieldMapping(
                        source=f['source'],
                        target=f['target'],
                        data_type=f.get('type'),
                        default_value=f.get('default_value')
                    ) for f in val["fields"]
                ]
                table = TableMapping(
                    table_name=val.get("table_name", key),
                    fields=fields,
                    primary_key=val.get("primary_key"),
                )
                # Gắn thêm junction info
                setattr(table, "junction_table", val.get("junction_table"))
                setattr(table, "junction_config", val.get("relation_keys"))
                arrays.append(table)
            related_configs[MappingType.ARRAYS] = arrays

        return related_configs


class ImprovedBatchPipeline:
    def __init__(self, mongo_connection, postgres_connection):
        self.mongo_conn = mongo_connection
        self.postgres_conn = postgres_connection
        self.transformer = TransformationEngine()
        self.validator = ConfigValidator()
    
    def run(self, config_path: str):
        try:
            # Validate config first
            config = self._load_and_validate_config(config_path)
            
            # Extract
            df = self.extract()
            logger.info(f"Extracted {len(df)} records")
            
            # Transform
            main_df, related_dfs = self.transformer.transform_batch(df, config)
            logger.info(f"Transformed data into {len(related_dfs)} related tables")
            
            # Load
            self.load_with_transaction(main_df, related_dfs, config)
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def _load_and_validate_config(self, config_path: str) -> Dict:
        config = self._load_config(config_path)
        self.validator.validate(config)
        return config
    
    def load_with_transaction(self, main_df: pd.DataFrame, 
                            related_dfs: Dict[str, pd.DataFrame], config: Dict):
        """Load data with proper transaction handling"""
        with self.postgres_conn.begin() as trans:
            try:
                # Load main table
                main_df.to_sql(config['main_table'], self.postgres_conn, 
                             if_exists='append', index=False)
                
                # Load related tables in proper order
                load_order = self._determine_load_order(config)
                for table_name in load_order:
                    if table_name in related_dfs:
                        self._load_table_with_upsert(related_dfs[table_name], table_name)
                
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise

class ConfigValidator:
    def validate(self, config: Dict) -> None:
        """Validate configuration structure and required fields"""
        required_keys = ['main_table', 'mappings']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        
        # Validate mappings structure
        mappings = config['mappings']
        if 'simple_fields' not in mappings:
            raise ValueError("Missing simple_fields in mappings")
        
        # Validate each field mapping
        for field in mappings['simple_fields']:
            if 'source' not in field or 'target' not in field:
                raise ValueError(f"Invalid field mapping: {field}")
