"""
database.py - SQLite 데이터 관리 (v2)
추가: news.category, jobs.salary_extracted, my_profile 테이블
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "shipyard_intel.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # 뉴스 테이블 (category 추가)
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            url TEXT UNIQUE NOT NULL,
            source TEXT,
            language TEXT DEFAULT 'ko',
            category TEXT DEFAULT 'international',
            published_at TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    # 기존 테이블에 category 컬럼 추가 (없을 경우)
    try:
        c.execute("ALTER TABLE news ADD COLUMN category TEXT DEFAULT 'international'")
    except Exception:
        pass

    # 기업 테이블
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            description TEXT,
            hq TEXT,
            employees TEXT,
            website TEXT,
            linkedin_url TEXT,
            job_page_url TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # 채용 공고 테이블 (salary_extracted, salary_currency 추가)
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT NOT NULL,
            location TEXT,
            experience TEXT,
            salary TEXT,
            salary_extracted INTEGER DEFAULT 0,
            salary_currency TEXT DEFAULT '',
            url TEXT UNIQUE NOT NULL,
            source TEXT,
            posted_at TEXT,
            fetched_at TEXT DEFAULT (datetime('now'))
        )
    """)
    for col, default in [("salary_extracted", "0"), ("salary_currency", "''")]:
        try:
            c.execute(f"ALTER TABLE jobs ADD COLUMN {col} TEXT DEFAULT {default}")
        except Exception:
            pass

    # 연봉 테이블
    c.execute("""
        CREATE TABLE IF NOT EXISTS salaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT,
            avg_salary TEXT,
            min_salary TEXT,
            max_salary TEXT,
            experience_level TEXT,
            source TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # 내 프로필 테이블 (v2 신규)
    c.execute("""
        CREATE TABLE IF NOT EXISTS my_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            linkedin_url TEXT DEFAULT '',
            current_company TEXT DEFAULT '',
            current_title TEXT DEFAULT '',
            experience_years INTEGER DEFAULT 0,
            education TEXT DEFAULT '',
            skills TEXT DEFAULT '',
            target_countries TEXT DEFAULT '',
            target_roles TEXT DEFAULT '',
            linkedin_headline TEXT DEFAULT '',
            linkedin_experience TEXT DEFAULT '',
            linkedin_skills TEXT DEFAULT '',
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print(f"[DB] v2 Initialized at {DB_PATH}")


def upsert_news(items: list) -> int:
    conn = get_connection()
    c = conn.cursor()
    count = 0
    for item in items:
        try:
            c.execute("""
                INSERT OR IGNORE INTO news (title, summary, url, source, language, category, published_at)
                VALUES (:title, :summary, :url, :source, :language, :category, :published_at)
            """, item)
            if c.rowcount > 0:
                count += 1
        except Exception as e:
            print(f"[DB] news upsert error: {e}")
    conn.commit()
    conn.close()
    return count


def upsert_jobs(items: list) -> int:
    conn = get_connection()
    c = conn.cursor()
    count = 0
    for item in items:
        try:
            c.execute("""
                INSERT OR IGNORE INTO jobs
                  (company, title, location, experience, salary, salary_extracted, salary_currency, url, source, posted_at)
                VALUES
                  (:company, :title, :location, :experience, :salary, :salary_extracted, :salary_currency, :url, :source, :posted_at)
            """, item)
            if c.rowcount > 0:
                count += 1
        except Exception as e:
            print(f"[DB] jobs upsert error: {e}")
    conn.commit()
    conn.close()
    return count


def upsert_salaries(items: list):
    conn = get_connection()
    c = conn.cursor()
    for item in items:
        try:
            c.execute("""
                INSERT OR REPLACE INTO salaries
                  (job_title, company, avg_salary, min_salary, max_salary, experience_level, source)
                VALUES (:job_title, :company, :avg_salary, :min_salary, :max_salary, :experience_level, :source)
            """, item)
        except Exception as e:
            print(f"[DB] salaries upsert error: {e}")
    conn.commit()
    conn.close()


def insert_companies(items: list):
    conn = get_connection()
    c = conn.cursor()
    for item in items:
        c.execute("""
            INSERT OR REPLACE INTO companies
              (name, name_en, description, hq, employees, website, linkedin_url, job_page_url)
            VALUES (:name, :name_en, :description, :hq, :employees, :website, :linkedin_url, :job_page_url)
        """, item)
    conn.commit()
    conn.close()


def get_profile() -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM my_profile ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}


def save_profile(data: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM my_profile")
    c.execute("""
        INSERT INTO my_profile
          (linkedin_url, current_company, current_title, experience_years, education,
           skills, target_countries, target_roles, linkedin_headline, linkedin_experience, linkedin_skills)
        VALUES
          (:linkedin_url, :current_company, :current_title, :experience_years, :education,
           :skills, :target_countries, :target_roles, :linkedin_headline, :linkedin_experience, :linkedin_skills)
    """, data)
    conn.commit()
    conn.close()


def fetch_all(table: str, limit: int = 100) -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def fetch_news_by_category(category: str, limit: int = 40) -> list:
    conn = get_connection()
    c = conn.cursor()
    if category == "all":
        c.execute("SELECT * FROM news ORDER BY rowid DESC LIMIT ?", (limit,))
    else:
        c.execute("SELECT * FROM news WHERE category=? ORDER BY rowid DESC LIMIT ?", (category, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def fetch_salary_jobs(limit: int = 80) -> list:
    """salary_extracted=1인 공고 우선 반환"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM jobs
        ORDER BY salary_extracted DESC, rowid DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
