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
    enum: Optional[str] = None

@dataclass
class TableMapping:
    table_name: str
    fields: List[FieldMapping]
    foreign_key: Optional[str] = None
    primary_key: Optional[str] = None
    source_path: Optional[str] = None
    junction_table: Optional[str] = None
    junction_config: Optional[Dict] = None
    relation: Optional[Dict] = None  # Store relation configuration directly

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

    def transform_nested_object(self, data: Dict, config: TableMapping, main_id: Any) -> pd.DataFrame:
        source_path = config.source_path
        if not source_path:
            return pd.DataFrame()

        nested_items = self.extractor.safe_extract(data, source_path)
        if not isinstance(nested_items, list):
            return pd.DataFrame()

        results = []
        for item in nested_items:
            if not isinstance(item, dict):
                continue

            row = {}
            valid_row = True

            for field in config.fields:
                field_name = field.source.split('.')[-1]
                value = item.get(field_name)

                if value is not None:
                    row[field.target] = value
                elif field.default_value is not None:
                    row[field.target] = field.default_value
                elif getattr(field, 'nullable', True) is False:
                    valid_row = False
                    break

            if valid_row and row:
                # Add foreign key from relation config
                if config.relation:
                    foreign_key = config.relation.get('foreign_key')
                    if foreign_key:
                        row[foreign_key] = main_id
                        logger.info(f"Added foreign key {foreign_key}={main_id} for nested object {config.table_name}")
                results.append(row)

        return pd.DataFrame(results)

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

    def transform_one_to_one(self, data: Dict, config: TableMapping, main_id: Any) -> pd.DataFrame:
        result = {}

        # Extract data for collection
        for field in config.fields:
            value = self.extractor.safe_extract(data, field.source)
            if value is not None:
                result[field.target] = value
            elif field.default_value is not None:
                result[field.target] = field.default_value
            elif getattr(field, 'nullable', True) is False:
                return pd.DataFrame()

        # Only process if we have data
        if result:
            # Add foreign key based on relation config
            if config.relation:
                foreign_key = config.relation.get('foreign_key')
                if foreign_key:
                    result[foreign_key] = main_id
                    logger.info(f"Added foreign key {foreign_key}={main_id} for one-to-one table {config.table_name}")

            # Add additional check for belongs_to_collection
            if config.table_name == 'collections':
                collection_id = result.get('collection_id')
                if not collection_id:
                    return pd.DataFrame()
                logger.info(f"Processing collection: {result}")

            return pd.DataFrame([result])
        return pd.DataFrame()

class TransformationEngine:
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer(self.extractor)

    def transform_batch(self, df: pd.DataFrame, config: Dict) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        results = {'main': [], 'related': {}}

        # Pre-process field mappings for better performance
        main_fields = [FieldMapping(**f) for f in config['mappings']['simple_fields']]
        main_config = TableMapping(table_name=config['main_table'], fields=main_fields)

        # Pre-process related table configs
        related_configs = {}
        for table_type in ['arrays', 'one_to_one', 'nested_objects']:
            if table_type not in config['mappings']:
                continue

            for table_name, table_config in config['mappings'][table_type].items():
                fields = [FieldMapping(**f) for f in table_config['fields']]

                # Handle different relation configurations based on table type
                relation = None
                junction_config = None

                if table_type == 'arrays':
                    junction_config = table_config.get('relation_keys')
                else:
                    relation = table_config.get('relation')

                mapping = TableMapping(
                    table_name=table_config.get('table_name', table_name),
                    fields=fields,
                    source_path=table_config.get('source_path'),
                    junction_table=table_config.get('junction_table'),
                    junction_config=junction_config,
                    relation=relation
                )
                related_configs[(table_type, table_name)] = mapping

        # Process each row
        for _, row in df.iterrows():
            data = row.to_dict()

            # Transform main table
            main_df = self.transformer.transform_simple(data, main_config)
            if main_df.empty:
                continue

            results['main'].append(main_df)
            main_id = main_df.iloc[0][config.get('primary_key', 'movie_id')]

            # Transform related tables using pre-processed configs
            for (table_type, table_name), mapping in related_configs.items():
                try:
                    if table_type == 'arrays':
                        transformed = self.transformer.transform_array(data, mapping, main_id)
                        for k, v in transformed.items():
                            if k not in results['related']:
                                results['related'][k] = []
                            if not v.empty:
                                results['related'][k].append(v)

                    elif table_type == 'nested_objects':
                        transformed = self.transformer.transform_nested_object(data, mapping, main_id)
                        if not transformed.empty:
                            if mapping.table_name not in results['related']:
                                results['related'][mapping.table_name] = []
                            results['related'][mapping.table_name].append(transformed)

                    else:  # one_to_one
                        transformed = self.transformer.transform_one_to_one(data, mapping, main_id)
                        if not transformed.empty:
                            if mapping.table_name not in results['related']:
                                results['related'][mapping.table_name] = []
                            results['related'][mapping.table_name].append(transformed)

                except Exception as e:
                    logger.error(f"Error processing {table_type} table {mapping.table_name}: {str(e)}")
                    continue        # Combine results
        main_df = pd.concat(results['main'], ignore_index=True) if results['main'] else pd.DataFrame()
        related_dfs = {
            k: pd.concat(v, ignore_index=True) for k, v in results['related'].items()
            if v and not all(df.empty for df in v)
        }

        return main_df, related_dfs
