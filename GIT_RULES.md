# AG-PROJECTS-mac- Git & GitHub 운영 규칙

이 문서는 `AG-PROJECTS-mac-` 레포지토리를 여러 컴퓨터에서 일관성 있게 사용하기 위한 규칙과 설정을 정리한 가이드입니다.

---

## 1. 레포지토리 구조 (Directory Structure)

모든 작업은 **대주제(Project) 폴더** 단위로 묶어 관리합니다.

```
AG-PROJECTS-mac-/
├── GIT_RULES.md              ← 이 문서
├── .gitignore                ← 무시 규칙 (아래 참조)
│
├── Project1-AutoPlotDigitizer/  ← 프로젝트 번호 + 이름
│   ├── AutoPlotDigitizerWeb/    ← 실제 소스코드
│   ├── debugging-detection-logic/   ← AI 작업 세션 문서
│   └── ...
│
├── Project2-FitnessApp/
│   └── native-app-packaging/
│
└── Project3-[새프로젝트명]/   ← 새 프로젝트 추가 시
```

### 폴더 명명 규칙
- **프로젝트 폴더**: `ProjectN-[대주제명]` (예: `Project3-Crawler`)
- **세션 작업 폴더**: AI와의 대화에서 만들어진 마크다운 문서 묶음. 소문자 + 하이픈 (예: `debugging-detection-logic`)
- **소스코드 폴더**: 원래 프로젝트 이름 유지 (예: `AutoPlotDigitizerWeb`)

---

## 2. .gitignore 규칙

레포지토리 최상단에 `.gitignore`가 있으며, 아래 항목들은 Git에서 추적하지 않습니다.

```gitignore
# OS 시스템 파일
.DS_Store

# AI 내부 상태/임시 파일 (매우 빈번하게 변경됨)
*.resolved
*.resolved.*
*.metadata.json

# 임시 미디어 저장소
tempmediaStorage/

# AI 생성 미디어 이미지
media__*.png
media__*.jpg

# Python 가상환경 및 캐시 (절대 커밋 금지 - 용량 수백MB)
venv/
.venv/
env/
__pycache__/
*.pyc

# 로그 파일 (선택적)
*.log
```

> **⚠️ 중요**: `venv/` 폴더는 GitHub의 100MB 파일 크기 제한으로 업로드가 불가합니다. 절대 커밋하지 마세요.

---

## 3. 커밋 메시지 규칙

[Conventional Commits](https://www.conventionalcommits.org/) 스타일을 따릅니다.

| 접두사 | 용도 |
|--------|------|
| `feat:` | 새로운 기능 추가 |
| `fix:` | 버그 수정 |
| `chore:` | 구조 변경, 폴더 정리, 설정 변경 등 |
| `docs:` | 문서 수정 |
| `refactor:` | 코드 리팩토링 |

**예시:**
```bash
git commit -m "feat: Add news crawler for shipyard intel project"
git commit -m "chore: Rename UUID session folders to descriptive names"
git commit -m "fix: Remove venv from tracking to resolve GitHub size limit"
```

---

## 4. 정기적인 정리 작업 (AI에게 요청)

AI(Antigravity)와 작업을 마친 후, **AI가 자동 생성한 UUID 폴더명**이 남아있을 수 있습니다. 필요할 때 AI에게 아래와 같이 요청하면 됩니다:

> **"이번 작업 폴더를 '[주제명]'으로 이름 바꾸고 커밋해줘."**

AI가 `git mv`를 통해 자동으로 이름을 변경하고 GitHub에 반영합니다.

---

## 5. 새 컴퓨터에 환경 설정하는 법

```bash
# 1. 레포지토리 클론
git clone https://github.com/teddingted/AG-PROJECTS-mac-.git
cd AG-PROJECTS-mac-

# 2. AI brain 디렉토리 심볼릭 링크 생성 (AI 시스템 경로 호환)
mkdir -p ~/.gemini/antigravity
ln -s "$(pwd)" ~/.gemini/antigravity/brain

# 3. Python 프로젝트 의존성 설치 (venv는 로컬에서 직접 생성)
cd Project1-AutoPlotDigitizer/AutoPlotDigitizerWeb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 6. 자주 쓰는 Git 명령어

```bash
# 현재 상태 확인
git status

# 모든 변경사항 스테이징 및 커밋
git add .
git commit -m "chore: [변경 내용 설명]"

# GitHub에 업로드
git push origin main

# GitHub에서 최신 내용 가져오기
git pull origin main

# 폴더명 변경 (Git 추적 유지)
git mv [기존이름] [새이름]
```

---

*마지막 업데이트: 2026-02-20*
