"""
salary_crawler.py - 조선/LNG 연봉 정보 (v2 - 해외 취업 특화)
사용자 프로필: HD한국조선해양 LNG 액화설비 공정 설계 연구원 (화학공학 석사)
국내외 연봉 비교 + 국가별 생활비 보정 포함
"""
import sys, os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import upsert_salaries

# ──────────────────────────────────────────────
# 연봉 벤치마크 데이터
# 출처: LinkedIn Salary, Glassdoor, PayScale, Levels.fyi, 업계 공개자료 (2024~2025)
# ──────────────────────────────────────────────

SALARY_DATA = [

    # ══════════════════════════════════════
    # 📍 현 직장 기준 (국내 비교 기준선)
    # ══════════════════════════════════════
    {"job_title": "LNG 액화설비 공정 연구원 (석사 2~3년차)", "company": "HD한국조선해양 (현 직장 기준)", "avg_salary": "약 5,800만원", "min_salary": "5,200만원", "max_salary": "6,500만원", "experience_level": "석사 초기 경력", "source": "잡플래닛/크레딧잡 2024"},
    {"job_title": "LNG 공정 연구원 (석사 5~8년차)", "company": "국내 조선사 평균", "avg_salary": "약 7,500만원", "min_salary": "6,500만원", "max_salary": "8,500만원", "experience_level": "5~8년 경력", "source": "업계 평균 2024"},
    {"job_title": "수석 연구원 (선임급)", "company": "국내 조선사 평균", "avg_salary": "약 1.0억원", "min_salary": "8,500만원", "max_salary": "1.2억원", "experience_level": "10년+ 경력", "source": "업계 평균 2024"},

    # ══════════════════════════════════════
    # 🇫🇷 프랑스 (GTT, TotalEnergies, TechnipFMC)
    # ══════════════════════════════════════
    {"job_title": "LNG Process Engineer (Junior)", "company": "GTT (프랑스)", "avg_salary": "€45,000~55,000/년 (약 6,500~8,000만원)", "min_salary": "€45,000", "max_salary": "€55,000", "experience_level": "1~3년", "source": "LinkedIn Salary / Glassdoor FR 2024"},
    {"job_title": "LNG Process Engineer (Senior)", "company": "GTT (프랑스)", "avg_salary": "€65,000~85,000/년 (약 9,500~1.25억원)", "min_salary": "€65,000", "max_salary": "€85,000", "experience_level": "5~10년", "source": "LinkedIn Salary / Glassdoor FR 2024"},
    {"job_title": "Process Engineer - LNG", "company": "TotalEnergies (프랑스)", "avg_salary": "€55,000~75,000/년 (약 8,000~1.1억원)", "min_salary": "€55,000", "max_salary": "€75,000", "experience_level": "3~7년", "source": "LinkedIn Salary 2024"},
    {"job_title": "Process/Chemical Engineer", "company": "TechnipFMC (프랑스/영국/미국)", "avg_salary": "€60,000~90,000/년 (약 8,800~1.3억원)", "min_salary": "€60,000", "max_salary": "€90,000", "experience_level": "3~8년", "source": "Glassdoor 2024"},

    # ══════════════════════════════════════
    # 🇶🇦 카타르 (QatarEnergy) - 면세 + 생활지원
    # ══════════════════════════════════════
    {"job_title": "Process Engineer - LNG (Junior)", "company": "QatarEnergy (카타르, 면세)", "avg_salary": "USD $60,000~90,000/년 (실수령 기준)", "min_salary": "$60,000", "max_salary": "$90,000", "experience_level": "2~5년", "source": "Glassdoor QA 2024"},
    {"job_title": "Senior Process Engineer - LNG", "company": "QatarEnergy (카타르, 면세)", "avg_salary": "USD $100,000~160,000/년 + 주거/차량 제공", "min_salary": "$100,000", "max_salary": "$160,000", "experience_level": "5~12년", "source": "LinkedIn / 업계 네트워크 2024"},
    {"job_title": "Principal Engineer - Liquefaction", "company": "QatarEnergy (카타르, 면세)", "avg_salary": "USD $160,000~220,000/년 + 패키지", "min_salary": "$160,000", "max_salary": "$220,000", "experience_level": "10년+ / 박사 선호", "source": "업계 네트워크 2024"},

    # ══════════════════════════════════════
    # 🇳🇱🇬🇧 네덜란드/영국 (Shell, Wood Group, LR)
    # ══════════════════════════════════════
    {"job_title": "Integrated Gas Process Engineer", "company": "Shell (네덜란드/싱가포르)", "avg_salary": "€65,000~95,000/년 + 보너스 (약 9,500만~1.4억)", "min_salary": "€65,000", "max_salary": "€95,000", "experience_level": "3~8년", "source": "Glassdoor NL 2024"},
    {"job_title": "Chemical/Process Engineer - LNG", "company": "Wood Group (영국/싱가포르/UAE)", "avg_salary": "£55,000~80,000/년 (약 9,000만~1.3억)", "min_salary": "£55,000", "max_salary": "£80,000", "experience_level": "3~8년", "source": "Glassdoor UK 2024"},
    {"job_title": "Gas Technology Engineer", "company": "Lloyd's Register (영국)", "avg_salary": "£50,000~70,000/년 (약 8,000만~1.13억)", "min_salary": "£50,000", "max_salary": "£70,000", "experience_level": "3~7년", "source": "Glassdoor UK 2024"},

    # ══════════════════════════════════════
    # 🇳🇴 노르웨이 (Golar LNG, Höegh LNG) - 세계 최고 복지
    # ══════════════════════════════════════
    {"job_title": "FLNG Process Engineer", "company": "Golar LNG (노르웨이)", "avg_salary": "NOK 850,000~1,200,000/년 (약 1.1억~1.5억)", "min_salary": "NOK 850,000", "max_salary": "NOK 1,200,000", "experience_level": "3~8년", "source": "Glassdoor NO 2024"},
    {"job_title": "FSRU Process Engineer", "company": "Höegh LNG (노르웨이)", "avg_salary": "NOK 800,000~1,100,000/년 (약 1.03억~1.42억)", "min_salary": "NOK 800,000", "max_salary": "NOK 1,100,000", "experience_level": "3~8년", "source": "Glassdoor NO 2024"},

    # ══════════════════════════════════════
    # 🇸🇬 싱가포르 (글로벌 허브, 낮은 세율)
    # ══════════════════════════════════════
    {"job_title": "LNG Process Engineer", "company": "글로벌 오일메이저 싱가포르 허브", "avg_salary": "SGD $90,000~140,000/년 (약 9,000만~1.4억, 세율 낮음)", "min_salary": "SGD $90,000", "max_salary": "SGD $140,000", "experience_level": "3~7년 (영어 필수)", "source": "MyCareersFuture SG 2024"},

    # ══════════════════════════════════════
    # 🇩🇪🇫🇮 독일/핀란드 (MAN ES, Wärtsilä)
    # ══════════════════════════════════════
    {"job_title": "Gas/LNG Application Engineer", "company": "MAN Energy Solutions (독일)", "avg_salary": "€55,000~75,000/년 (약 8,000만~1.1억)", "min_salary": "€55,000", "max_salary": "€75,000", "experience_level": "2~6년", "source": "Glassdoor DE 2024"},
    {"job_title": "LNG Solutions Engineer", "company": "Wärtsilä (핀란드)", "avg_salary": "€52,000~72,000/년 (약 7,500만~1.05억)", "min_salary": "€52,000", "max_salary": "€72,000", "experience_level": "2~6년 + 우수한 워라밸", "source": "Glassdoor FI 2024"},

    # ══════════════════════════════════════
    # 🌍 국가별 생활비 보정 지수 (참고)
    # ══════════════════════════════════════
    {"job_title": "[참고] 구매력 기준 환산 지수", "company": "카타르 (면세+지원)", "avg_salary": "실수령 한국 대비 2.5~3.5배", "min_salary": "2.5x", "max_salary": "3.5x", "experience_level": "패키지 포함 기준", "source": "Numbeo COL Index 2024"},
    {"job_title": "[참고] 구매력 기준 환산 지수", "company": "노르웨이 (세금 400만원+)", "avg_salary": "실수령 한국 대비 1.5~2.0배", "min_salary": "1.5x", "max_salary": "2.0x", "experience_level": "높은 세금 감안", "source": "Numbeo COL Index 2024"},
    {"job_title": "[참고] 구매력 기준 환산 지수", "company": "싱가포르 (낮은 세율)", "avg_salary": "실수령 한국 대비 1.8~2.5배", "min_salary": "1.8x", "max_salary": "2.5x", "experience_level": "세율 15~20% 낮음", "source": "Numbeo COL Index 2024"},
    {"job_title": "[참고] 구매력 기준 환산 지수", "company": "프랑스/독일 (복지 우수)", "avg_salary": "실수령 한국 대비 1.2~1.7배", "min_salary": "1.2x", "max_salary": "1.7x", "experience_level": "높은 세금, 복지로 보완", "source": "Numbeo COL Index 2024"},
]


def run_all():
    upsert_salaries(SALARY_DATA)
    print(f"[SALARY] {len(SALARY_DATA)} international salary benchmarks saved")


if __name__ == "__main__":
    from db.database import init_db
    init_db()
    run_all()
