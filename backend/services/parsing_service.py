from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
    options.page_load_strategy = "eager"
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def parse_url(url: str, timeout: int = 40) -> dict:
    """Открывает страницу конкурента через Selenium и извлекает title, h1, первый абзац."""
    driver = _build_driver()
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    # Cookie/consent-баннеры (OneTrust, Cookiebot, Quantcast и т.п.) часто содержат
    # длинный текст-абзац, который иначе побеждает как "первый абзац" вместо контента страницы.
    # Помечаем такие узлы, но НЕ вырезаем из дерева (чтобы случайно не задеть обёртку реального контента) —
    # просто пропускаем кандидатов, чьи предки попадают под эти маркеры.
    consent_markers = ("cookie", "onetrust", "cookiebot", "qc-cmp", "gdpr-banner")

    def in_consent_banner(tag) -> bool:
        for ancestor in [tag] + list(tag.parents):
            if not getattr(ancestor, "get", None):
                continue
            el_id = (ancestor.get("id") or "").lower()
            el_class = " ".join(ancestor.get("class") or []).lower()
            if any(marker in el_id or marker in el_class for marker in consent_markers):
                return True
        return False

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    h1 = None
    for h1_tag in soup.find_all("h1"):
        if not in_consent_banner(h1_tag):
            text = h1_tag.get_text(strip=True)
            if text:
                h1 = text
                break

    first_paragraph = None
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 40 and "cookie" not in text.lower() and not in_consent_banner(p):
            first_paragraph = text
            break

    return {
        "url": url,
        "title": title,
        "h1": h1,
        "first_paragraph": first_paragraph,
    }
