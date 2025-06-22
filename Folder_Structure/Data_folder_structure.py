import os

# Cấu trúc thư mục và file
structure = {
    "movie_data_pipeline": [
        "README.md",
        "requirements.txt",
        ".env",
        {
            "config": [
                "kafka_config.py",
                "spark_config.py",
                "postgres_config.py",
                "tmdb_config.py",
                "mongo_config.py"
            ]
        },
        {
            "kafka": [
                {
                    "producer": [
                        "async_producer.py"
                    ]
                },
                {
                    "consumer": [
                        "spark_stream_consumer.py"
                    ]
                }
            ]
        },
        {
            "tmdb_ingestion": [
                "fetch_tmdb_data.py",
                "backup_to_kafka.py",
                "json_schema.py"
            ]
        },
        {
            "spark_jobs": [
                "clean_transform.py",
                "enrich_data.py",
                "utils.py"
            ]
        },
        {
            "pipelines": [
                "airflow_dag.py",
                "batch_pipeline.py"
            ]
        },
        {
            "database": [
                "schema.sql",
                "init_postgres.py",
                "insert_data.py"
            ]
        },
        {
            "monitoring": [
                "logger.py"
            ]
        },
        {
            "tests": [
                "test_tmdb_fetch.py",
                "test_clean_transform.py",
                "test_kafka_pipeline.py"
            ]
        }
    ]
}


def create_structure(base_path, structure):
    for item in structure:
        if isinstance(item, str):
            # Nếu là file, tạo file rỗng
            file_path = os.path.join(base_path, item)
            open(file_path, 'a').close()
        elif isinstance(item, dict):
            for folder_name, sub_structure in item.items():
                folder_path = os.path.join(base_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                create_structure(folder_path, sub_structure)


# Chạy script
if __name__ == "__main__":
    base_dir = os.getcwd()  # hoặc thay bằng đường dẫn tuyệt đối tùy ý
    root_folder = os.path.join(base_dir, "movie_data_pipeline")
    os.makedirs(root_folder, exist_ok=True)
    create_structure(root_folder, structure["movie_data_pipeline"])
    print(f"Cấu trúc thư mục đã được tạo tại: {root_folder}")
