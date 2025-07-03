import psycopg2

import sqlparse
import time
from psycopg2 import OperationalError, ProgrammingError, errors
from Data_Pipeline.config.postgres_config import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USER

def ensure_database_exists():
    try:
        conn = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST)
        conn.close()
    except OperationalError as e:
        if 'does not exist' in str(e):
            print("⚠️ Database chưa tồn tại. Đang tạo...")
            admin_conn = psycopg2.connect(dbname='postgres', user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST)
            admin_conn.autocommit = True
            admin_cur = admin_conn.cursor()
            admin_cur.execute(f"CREATE DATABASE {POSTGRES_DB}")
            admin_cur.close()
            admin_conn.close()
            time.sleep(1.5)
            print("✅ Tạo thành công.")
            time.sleep(2)
        else:
            raise

def run_sql_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        sql_code = f.read()


    conn = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST)
    cur = conn.cursor()

    statements = sqlparse.split(sql_code)
    for stmt in statements:
        stmt_clean = stmt.strip()
        if not stmt_clean:
            continue
        try:
            cur.execute(stmt_clean)
            print(f"✅ OK: {stmt_clean[:60]}...")
            time.sleep(0.5)
        except ProgrammingError as e:
            print(f"❌ SQL Error in: {stmt_clean}")
            print(e)
            conn.rollback()
            break
        except errors.DuplicateTable:
            print(f"⚠️ Table already exists, skipping: {stmt_clean[:60]}...")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            conn.rollback()
            break
    print('DATABASE SET UP THÀNH CÔNG')
    conn.commit()
    cur.close()
    conn.close()

# === CHẠY ===
ensure_database_exists()
run_sql_file("D:\WorkSpace\Do-an-2\Data_Pipeline\database\schema.sql")
