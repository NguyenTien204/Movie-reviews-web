# Refactored Transformation Module

from typing import Dict, List, Tuple
import pandas as pd
import logging

from Data_Pipeline.pipelines.extract import (
    JSONPathExtractor,
    SimpleFieldStrategy, NestedObjectStrategy,
    ArrayStrategy, MappingType,
    FieldMapping, TableMapping
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility functions

def parse_field_mappings(fields_cfg: List[Dict]) -> List[FieldMapping]:
    return [
        FieldMapping(
            source=f['source'],
            target=f['target'],
            data_type=f.get('type'),
            default_value=f.get('default_value')
        ) for f in fields_cfg
    ]

def detect_primary_key(df: pd.DataFrame) -> str:
    id_cols = [col for col in df.columns if col.endswith('_id')]
    return id_cols[0] if id_cols else df.columns[0]

# Config Parser Class
class ConfigParser:
    def parse_main_table(self, config: Dict) -> TableMapping:
        fields = parse_field_mappings(config['mappings']['simple_fields'])
        return TableMapping(table_name=config['main_table'], fields=fields)

    def parse_related_configs(self, config: Dict) -> Dict[MappingType, List[TableMapping]]:
        mappings = config.get("mappings", {})
        result = {}

        for key, mapping_type in [
            ("one_to_one", MappingType.ONE_TO_ONE),
            ("nested_objects", MappingType.NESTED_OBJECTS),
            ("arrays", MappingType.ARRAYS)
        ]:
            if key not in mappings:
                continue

            tables = []
            for tbl_key, tbl_cfg in mappings[key].items():
                fields = parse_field_mappings(tbl_cfg['fields'])
                table = TableMapping(
                    table_name=tbl_cfg.get('table_name', tbl_key),
                    fields=fields,
                    primary_key=tbl_cfg.get('primary_key'),
                    foreign_key=tbl_cfg.get('relation', {}).get('foreign_key')
                )
                if 'source_path' in tbl_cfg:
                    setattr(table, 'source_path', tbl_cfg['source_path'])
                if 'junction_table' in tbl_cfg:
                    setattr(table, 'junction_table', tbl_cfg['junction_table'])
                if 'relation_keys' in tbl_cfg:
                    setattr(table, 'junction_config', tbl_cfg['relation_keys'])
                tables.append(table)
            result[mapping_type] = tables

        return result

# Transformer Classes
class MainTableTransformer:
    def __init__(self, extractor: JSONPathExtractor):
        self.extractor = extractor

    def transform(self, df: pd.DataFrame, config: TableMapping) -> pd.DataFrame:
        result = {}
        for field in config.fields:
            if field.source == "_id":
                result[field.target] = df['_id'].astype(str)
            elif '.' in field.source:
                result[field.target] = df.apply(lambda row: self.extractor.safe_extract(row.to_dict(), field.source), axis=1)
            else:
                result[field.target] = df.get(field.source, field.default_value)
        return pd.DataFrame(result)

class RelatedTableTransformer:
    def __init__(self, extractor: JSONPathExtractor):
        self.strategies = {
            MappingType.SIMPLE: SimpleFieldStrategy(extractor),
            MappingType.ONE_TO_ONE: SimpleFieldStrategy(extractor),
            MappingType.NESTED_OBJECTS: NestedObjectStrategy(extractor),
            MappingType.ARRAYS: ArrayStrategy(extractor)
        }

    def transform(self, df: pd.DataFrame, main_df: pd.DataFrame, related_configs: Dict[MappingType, List[TableMapping]]) -> Dict[str, pd.DataFrame]:
        main_pk = detect_primary_key(main_df)
        result = {}

        for mapping_type, tables in related_configs.items():
            strategy = self.strategies[mapping_type]
            for table_cfg in tables:
                collected = []
                for idx, row in df.iterrows():
                    main_id = main_df.iloc[idx][main_pk]
                    records = strategy.process(row.to_dict(), table_cfg, main_id)
                    for tbl_name, recs in records.items():
                        valid = [r for r in recs if any(r.values()) and (tbl_name != 'collections' or r.get('collection_id'))]
                        collected.extend(valid)
                if collected:
                    result[table_cfg.table_name] = pd.DataFrame(collected)

        return result

# Pipeline Controller
class TransformationEngine:
    def __init__(self):
        self.extractor = JSONPathExtractor()
        self.parser = ConfigParser()
        self.main_transformer = MainTableTransformer(self.extractor)
        self.related_transformer = RelatedTableTransformer(self.extractor)

    def transform_batch(self, df: pd.DataFrame, config: Dict) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        main_cfg = self.parser.parse_main_table(config)
        related_cfgs = self.parser.parse_related_configs(config)

        main_df = self.main_transformer.transform(df, main_cfg)
        related_dfs = self.related_transformer.transform(df, main_df, related_cfgs)

        return main_df, related_dfs
