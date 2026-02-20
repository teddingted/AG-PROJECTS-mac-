"""
linkedin_profile.py - LinkedIn 공개 프로필 크롤러 (v2)
Playwright로 공개 프로필에서 experience/skills/headline 추출
로그인 불필요 - 공개 데이터만 접근
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import get_profile, save_profile

def fetch_linkedin_public_profile(linkedin_url: str) -> dict:
    """
    LinkedIn 공개 프로필 URL에서 헤드라인, 경력, 스킬 수집
    실패 시 빈 dict 반환 (수동 입력으로 대체)
    """
    result = {
        "linkedin_headline": "",
        "linkedin_experience": "",
        "linkedin_skills": "",
    }
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            )
            page = ctx.new_page()
            page.goto(linkedin_url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # 헤드라인 추출
            headline_el = page.query_selector(".text-heading-xlarge, .top-card-layout__headline, h2.top-card__subline-item")
            if headline_el:
                result["linkedin_headline"] = headline_el.inner_text().strip()

            # 경력 추출
            exp_items = page.query_selector_all(".experience-item, .pv-entity__summary-info, section.experience li")
            exp_texts = []
            for el in exp_items[:5]:
                txt = el.inner_text().strip().replace("\n", " | ")
                if txt:
                    exp_texts.append(txt)
            result["linkedin_experience"] = "\n".join(exp_texts)

            # 스킬 추출
            skill_els = page.query_selector_all(".skill-categories-section li, .pv-skill-category-entity__name, .pvs-list__item--line-separated span[aria-hidden='true']")
            skills = [s.inner_text().strip() for s in skill_els[:20] if s.inner_text().strip()]
            result["linkedin_skills"] = ", ".join(skills)

            browser.close()
            print(f"[LINKEDIN] Profile fetched: headline='{result['linkedin_headline']}', skills={len(skills)}")
    except ImportError:
        print("[LINKEDIN] Playwright not installed. Run: playwright install chromium")
    except Exception as e:
        print(f"[LINKEDIN] Profile fetch failed (may need login): {e}")

    return result


def update_profile_from_linkedin(linkedin_url: str) -> dict:
    """기존 프로필을 유지하고 LinkedIn 데이터만 병합"""
    current = get_profile()
    linkedin_data = fetch_linkedin_public_profile(linkedin_url)
    current.update({k: v for k, v in linkedin_data.items() if v})
    current["linkedin_url"] = linkedin_url
    # id, updated_at 제거
    current.pop("id", None)
    current.pop("updated_at", None)
    # 필수 필드 기본값
    for f in ["current_company","current_title","experience_years","education","skills","target_countries","target_roles","linkedin_headline","linkedin_experience","linkedin_skills"]:
        current.setdefault(f, "" if f != "experience_years" else 0)
    save_profile(current)
    return current


if __name__ == "__main__":
    url = input("LinkedIn 공개 프로필 URL 입력: ").strip()
    result = fetch_linkedin_public_profile(url)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
