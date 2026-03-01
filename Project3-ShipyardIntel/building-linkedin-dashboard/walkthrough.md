# 🚢 조선업 커리어 인텔리전스 대시보드 v2

## 새로 추가된 기능

### 1. ⚙️ 내 프로필 연동
- 헤더 우상단 프로필 배지 클릭 → 슬라이드 패널 오픈
- **LinkedIn URL** 입력 후 "자동 수집" → Playwright로 공개 프로필 자동 파싱
- 수동 입력: 현재 회사, 직함, 경력 년수, 스킬, 타겟 국가/직무
- 저장 후 **대시보드 즉시 개인화**:
  - 헤더에 내 역할/회사 표시
  - 내 스킬과 일치하는 뉴스 헤드라인 **골드 색상 하이라이트**
  - "추천 필터" 바에 타겟 국가/스킬 칩 표시

### 2. 📰 뉴스 3탭 구조 개편
| 탭 | 소스 | 특징 |
|---|---|---|
| 🇰🇷 조선 3사 | Google News RSS (한화오션/삼성중공업/HD현대) | 30건/회 |
| 📋 정책 | 해양수산부 + Google News 폴백 | IMO, 조선 정책 |
| 🌍 MASGA·국제 | gCaptain, Marine Log, Maritime Executive | MASGA 자동 태그 |

### 3. 💼 Job Salary Intel 패널 (신규)
- **"연봉 명시 공고"** 탭: `salary_extracted=1` 공고 우선 표시
- 연봉 정보를 **보라색 배지**로 강조
- 기업 정보 탭: 15개 국제 LNG 타겟 기업 카드

---

## 검증 결과

**서버 크롤링:**
- ✅ 뉴스: **74건** 저장 (조선3사 30 + 정책 18 + Marine Log 14 + Maritime Executive 20)
- ✅ 기업: **15개사** (국제 12 + 국내 비교 3)
- ✅ 채용: **28건** (**이전 오류 수정** - salary_extracted 필드 누락 버그 해결)
- ✅ 연봉: **22건** (국제 벤치마크)

**브라우저 검증:**

![v2 뉴스 3탭 구조](/Users/dm_chamber/.gemini/antigravity/brain/69778c82-f009-4c36-85ef-2fb6f7f8ae78/v2_news_tabs.png)
*뉴스 패널 - 🇰🇷 조선 3사 탭 활성화*

![v2 My Profile 패널](/Users/dm_chamber/.gemini/antigravity/brain/69778c82-f009-4c36-85ef-2fb6f7f8ae78/v2_profile_panel_open.png)
*내 프로필 슬라이드 패널 - LinkedIn URL, 커리어 정보, 타겟 국가 입력*

![v2 대시보드 전체 녹화](/Users/dm_chamber/.gemini/antigravity/brain/69778c82-f009-4c36-85ef-2fb6f7f8ae78/dashboard_v2_verification_1771594097411.webp)
*v2 전체 검증 녹화*

---

## 실행

```bash
cd AG-PROJECTS-mac-/Project3-ShipyardIntel
bash run.sh   # → http://localhost:8000
```

> **프로필 설정 방법**: 우상단 👤 배지 클릭 → 현재 커리어 입력 → 💾 저장
