# --- DuplicateRemover: loại bỏ bản ghi đã tồn tại trong database ---
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging

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
    """JSON path extraction """
    
    def safe_extract(self, doc: Dict, path: str) -> Any:
        try:
            return self._extract_nested_field(doc, path)
        except Exception as e:
            logger.warning(f"Failed to extract path '{path}': {e}")
            return None
    
    def _extract_nested_field(self, doc: Dict, path: str) -> Any:
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
    

class DuplicateRemover:
    """Loại bỏ các bản ghi trùng lặp với dữ liệu đã có trong database."""
    def __init__(self, pg_engine):
        self.pg_engine = pg_engine

    def remove_existing(self, df: pd.DataFrame, table_name: str, key_column: str) -> pd.DataFrame:
        """Loại bỏ các bản ghi đã tồn tại trong bảng theo key_column."""
        try:
            existing_keys = pd.read_sql(f"SELECT {key_column} FROM {table_name}", self.pg_engine)[key_column].tolist()
            filtered_df = df[~df[key_column].isin(existing_keys)]
            logger.info(f"Đã loại bỏ {len(df) - len(filtered_df)} bản ghi trùng lặp với bảng {table_name}.")
            return filtered_df
        except Exception as e:
            logger.error(f"ERORR: Lỗi khi kiểm tra trùng lặp với bảng {table_name}: {e}")
            return df