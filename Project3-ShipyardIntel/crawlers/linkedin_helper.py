"""
linkedin_helper.py - LinkedIn 계정 추천 및 LNG/해양 글로벌 네트워크 가이드 (v2)
사용자 프로필: LNG 액화설비 공정 설계 연구원 (화학공학 석사) - 해외 취업 목표
"""

# ── 팔로우 추천: LNG/해양 국제 기업 페이지 ──
COMPANY_PAGES = [
    # 최우선 타겟
    {
        "name": "GTT (Gaztransport & Technigaz) ⭐",
        "url": "https://www.linkedin.com/company/gtt-gaztransport-technigaz/",
        "type": "company",
        "description": "LNG 격납시스템 세계 1위. 귀하의 LNG 공정 배경과 가장 직결되는 회사. 프랑스 파리 근교.",
    },
    {
        "name": "QatarEnergy ⭐",
        "url": "https://www.linkedin.com/company/qatarenergy/",
        "type": "company",
        "description": "최고 연봉 타겟. 면세+주거+차량 지원. 2030 LNG 증산으로 대규모 채용 중.",
    },
    {
        "name": "Shell ⭐",
        "url": "https://www.linkedin.com/company/shell/",
        "type": "company",
        "description": "LNG 글로벌 최대 트레이더. Integrated Gas 부문 Process Engineer 채용 활발.",
    },
    {
        "name": "TotalEnergies",
        "url": "https://www.linkedin.com/company/totalenergies/",
        "type": "company",
        "description": "프랑스 LNG 메이저. 화학공학 석사 Process Engineer 수시 채용.",
    },
    {
        "name": "TechnipFMC",
        "url": "https://www.linkedin.com/company/technipfmc/",
        "type": "company",
        "description": "LNG 플랜트 EPC 선두. 액화 공정 설계 엔지니어 핵심 채용처.",
    },
    {
        "name": "Wärtsilä",
        "url": "https://www.linkedin.com/company/wartsila/",
        "type": "company",
        "description": "LNG 가스핸들링·재기화 솔루션. 핀란드 본사, 워라밸 우수.",
    },
    {
        "name": "Golar LNG",
        "url": "https://www.linkedin.com/company/golar-lng/",
        "type": "company",
        "description": "FLNG 개척자. 노르웨이 오슬로. Liquefaction Engineer 핵심 채용처.",
    },
    {
        "name": "Höegh LNG",
        "url": "https://www.linkedin.com/company/hoegh-lng/",
        "type": "company",
        "description": "FSRU 세계 선두. 재기화 공정 엔지니어 채용. 노르웨이 워라밸.",
    },
    {
        "name": "Saipem",
        "url": "https://www.linkedin.com/company/saipem/",
        "type": "company",
        "description": "FLNG·해양플랜트 건설 EPC. Process Engineer 글로벌 채용.",
    },
    {
        "name": "Wood Group (John Wood Group)",
        "url": "https://www.linkedin.com/company/john-wood-group/",
        "type": "company",
        "description": "LNG 플랜트 FEED·기본설계 컨설팅. 싱가포르/중동 허브에서 채용.",
    },
    {
        "name": "MAN Energy Solutions",
        "url": "https://www.linkedin.com/company/man-energy-solutions/",
        "type": "company",
        "description": "LNG/암모니아 엔진 R&D. 독일 기반. 친환경 추진 미래 성장성 높음.",
    },
    {
        "name": "Lloyd's Register",
        "url": "https://www.linkedin.com/company/lloyds-register/",
        "type": "company",
        "description": "세계 선급. LNG 선박 인증/컨설팅. 규정·안전 분야 커리어 옵션.",
    },
    # 국내 비교용
    {
        "name": "HD Hyundai Heavy Industries (비교용)",
        "url": "https://www.linkedin.com/company/hd-hyundai-heavy-industries/",
        "type": "company",
        "description": "[국내 비교] 현재 재직 그룹사. 글로벌 활동 및 해외 네트워크 확장 시 활용.",
    },
]

