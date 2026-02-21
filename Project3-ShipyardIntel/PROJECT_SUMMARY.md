# Project 3: Shipyard Career Intelligence (ShipyardIntel)
> *Comprehensive Portfolio Summary*

## 📌 Project Overview
**ShipyardIntel** is a specialized Career Intelligence dashboard tailored for the shipbuilding industry. The system autonomously crawls and aggregates industry news, corporate information, and salary data. It also integrates a user's LinkedIn profile to provide highly targeted insights and career recommendations.

## 🛠️ Tech Stack & Key Technologies
- **Backend Framework**: Python 3, FastAPI (v2.0.0)
- **Database**: SQLite (`shipyard_intel.db`)
- **Web Crawling**: Requests, BeautifulSoup4 (BS4) for data extraction
- **Task Scheduling**: APScheduler (Automated background scraping)
- **Frontend**: HTML5, Vanilla JavaScript, CSS, Fetch API
- **Integration**: Custom LinkedIn Profile fetching module

## ✨ Performed Tasks & Features
1. **Automated Crawling Engine**: Developed specialized web crawlers (`news_crawler.py`, `company_crawler.py`, `salary_crawler.py`) that run via background threads to collect real-time data on the shipbuilding sector.
2. **API Development**: Built a robust RESTful API using FastAPI, serving endpoints like `/api/news`, `/api/companies`, `/api/jobs`, and `/api/salaries` with dynamic pagination and category filtering.
3. **LinkedIn Integration**: Created a feature to ingest a user's LinkedIn URL (`/api/profile/fetch-linkedin`), parse their professional experience, and match it against the aggregated industry intelligence.
4. **Task Scheduler**: Implemented a background scheduler (`scheduler.py`) to periodically refresh database records so the dashboard is always up-to-date without blocking user requests.
5. **Interactive Dashboard**: Designed a comprehensive single-page application (`dashboard.html`) to visualize market news, salary brackets, hiring companies, and user profiles.

## 📁 Project Structure
- `app.py`: The main FastAPI server and routing definitions.
- `crawlers/`: Dedicated Python scripts handling targeted background scraping.
- `db/`: SQLite database setup and query functions (`database.py`).
- `static/`: Frontend dashboard assets (`dashboard.html`).
- `scheduler.py`: The cron-like job manager for automated updates.

## 📈 Project Outcomes & Achievements
- Engineered a fully automated, standalone market intelligence tool combining web scraping and a modern API backend.
- Streamlined information gathering for professionals in the niche shipbuilding domain.
- Designed a scalable modular architecture that separates the data acquisition layer (crawlers) from the presentation layer (FastAPI & HTML).
