# 대시보드 v2 - LinkedIn 연동 & 뉴스/연봉 구조 개편

## User Review Required

> [!IMPORTANT]
> **LinkedIn 연동 방식**: LinkedIn 공식 API는 개인 인증 없이는 데이터 접근이 매우 제한됩니다.
> 아래 두 가지 방식 중 선택이 필요합니다:
>
> **A. 수동 입력 방식 (추천)**: 대시보드에 "내 프로필" 설정 패널을 추가하여 직접 커리어 정보를 입력. 입력된 정보를 기반으로 모든 추천이 개인화됨. 빠르고 안정적.
>
> **B. LinkedIn URL 크롤링**: LinkedIn 공개 프로필 URL을 입력하면 Playwright로 공개 정보(헤드라인, 경력, 스킬)를 자동 수집. **단, LinkedIn 이용약관상 자동화는 금지이므로 수집 실패 가능성 있음.**
>
> → **이 계획은 A + B 병행 방식을 채택합니다** (수동 입력이 기본, LinkedIn URL로 자동보완)

> [!WARNING]
> **MASGA**: "Make American Shipbuilding Great Again" (2025년 트럼프 행정부 LNG 수출선 美 건조 의무화 행정명령)으로 해석하였습니다. 맞는지 확인해주세요.

---

## Proposed Changes

### My Profile System

#### [NEW] `db/database.py` → `my_profile` 테이블 추가
- 경력, 스킬, 교육, 타겟 국가/역할, LinkedIn URL 저장

#### [NEW] `crawlers/linkedin_profile.py`
Playwright로 사용자의 LinkedIn 공개 프로필을 가져옴:
- 경력 (experience): 직함, 회사, 기간
- 스킬 (skills): 기술 키워드 추출
- 교육 (education): 학위, 전공
- 헤드라인

---

### 뉴스 크롤러 개편

기존: 다양한 국제 미디어  
변경: **헤드라인 중심**, 3개 카테고리로 구조화

| 카테고리 | 대상 |
|---|---|
| 🇰🇷 국내 조선 3사 | 한화오션·삼성중공업·HD현대중공업 그룹 공식 뉴스룸 보도자료 |
| 📋 조선 정책 | 한국 해양수산부, 산업통상자원부, IMO 정책 관련 |
| 🌍 국제 (MASGA 포함) | gCaptain, Marine Log, Lloyd's List Free, gcaptain MASGA 정책 뉴스 |

#### [MODIFY] `crawlers/news_crawler.py`
- 헤드라인 + 출처 + 날짜만 수집 (요약 생략, 속도↑)
- 카테고리 필드 추가 (`category`: ko_company / ko_policy / international)

#### [MODIFY] `db/database.py`
- `news` 테이블에 `category` 컬럼 추가

---

### 채용 & 연봉 패널 통합 개편

**기존**: 기업 정보 + 채용 공고 (분리)  
**변경**: **"Job Salary Intelligence"** - 실제 채용공고에서 제시된 연봉이 핵심

#### [MODIFY] `crawlers/company_crawler.py`
- 실제 채용사이트에서 공고별 연봉 정보 추출
- 대상: LinkedIn Jobs, Indeed (직접 연봉 명시 포고 필터), GTT Careers, QatarEnergy Careers

#### [MODIFY] `db/database.py`
- `jobs` 테이블에 `salary_extracted` 컬럼 추가 (공고 내 연봉 명시 여부)

---

### 대시보드 UI 개편

#### [MODIFY] `static/dashboard.html`
4개 패널 → **5개 패널** 구조:

```
┌──────────────────────────────────────────────┐
│ 🚢 조선업 커리어 인텔리전스               [⚙️ 내 프로필]  │
├──────┬──────┬──────────────────────────┬─────┤
│ 📰   │ 📰   │ 📰 뉴스 (3탭)            │     │
│      │ 국내 │ 국내조선3사|정책|MASGA    │     │
├──────┴──────┴──────────────────────────┤     │
│ 💼 Job Salary Intel    │ 💰 연봉 비교   │ 🔗  │
│ (실제 공고 연봉 표시)   │ (국가별 차트) │     │
└─────────────────────────────────────────────┘
```

- **⚙️ 내 프로필** 슬라이드인 패널 추가
  - LinkedIn URL 입력 → 자동 프로필 수집
  - 수동 입력: 스킬, 경력, 타겟 국가
  - 프로필 기반으로 뉴스 키워드 하이라이트, 연봉 구간 표시

---

## Verification Plan

### Automated Tests
```bash
# 개별 크롤러 테스트
python crawlers/news_crawler.py    # 3 카테고리 뉴스 확인
python crawlers/linkedin_profile.py  # 공개 프로필 수집 테스트

# 서버 재시작
uvicorn app:app --reload --port 8000
```

### Manual Verification
1. `⚙️ 내 프로필` 버튼 → 패널 열림 확인
2. LinkedIn URL 입력 → 경력/스킬 자동 수집 확인 (또는 실패 시 수동 입력 안내)
3. 뉴스 탭 3개 (국내조선3사 / 정책 / MASGA국제) 각각 확인
4. Job Salary Intel 패널에서 연봉 명시 공고 확인
