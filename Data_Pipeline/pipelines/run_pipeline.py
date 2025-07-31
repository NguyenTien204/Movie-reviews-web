# Data_Pipeline/pipelines/run_pipeline.py   (overwrite)
import logging

from Data_Pipeline.pipelines.extract import MongoExtractor
from Data_Pipeline.pipelines.load import PostgresLoader
from Data_Pipeline.pipelines.validator import load_and_validate
from Data_Pipeline.pipelines.transform import TransformationEngine
from Data_Pipeline.config.connection import (
    POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION,
    MongoConnection, PostgresConnection
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('etl_pipeline.log'),
              logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class ModernETLPipeline:
    def __init__(self):
        self.mongo = MongoConnection(
            MONGO_URI, MONGO_DB_NAME, MOVIE_COLLECTION)
        self.postgres = PostgresConnection(
            POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
            POSTGRES_HOST, POSTGRES_PORT)
        self.extractor = MongoExtractor(self.mongo.coll)
        self.loader = PostgresLoader(self.postgres.engine)
        self.transformer = TransformationEngine()

    def run(self, config_path: str) -> None:
        logger.info("=== Starting ETL Pipeline ===")
        cfg = load_and_validate(config_path)

        for batch_df in self.extractor.extract():
            main_df, related_dfs = self.transformer.transform_batch(batch_df, cfg)
            self.loader.load(main_df, related_dfs, cfg['main_table'])

        logger.info("=== ETL Pipeline completed successfully ===")

    def close(self) -> None:
        self.mongo.close()
        self.postgres.dispose()

def main():
    pipeline = ModernETLPipeline()
    try:
        pipeline.run("Data_Pipeline/config/transform_config.yaml")
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
#  python -m Data_Pipeline.pipelines.run_pipeline