# ── 팔로우 추천: LNG/해양 분야 전문 인플루언서 검색 ──
INFLUENCERS = [
    {
        "name": "LNG Process Engineers (글로벌)",
        "url": "https://www.linkedin.com/search/results/people/?keywords=LNG+process+engineer&network=%5B%22F%22%5D",
        "description": "LNG 공정 엔지니어 글로벌 네트워크 탐색 (1촌 연결 기준)",
        "specialty": "LNG Process Engineering",
    },
    {
        "name": "GTT Engineers (현직자 탐색)",
        "url": "https://www.linkedin.com/search/results/people/?keywords=GTT+Gaztransport+engineer",
        "description": "GTT 현직 엔지니어 탐색 → 내부 채용 문화/연봉 정보 네트워킹",
        "specialty": "LNG Containment / GTT",
    },
    {
        "name": "QatarEnergy Engineers (현직자 탐색)",
        "url": "https://www.linkedin.com/search/results/people/?keywords=QatarEnergy+process+engineer",
        "description": "QatarEnergy 현직 엔지니어 탐색 → 카타르 생활/연봉 실정 파악",
        "specialty": "QatarEnergy / LNG 카타르",
    },
    {
        "name": "Korean LNG Engineers Abroad (해외 취업 한국인)",
        "url": "https://www.linkedin.com/search/results/people/?keywords=Korean+LNG+engineer+abroad",
        "description": "해외 취업 한국인 LNG 엔지니어 → 실질적인 해외 취업 조언 가능",
        "specialty": "해외취업 한국인 네트워크",
    },
]

# ── 가입 추천: LinkedIn 그룹 ──
GROUPS = [
    {
        "name": "LNG Industry Professionals",
        "url": "https://www.linkedin.com/groups/4320826/",
        "description": "LNG 업계 글로벌 전문가 그룹. 채용 정보·기술 트렌드 공유",
    },
    {
        "name": "Shipbuilding & Marine Engineering Professionals",
        "url": "https://www.linkedin.com/groups/1773/",
        "description": "4만+ 글로벌 조선 전문가 그룹. 조선·LNG선 기술 논의",
    },
    {
        "name": "Offshore & LNG Process Engineering",
        "url": "https://www.linkedin.com/groups/136097/",
        "description": "해양·LNG 공정 엔지니어링 전문 그룹",
    },
    {
        "name": "Chemical Engineers Network",
        "url": "https://www.linkedin.com/groups/58957/",
        "description": "화학공학 글로벌 네트워크. 해외 취업 정보·커리어 전환 논의",
    },
    {
        "name": "Korea Engineering Professionals Abroad",
        "url": "https://www.linkedin.com/search/results/groups/?keywords=korean+engineers+abroad",
        "description": "해외 취업 한국인 엔지니어 커뮤니티. 실질 정보 교류",
    },
]

# ── LNG/해외 특화 채용 검색 URL ──
def get_linkedin_job_search_url(keyword: str, location: str = "") -> str:
    from urllib.parse import quote
    base = f"https://www.linkedin.com/jobs/search/?keywords={quote(keyword)}"
    if location:
        base += f"&location={quote(location)}"
    return base

QUICK_SEARCHES = [
    {"label": "LNG Process Engineer (글로벌)", "url": get_linkedin_job_search_url("LNG process engineer")},
    {"label": "Liquefaction Engineer (카타르)", "url": get_linkedin_job_search_url("liquefaction engineer", "Qatar")},
    {"label": "LNG Engineer (노르웨이)", "url": get_linkedin_job_search_url("LNG engineer", "Norway")},
    {"label": "LNG Process Engineer (싱가포르)", "url": get_linkedin_job_search_url("LNG process engineer", "Singapore")},
    {"label": "FLNG / FSRU Engineer (글로벌)", "url": get_linkedin_job_search_url("FLNG FSRU process engineer")},
    {"label": "Chemical Engineer - LNG (프랑스)", "url": get_linkedin_job_search_url("chemical engineer LNG", "France")},
    {"label": "GTT 채용 직접 검색", "url": get_linkedin_job_search_url("GTT Gaztransport engineer")},
    {"label": "Cryogenic / LNG Equipment Engineer", "url": get_linkedin_job_search_url("cryogenic LNG engineer")},
]


def get_all_data() -> dict:
    return {
        "company_pages": COMPANY_PAGES,
        "influencers": INFLUENCERS,
        "groups": GROUPS,
        "quick_searches": QUICK_SEARCHES,
    }


if __name__ == "__main__":
    import json
    data = get_all_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
