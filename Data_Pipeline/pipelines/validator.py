from typing import Dict
import logging
import yaml
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
# Data_Pipeline/pipelines/config_loader.py


def load_and_validate(path: str) -> Dict:
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    ConfigValidator().validate(cfg)
    return cfg

