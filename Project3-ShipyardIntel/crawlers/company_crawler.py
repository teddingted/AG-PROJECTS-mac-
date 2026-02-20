"""
company_crawler.py - 조선/LNG 기업 정보 및 채용 크롤러 (v2 - 해외 취업 특화)
사용자 프로필: HD한국조선해양 LNG 액화설비 공정 설계 연구원 (화학공학 석사)
목표: 국내 대비 더 나은 조건의 해외 기업/국가 서치

[해외 핵심 타겟]
- GTT (Gaztransport & Technigaz) - LNG 격납 시스템 글로벌 1위 (프랑스)
- QatarEnergy / QatarEnergy LNG - 세계 최대 LNG 생산국 (카타르)
- Shell / Shell LNG - 글로벌 LNG 선도 메이저 (네덜란드/영국)
- TotalEnergies - 프랑스계 LNG 메이저
- Wärtsilä - LNG 엔진/가스 핸들링 솔루션 (핀란드)
- TechnipFMC - LNG 플랜트 EPC 전문 (프랑스/미국)
- Saipem - 해양 FLNG 건설 EPC (이탈리아)
- Wood Group (John Wood Group) - 과정 설계 컨설팅 (영국)
- Golar LNG - FLNG 선박 운영 (노르웨이)
- Höegh LNG - FSRU 운영 (노르웨이)
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import insert_companies, upsert_jobs

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ──────────────────────────────────────────────
# 기업 데이터 (해외 타겟 + 국내 비교용)
# ──────────────────────────────────────────────
COMPANIES = [
    # ══════════════════════════════
    # 🌍 해외 핵심 타겟 기업
    # ══════════════════════════════
    {
        "name": "GTT (Gaztransport & Technigaz)",
        "name_en": "GTT",
        "description": "⭐ 최우선 타겟. LNG 격납 시스템(Mark III, NO96) 글로벌 1위. 전 세계 LNG선에 탑재되는 기술 원천사. LNG 액화/공정 연구원에게 최적의 해외 커리어. 파리 근교 본사.",
        "hq": "🇫🇷 Saint-Rémy-lès-Chevreuse, France",
        "employees": "약 800명 (소수 정예)",
        "website": "https://www.gtt.fr",
        "linkedin_url": "https://www.linkedin.com/company/gtt-gaztransport-technigaz/",
        "job_page_url": "https://www.gtt.fr/en/careers/",
    },
    {
        "name": "QatarEnergy LNG",
        "name_en": "QatarEnergy LNG",
        "description": "⭐ 최고 연봉 타겟. 세계 최대 LNG 생산국 카타르 국영기업. 면세 고연봉(USD 8,000~15,000/월) + 주거/차량 지원. 공정 엔지니어 상시 채용. 2030 LNG 증산 프로젝트 진행중.",
        "hq": "🇶🇦 Doha, Qatar",
        "employees": "약 11,000명",
        "website": "https://www.qatarenergy.qa",
        "linkedin_url": "https://www.linkedin.com/company/qatarenergy/",
        "job_page_url": "https://careers.qatarenergy.qa/",
    },
    {
        "name": "Shell LNG",
        "name_en": "Shell plc",
        "description": "LNG 글로벌 최대 트레이더 겸 생산자. 세계 각국 LNG 프로젝트 참여. Integrated Gas 부문 LNG 공정 엔지니어 채용. 네덜란드 본사, 싱가포르/카타르/호주 오퍼레이션.",
        "hq": "🇳🇱 The Hague, Netherlands",
        "employees": "약 93,000명",
        "website": "https://www.shell.com",
        "linkedin_url": "https://www.linkedin.com/company/shell/",
        "job_page_url": "https://www.shell.com/careers.html",
    },
    {
        "name": "TotalEnergies",
        "name_en": "TotalEnergies SE",
        "description": "프랑스 에너지 메이저. LNG 공정 엔지니어 채용 활발. 카타르/모잠비크/호주 LNG 프로젝트 주도. 파리 본사 + 글로벌 오퍼레이션. 화학공학 석사 선호.",
        "hq": "🇫🇷 Courbevoie, France",
        "employees": "약 101,000명",
        "website": "https://www.totalenergies.com",
        "linkedin_url": "https://www.linkedin.com/company/totalenergies/",
        "job_page_url": "https://careers.totalenergies.com/",
    },
    {
        "name": "Wärtsilä (가스 솔루션 부문)",
        "name_en": "Wärtsilä Corporation",
        "description": "LNG/가스 핸들링·재기화 시스템 솔루션 전문. LNG 연료공급장치 및 FSRU 관련 기술 개발. 핀란드 본사, 유럽식 워라밸 우수. Process Engineer 채용.",
        "hq": "🇫🇮 Helsinki, Finland",
        "employees": "약 17,000명",
        "website": "https://www.wartsila.com",
        "linkedin_url": "https://www.linkedin.com/company/wartsila/",
        "job_page_url": "https://www.wartsila.com/careers",
    },
    {
        "name": "TechnipFMC",
        "name_en": "TechnipFMC plc",
        "description": "LNG 플랜트 EPC 글로벌 선두. 액화 공정 설계·엔지니어링 전문. Floating LNG(FLNG) 프로젝트 참여. 파리/런던/휴스턴 오퍼레이션. 화학공학 프로세스 엔지니어 채용.",
        "hq": "🇬🇧 London, UK / 🇺🇸 Houston, USA",
        "employees": "약 20,000명",
        "website": "https://www.technipfmc.com",
        "linkedin_url": "https://www.linkedin.com/company/technipfmc/",
        "job_page_url": "https://www.technipfmc.com/en/careers/",
    },
    {
        "name": "Saipem",
        "name_en": "Saipem SpA",
        "description": "이탈리아 해양 건설 EPC. FLNG·해양플랜트 설계·건조 참여. 상시적인 Process Engineer 채용. 중동·아프리카 LNG 프로젝트 다수 수행. 밀라노 본사.",
        "hq": "🇮🇹 San Donato Milanese, Italy",
        "employees": "약 30,000명",
        "website": "https://www.saipem.com",
        "linkedin_url": "https://www.linkedin.com/company/saipem/",
        "job_page_url": "https://www.saipem.com/en/careers",
    },
    {
        "name": "Golar LNG",
        "name_en": "Golar LNG",
        "description": "노르웨이 FLNG(Floating LNG) 개척자. FLNG Hilli 운영 중, 신규 FLNG 프로젝트 추진. 소규모 정예 팀. 오슬로 기반. Process/Liquefaction 엔지니어 채용.",
        "hq": "🇳🇴 Oslo, Norway",
        "employees": "약 600명",
        "website": "https://www.golarlng.com",
        "linkedin_url": "https://www.linkedin.com/company/golar-lng/",
        "job_page_url": "https://www.golarlng.com/career.aspx",
    },
    {
        "name": "Höegh LNG",
        "name_en": "Höegh LNG",
        "description": "노르웨이 FSRU(부유식 재기화선) 세계 선두. LNG 재기화·공급 공정 엔지니어 채용. 워라밸 우수한 노르웨이 근무환경. 에너지 전환 분야 FSRU 수요 증가 중.",
        "hq": "🇳🇴 Oslo, Norway",
        "employees": "약 500명",
        "website": "https://www.hoeghlng.com",
        "linkedin_url": "https://www.linkedin.com/company/hoegh-lng/",
        "job_page_url": "https://www.hoeghlng.com/about/career/",
    },
    {
        "name": "Wood Group (John Wood Group)",
        "name_en": "Wood Group plc",
        "description": "영국 에너지·프로세스 엔지니어링 컨설팅. LNG 플랜트 FEED·기본설계 용역 수행. Process Chemical Engineer 글로벌 채용. 싱가포르/아부다비/런던 허브.",
        "hq": "🇬🇧 Aberdeen, UK",
        "employees": "약 35,000명",
        "website": "https://www.woodplc.com",
        "linkedin_url": "https://www.linkedin.com/company/john-wood-group/",
        "job_page_url": "https://careers.woodplc.com/",
    },
    {
        "name": "MAN Energy Solutions",
        "name_en": "MAN Energy Solutions",
        "description": "독일 선박 엔진 글로벌 1위. 암모니아·LNG·메탄올 이중연료 엔진 개발 중. 공정/연소 엔지니어 채용. 코펜하겐/아우크스부르크 R&D 센터. 친환경 추진 분야 미래 성장성 높음.",
        "hq": "🇩🇪 Augsburg, Germany",
        "employees": "약 14,000명",
        "website": "https://www.man-es.com",
        "linkedin_url": "https://www.linkedin.com/company/man-energy-solutions/",
        "job_page_url": "https://www.man-es.com/company/career",
    },
    {
        "name": "Lloyd's Register (LR)",
        "name_en": "Lloyd's Register",
        "description": "영국 세계 선급. LNG 선박 인증·컨설팅·기술 규정 개발. Process/Safety 엔지니어 채용. 런던 본사 + 전세계 오퍼레이션. 규정·안전 분야 커리어 전환 옵션.",
        "hq": "🇬🇧 London, UK",
        "employees": "약 8,000명",
        "website": "https://www.lr.org",
        "linkedin_url": "https://www.linkedin.com/company/lloyds-register/",
        "job_page_url": "https://www.lr.org/en/careers/",
    },
    # ══════════════════════════════
    # 🏭 국내 비교 기준 기업
    # ══════════════════════════════
    {
        "name": "HD한국조선해양 (현 직장)",
        "name_en": "HD Korea Shipbuilding & Offshore Engineering",
        "description": "[현 직장 - 국내 비교 기준] HD현대 그룹 조선 중간지주사. LNG선 건조 세계 최고 수준. 연구원 평균 연봉 약 5,500~7,500만원. 복지 양호하나 업무 강도 높음.",
        "hq": "🇰🇷 서울시 종로구",
        "employees": "약 500명 (연구소)",
        "website": "https://www.ksoe.co.kr",
        "linkedin_url": "https://www.linkedin.com/company/ksoe-korea-shipbuilding-offshore-engineering/",
        "job_page_url": "https://www.ksoe.co.kr/career",
    },
    {
        "name": "HD현대중공업",
        "name_en": "HD Hyundai Heavy Industries",
        "description": "[국내 비교 기준] 세계 최대 조선소. LNG선 건조 주력. 연구직 평균 연봉 6,500~8,500만원. 직원 13,000명. 울산 소재.",
        "hq": "🇰🇷 울산광역시",
        "employees": "약 13,000명",
        "website": "https://www.hhi.co.kr",
        "linkedin_url": "https://www.linkedin.com/company/hd-hyundai-heavy-industries/",
        "job_page_url": "https://www.hhi.co.kr/en/about/career",
    },
    {
        "name": "삼성중공업",
        "name_en": "Samsung Heavy Industries",
        "description": "[국내 비교 기준] LNG선·FLNG 전문. 연구직 연봉 7,000~9,000만원. 거제 소재. 스마트 조선 기술 선도.",
        "hq": "🇰🇷 경상남도 거제시",
        "employees": "약 10,000명",
        "website": "https://www.shi.samsung.co.kr",
        "linkedin_url": "https://www.linkedin.com/company/samsung-heavy-industries/",
        "job_page_url": "https://www.shi.samsung.co.kr/Kor/career/JobOpening.aspx",
    },
]


def load_companies():
    insert_companies(COMPANIES)
    print(f"[COMPANY] {len(COMPANIES)} companies loaded ({sum(1 for c in COMPANIES if '🌍' in c.get('description','') or '⭐' in c.get('description',''))} international targets)")


def crawl_linkedin_jobs() -> list:
    """LinkedIn Jobs - LNG 공정 엔지니어 글로벌 채용 (공개 데이터)"""
    items = []
    searches = [
        ("LNG+process+engineer", "worldwide"),
        ("liquefaction+engineer", "worldwide"),
        ("LNG+chemical+engineer", "Qatar"),
        ("FLNG+engineer", "worldwide"),
    ]
    # LinkedIn 공개 채용 페이지는 JS 렌더링 필요 → 큐레이션 링크 제공
    for kw, loc in searches:
        from urllib.parse import quote
        url = f"https://www.linkedin.com/jobs/search/?keywords={kw}&location={quote(loc)}"
        items.append({
            "company": "LinkedIn Jobs",
            "title": f"🌍 {kw.replace('+', ' ')} ({loc})",
            "location": loc,
            "experience": "",
            "salary": "",
            "salary_extracted": 0,
            "salary_currency": "",
            "url": url,
            "source": "LinkedIn 채용검색",
            "posted_at": datetime.now().strftime("%Y-%m-%d"),
        })
    print(f"[JOBS] LinkedIn search links: {len(items)}")
    return items


def crawl_saramin_jobs() -> list:
    """사람인 - 국내 LNG/조선 채용 (비교용)"""
    items = []
    keywords = ["LNG 공정", "조선 연구원", "선박 공정 설계", "화학공학 조선"]
    for kw in keywords:
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&searchword={kw}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "lxml")
            postings = soup.select(".item_recruit")
            for post in postings[:6]:
                title_el = post.select_one(".job_tit a")
                company_el = post.select_one(".corp_name a")
                condition_el = post.select_one(".job_condition")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                if not href.startswith("http"):
                    href = "https://www.saramin.co.kr" + href
                items.append({
                    "company": company_el.get_text(strip=True) if company_el else "미상",
                    "title": f"[국내] {title_el.get_text(strip=True)}",
                    "location": condition_el.get_text(" | ", strip=True)[:60] if condition_el else "",
                    "experience": "",
                    "salary": "",
                    "salary_extracted": 0,
                    "salary_currency": "KRW",
                    "url": href,
                    "source": "사람인 (국내비교)",
                    "posted_at": datetime.now().strftime("%Y-%m-%d"),
                })
        except Exception as e:
            print(f"[JOBS] Saramin error for '{kw}': {e}")
    print(f"[JOBS] 사람인 국내 LNG: {len(items)} postings")
    return items


def run_all():
    load_companies()
    jobs = []
    jobs += crawl_linkedin_jobs()
    jobs += crawl_saramin_jobs()
    from db.database import upsert_jobs
    saved = upsert_jobs(jobs)
    print(f"[JOBS] Total new jobs saved: {saved}/{len(jobs)}")


if __name__ == "__main__":
    from db.database import init_db
    init_db()
    run_all()
