"""
scheduler.py - APScheduler 기반 자동 크롤링 스케줄러
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()


def setup_scheduler():
    from crawlers.news_crawler import run_all as news_run
    from crawlers.company_crawler import run_all as company_run
    from crawlers.salary_crawler import run_all as salary_run

    # 뉴스: 6시간마다
    scheduler.add_job(
        news_run,
        trigger=IntervalTrigger(hours=6),
        id="news_job",
        name="뉴스 크롤링",
        replace_existing=True,
    )

    # 채용/기업: 12시간마다
    scheduler.add_job(
        company_run,
        trigger=IntervalTrigger(hours=12),
        id="company_job",
        name="기업·채용 크롤링",
        replace_existing=True,
    )

    # 연봉: 24시간마다
    scheduler.add_job(
        salary_run,
        trigger=IntervalTrigger(hours=24),
        id="salary_job",
        name="연봉 크롤링",
        replace_existing=True,
    )

    logger.info("✅ Scheduler configured: news(6h) / company(12h) / salary(24h)")
    return scheduler


def get_job_status() -> list[dict]:
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
        })
    return jobs
