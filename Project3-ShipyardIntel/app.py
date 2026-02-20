"""
app.py - FastAPI 서버 (v2)
추가: /api/profile GET/POST, /api/profile/fetch-linkedin POST, /api/news?category=... , /api/salary-jobs
"""
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os, threading

from db.database import (
    init_db, fetch_all, fetch_news_by_category, fetch_salary_jobs,
    get_profile, save_profile
)
from crawlers.linkedin_helper import get_all_data
from scheduler import setup_scheduler, scheduler, get_job_status

app = FastAPI(title="조선업 커리어 인텔리전스 v2", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def on_startup():
    init_db()

    def initial_crawl():
        try:
            from crawlers.news_crawler import run_all as news_run
            from crawlers.company_crawler import run_all as company_run
            from crawlers.salary_crawler import run_all as salary_run
            print("[STARTUP] Running initial crawl...")
            company_run()
            salary_run()
            news_run()
            print("[STARTUP] Initial crawl complete!")
        except Exception as e:
            print(f"[STARTUP] Crawl error: {e}")

    threading.Thread(target=initial_crawl, daemon=True).start()
    sched = setup_scheduler()
    sched.start()
    print("[STARTUP] Scheduler started")


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(os.path.join(STATIC_DIR, "dashboard.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# ── 뉴스 (category 파라미터 지원)
@app.get("/api/news")
async def get_news(category: str = "all", limit: int = 60):
    items = fetch_news_by_category(category, limit=limit)
    return {"data": items, "count": len(items)}


# ── 기업
@app.get("/api/companies")
async def get_companies():
    companies = fetch_all("companies", limit=50)
    return {"data": companies, "count": len(companies)}


# ── 채용 공고 (salary_extracted 우선)
@app.get("/api/jobs")
async def get_jobs(limit: int = 60):
    items = fetch_salary_jobs(limit=limit)
    return {"data": items, "count": len(items)}


# ── 연봉
@app.get("/api/salaries")
async def get_salaries():
    items = fetch_all("salaries", limit=200)
    return {"data": items, "count": len(items)}


# ── LinkedIn 추천
@app.get("/api/linkedin")
async def get_linkedin():
    return get_all_data()


# ── 내 프로필 조회
@app.get("/api/profile")
async def get_my_profile():
    profile = get_profile()
    return {"data": profile}


# ── 내 프로필 저장
@app.post("/api/profile")
async def save_my_profile(payload: dict = Body(...)):
    required_fields = [
        "linkedin_url", "current_company", "current_title",
        "experience_years", "education", "skills",
        "target_countries", "target_roles",
        "linkedin_headline", "linkedin_experience", "linkedin_skills",
    ]
    data = {f: payload.get(f, "" if f != "experience_years" else 0) for f in required_fields}
    save_profile(data)
    return {"message": "프로필이 저장되었습니다.", "data": data}


# ── LinkedIn 프로필 자동 수집
@app.post("/api/profile/fetch-linkedin")
async def fetch_linkedin_profile(payload: dict = Body(...)):
    url = payload.get("linkedin_url", "")
    if not url:
        return {"error": "LinkedIn URL이 필요합니다."}
    try:
        from crawlers.linkedin_profile import update_profile_from_linkedin
        result = update_profile_from_linkedin(url)
        return {"message": "LinkedIn 프로필 수집 완료", "data": result}
    except Exception as e:
        return {"error": str(e), "message": "자동 수집 실패. 수동으로 입력해주세요."}


# ── 스케줄러 상태
@app.get("/api/scheduler/status")
async def scheduler_status():
    return {"jobs": get_job_status(), "running": scheduler.running}


# ── 즉시 갱신
@app.post("/api/refresh")
async def refresh_all():
    def run():
        from crawlers.news_crawler import run_all as news_run
        from crawlers.company_crawler import run_all as company_run
        from crawlers.salary_crawler import run_all as salary_run
        company_run(); salary_run(); news_run()

    threading.Thread(target=run, daemon=True).start()
    return {"message": "크롤링 시작됨. 30초 후 새로고침하세요."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
