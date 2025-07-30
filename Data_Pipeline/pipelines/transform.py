from typing import Dict, List, Any, Optional
import pandas as pd
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FieldMapping:
    source: str
    target: str
    data_type: Optional[str] = None
    default_value: Any = None
    required: bool = False
    nullable: Optional[bool] = None

@dataclass
class TableMapping:
    table_name: str
    fields: List[FieldMapping]
    foreign_key: Optional[str] = None
    primary_key: Optional[str] = None
    source_path: Optional[str] = None
    junction_table: Optional[str] = None
    junction_config: Optional[Dict] = None

class DataExtractor:
    def safe_extract(self, doc: Dict, path: str) -> Any:
        try:
            if not path:
                return doc

            parts = path.replace("[]", ".[]").split(".")
            current = doc

            for part in parts:
                if not current:
                    return None

                if part == "[]":
                    if not isinstance(current, list):
                        return []
                    continue

                if isinstance(current, list):
                    if part.isdigit():
                        idx = int(part)
                        current = current[idx] if 0 <= idx < len(current) else None
                    else:
                        current = [item.get(part) for item in current if isinstance(item, dict)]
                elif isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None

            return current
        except Exception as e:
            logger.warning(f"Failed to extract path '{path}': {e}")
            return None

class DataTransformer:
    def __init__(self, extractor: DataExtractor):
        self.extractor = extractor

    def transform_array(self, data: Dict, config: TableMapping, main_id: Any) -> Dict[str, List[Dict]]:
        array_path = config.source_path or config.fields[0].source.split("[]")[0]
        items = self.extractor.safe_extract(data, array_path)

        if not isinstance(items, list):
            return {}

        main_results = []
        junction_results = []

        for item in items:
            if not isinstance(item, dict):
                continue

            row = {}
            valid_row = True

            for field in config.fields:
                field_path = field.source.split("[]")[-1].lstrip(".")
                value = item.get(field_path)

                if value is not None:
                    row[field.target] = value
                elif field.default_value is not None:
                    row[field.target] = field.default_value
                elif field.required:
                    valid_row = False
                    break

            if not valid_row or not row:
                continue

            main_results.append(row)

            if config.junction_config:
                junction_results.append({
                    config.junction_config['left_key']: main_id,
                    config.junction_config['right_key']: row.get(config.junction_config['right_key'])
                })

        result = {}
        if main_results:
            result[config.table_name] = pd.DataFrame(main_results)
        if junction_results:
            result[config.junction_table] = pd.DataFrame(junction_results)

        return result

    def transform_simple(self, data: Dict, config: TableMapping) -> pd.DataFrame:
        result = {}
        for field in config.fields:
            value = self.extractor.safe_extract(data, field.source)
            if value is not None:
                result[field.target] = value
            elif field.default_value is not None:
                result[field.target] = field.default_value
        return pd.DataFrame([result]) if result else pd.DataFrame()

class TransformationEngine:
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer(self.extractor)

    def transform_batch(self, df: pd.DataFrame, config: Dict) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        results = {'main': [], 'related': {}}

        for _, row in df.iterrows():
            data = row.to_dict()

            # Transform main table
            main_fields = [FieldMapping(**f) for f in config['mappings']['simple_fields']]
            main_config = TableMapping(table_name=config['main_table'], fields=main_fields)
            main_df = self.transformer.transform_simple(data, main_config)

            if main_df.empty:
                continue

            results['main'].append(main_df)
            main_id = main_df.iloc[0][config.get('primary_key', 'movie_id')]

            # Transform related tables
            for table_type in ['arrays']:
                if table_type not in config['mappings']:
                    continue

                for table_name, table_config in config['mappings'][table_type].items():
                    fields = [FieldMapping(**f) for f in table_config['fields']]
                    mapping = TableMapping(
                        table_name=table_config.get('table_name', table_name),
                        fields=fields,
                        source_path=table_config.get('source_path'),
                        junction_table=table_config.get('junction_table'),
                        junction_config=table_config.get('relation_keys')
                    )

                    transformed = self.transformer.transform_array(data, mapping, main_id)
                    for k, v in transformed.items():
                        if k not in results['related']:
                            results['related'][k] = []
                        results['related'][k].append(v)

        # Combine results
        main_df = pd.concat(results['main'], ignore_index=True) if results['main'] else pd.DataFrame()
        related_dfs = {
            k: pd.concat(v, ignore_index=True) for k, v in results['related'].items()
            if v and not all(df.empty for df in v)
        }

        return main_df, related_dfs
