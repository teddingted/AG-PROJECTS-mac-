"""
news_crawler.py - 조선업 뉴스 크롤러 (v2 - 3카테고리 구조)

category:
  ko_company  → 한국 조선 3사 (한화오션, 삼성중공업, HD현대중공업·미포·삼호·KSOE)
  ko_policy   → 조선 정책 (해양수산부, IMO, 한국 정부 조선산업)
  international → MASGA·국제 조선 뉴스 (gCaptain, Marine Log, Maritime Executive)
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import upsert_news

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def _get(url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return BeautifulSoup(r.text, "lxml")
    except Exception as e:
        print(f"[NEWS] fetch error ({url}): {e}")
        return None

def _extract(soup: BeautifulSoup, selectors: list, base_url: str, source: str, lang: str, category: str, limit: int = 20) -> list:
    """공통 추출 로직 - 헤드라인 위주 (summary 생략으로 경량화)"""
    items = []
    for sel in selectors:
        articles = soup.select(sel)
        if not articles:
            continue
        for art in articles[:limit]:
            title_el = art.select_one("h1,h2,h3,h4,.title,.entry-title,.headline,.subject")
            link_el = art.select_one("a[href]")
            date_el = art.select_one("time,.date,.regdate,.entry-date,.published")
            if not title_el or not link_el:
                # title_el이 a 태그일 수도
                if art.name == "a" and art.get_text(strip=True):
                    link_el = art
                    title_el = art
                else:
                    continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
            title = title_el.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            items.append({
                "title": title,
                "summary": "",  # 헤드라인 위주로 summary 생략
                "url": href,
                "source": source,
                "language": lang,
                "category": category,
                "published_at": date_el.get_text(strip=True)[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
            })
        if items:
            break
    return items


# ══════════════════════════════════════════════
# 카테고리 1: 🇰🇷 ko_company - 조선 3사 뉴스
# ══════════════════════════════════════════════

def crawl_ko_company_gnews() -> list:
    """Google News RSS - 한국 조선 3사 뉴스 (한화오션/삼성중공업/HD현대 신뢰할 수 있는 소스)"""
    import xml.etree.ElementTree as ET
    items = []
    queries = [
        ("한화오션", "한화오션"),
        ("삼성중공업", "삼성중공업"),
        ("HD현대중공업 OR HD한국조선해양", "HD현대"),
        ("현대미포조선 OR 현대삼호중공업", "현대미포·삼호"),
    ]
    from urllib.parse import quote
    for q, label in queries:
        url = f"https://news.google.com/rss/search?q={quote(q)}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:8]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                if title_el is None or link_el is None:
                    continue
                title = title_el.text or ""
                # 광고/스포츠 등 비관련 제거
                if any(kw in title for kw in ["경기", "야구", "축구", "주가", "증시"]):
                    continue
                pub = (pub_el.text or "")[:16] if pub_el is not None else datetime.now().strftime("%Y-%m-%d")
                items.append({
                    "title": f"[{label}] {title}",
                    "summary": "",
                    "url": link_el.text or "",
                    "source": f"{label} (구글뉴스)",
                    "language": "ko",
                    "category": "ko_company",
                    "published_at": pub[:10],
                })
        except Exception as e:
            print(f"[NEWS] Google News RSS ({label}): {e}")
    print(f"[NEWS] Google News 조선3사: {len(items)} articles")
    return items



def crawl_maritime_korea() -> list:
    """해양한국 - 국내 조선 전문지 (ko_company)"""
    items = []
    for url in ["http://www.monthlymaritimekorea.com/news/articleList.html", "http://www.monthlymaritimekorea.com/"]:
        soup = _get(url)
        if not soup:
            continue
        articles = soup.select(".article-list li, article, .news-list li")
        for art in articles[:20]:
            title_el = art.select_one("a, h3, h4, .title")
            link_el = art.select_one("a[href]")
            date_el = art.select_one(".date, time")
            if not title_el or not link_el:
                continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = "http://www.monthlymaritimekorea.com" + href
            title = title_el.get_text(strip=True)
            if len(title) < 5:
                continue
            items.append({
                "title": title, "summary": "", "url": href,
                "source": "해양한국", "language": "ko",
                "category": "ko_company",
                "published_at": date_el.get_text(strip=True)[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
            })
        if items:
            break
    print(f"[NEWS] 해양한국: {len(items)} articles")
    return items


# ══════════════════════════════════════════════
# 카테고리 2: 📋 ko_policy - 조선 정책 뉴스
# ══════════════════════════════════════════════

def crawl_mof_policy() -> list:
    """해양수산부 보도자료 - 조선산업 정책"""
    items = []
    for url in [
        "https://www.mof.go.kr/doc/ko/selectDoc.do?bbsId=PRESS_RELEASE&menuSeq=971",
        "https://www.mof.go.kr/doc/ko/selectDoc.do?bbsId=PRESS_RELEASE",
    ]:
        soup = _get(url)
        if not soup:
            continue
        rows = soup.select("table tbody tr, .board-list li, article")
        count = 0
        for row in rows[:30]:
            title_el = row.select_one("a, .title, h3, td.subject")
            link_el = row.select_one("a[href]")
            date_el = row.select_one("td.date, .date, time")
            if not title_el or not link_el:
                continue
            title = title_el.get_text(strip=True)
            # 조선 관련 필터
            if not any(kw in title for kw in ["조선", "선박", "해운", "LNG", "항만", "해양"]):
                continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = "https://www.mof.go.kr" + href
            items.append({
                "title": f"[해양수산부] {title}",
                "summary": "", "url": href,
                "source": "해양수산부", "language": "ko",
                "category": "ko_policy",
                "published_at": date_el.get_text(strip=True)[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
            })
            count += 1
            if count >= 10:
                break
        if items:
            break
    print(f"[NEWS] 해양수산부: {len(items)} articles")
    return items


def crawl_ko_policy_gnews() -> list:
    """Google News RSS - 조선 정책 뉴스 (해양수산부/산업부 접근 불가 시 폴백)"""
    import xml.etree.ElementTree as ET
    items = []
    queries = [
        ("조선업 정책 OR 조선 지원 OR 선박 수출 지원", "조선정책"),
        ("LNG 선박 정책 OR 해양 정책 OR IMO 조선", "해양정책"),
        ("MASGA OR Make American Shipbuilding OR US shipbuilding policy", "MASGA정책"),
    ]
    from urllib.parse import quote
    for q, label in queries:
        url = f"https://news.google.com/rss/search?q={quote(q)}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:6]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                if title_el is None or link_el is None:
                    continue
                title = title_el.text or ""
                pub = (pub_el.text or "")[:16] if pub_el is not None else datetime.now().strftime("%Y-%m-%d")
                items.append({
                    "title": f"[{label}] {title}",
                    "summary": "",
                    "url": link_el.text or "",
                    "source": f"{label} (구글뉴스)",
                    "language": "ko",
                    "category": "ko_policy",
                    "published_at": pub[:10],
                })
        except Exception as e:
            print(f"[NEWS] Google News RSS Policy ({label}): {e}")
    print(f"[NEWS] Google News 정책: {len(items)} articles")
    return items



# ══════════════════════════════════════════════
# 카테고리 3: 🌍 international - MASGA/국제 뉴스
# ══════════════════════════════════════════════

def crawl_gcaptain() -> list:
    """gCaptain - MASGA 포함 국제 조선/해운 뉴스"""
    items = []
    for url in [
        "https://gcaptain.com/category/shipbuilding/",
        "https://gcaptain.com/",
    ]:
        soup = _get(url)
        if not soup:
            continue
        articles = soup.select("article, .post, .entry")
        for art in articles[:25]:
            title_el = art.select_one("h2, h3, .entry-title, .post-title")
            link_el = art.select_one("a[href]")
            date_el = art.select_one("time, .entry-date, .published")
            if not title_el or not link_el:
                continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = "https://gcaptain.com" + href
            title = title_el.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            # MASGA 태그 자동 부여
            is_masga = any(kw in title.lower() for kw in ["american", "usa", "u.s.", "trump", "masga", "executive order", "jones act"])
            items.append({
                "title": ("🇺🇸 [MASGA] " if is_masga else "") + title,
                "summary": "", "url": href,
                "source": "gCaptain", "language": "en",
                "category": "international",
                "published_at": date_el.get("datetime", "")[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
            })
        if items:
            break
    print(f"[NEWS] gCaptain: {len(items)} articles")
    return items


def crawl_marine_log() -> list:
    """Marine Log - 미국 조선/해운 업계지"""
    items = []
    for url in ["https://www.marinelog.com/news/", "https://www.marinelog.com/"]:
        soup = _get(url)
        if not soup:
            continue
        articles = soup.select("article, .post, .entry")
        for art in articles[:20]:
            title_el = art.select_one("h2, h3, .entry-title")
            link_el = art.select_one("a[href]")
            date_el = art.select_one("time, .entry-date")
            if not title_el or not link_el:
                continue
            href = link_el.get("href", "")
            title = title_el.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            is_masga = any(kw in title.lower() for kw in ["american", "u.s.", "trump", "shipbuilding act", "masga"])
            items.append({
                "title": ("🇺🇸 [MASGA] " if is_masga else "") + title,
                "summary": "", "url": href,
                "source": "Marine Log", "language": "en",
                "category": "international",
                "published_at": date_el.get("datetime", "")[:10] if date_el else datetime.now().strftime("%Y-%m-%d"),
            })
        if items:
            break
    print(f"[NEWS] Marine Log: {len(items)} articles")
    return items


def crawl_maritime_executive() -> list:
    """Maritime Executive - 국제 조선/해운"""
    items = []
    for url in ["https://maritime-executive.com/article", "https://maritime-executive.com"]:
        soup = _get(url)
        if not soup:
            continue
        articles = soup.select("article, .card, .story-item")
        for art in articles[:20]:
            title_el = art.select_one("h2, h3, .card-title, .entry-title")
            link_el = art.select_one("a[href]")
            if not title_el or not link_el:
                continue
            href = link_el.get("href", "")
            if not href.startswith("http"):
                href = "https://maritime-executive.com" + href
            title = title_el.get_text(strip=True)
            if not title or len(title) < 10:
                continue
            items.append({
                "title": title, "summary": "", "url": href,
                "source": "Maritime Executive", "language": "en",
                "category": "international",
                "published_at": datetime.now().strftime("%Y-%m-%d"),
            })
        if items:
            break
    print(f"[NEWS] Maritime Executive: {len(items)} articles")
    return items


def run_all() -> int:
    all_items = []
    # 조선 3사 (Google News RSS - 가장 안정적)
    all_items += crawl_ko_company_gnews()
    all_items += crawl_maritime_korea()   # 해양한국 (작동 확인)
    # 정책 (Google News RSS 폴백)
    all_items += crawl_mof_policy()       # 해수부 직접 시도
    all_items += crawl_ko_policy_gnews()  # Google News 폴백
    # 국제 (MASGA 포함)
    all_items += crawl_gcaptain()
    all_items += crawl_marine_log()
    all_items += crawl_maritime_executive()

    saved = upsert_news(all_items)
    print(f"[NEWS] Total new articles saved: {saved}/{len(all_items)}")
    return saved


if __name__ == "__main__":
    from db.database import init_db
    init_db()
    run_all()
