import json
import os
from urllib.parse import parse_qs, quote_plus, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from news_sources import NewsSource


class ScrapeError(Exception):
    pass


def _allowed(url: str, source: NewsSource) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme in ("http", "https") and any(
        host == domain or host.endswith("." + domain) for domain in source.domains
    )


def _unwrap(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname and parsed.hostname.endswith("google.com") and parsed.path == "/url":
        return parse_qs(parsed.query).get("q", [url])[0]
    return url


def _driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36")
    options.binary_location = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
    driver = webdriver.Chrome(service=Service(os.getenv("CHROMEDRIVER", "/usr/local/bin/chromedriver")), options=options)
    driver.set_page_load_timeout(25)
    return driver


def _first_result(driver, source: NewsSource, keyword: str) -> str:
    if source.name == "ProPakistani":
        try:
            driver.get(f"https://propakistani.pk/wp-json/wp/v2/search?search={quote_plus(keyword)}&per_page=1")
            results = json.loads(driver.find_element(By.TAG_NAME, "body").text)
            if results and _allowed(results[0]["url"], source):
                return results[0]["url"]
        except (WebDriverException, ValueError, KeyError, TypeError):
            pass
    query = quote_plus(f"site:{source.domains[0]} {keyword}")
    engines = (
        (f"https://www.google.com/search?q={query}&num=10", "a:has(h3)"),
        (f"https://www.bing.com/search?q={query}", "li.b_algo h2 a"),
    )
    for search_url, selector in engines:
        try:
            driver.get(search_url)
            WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CSS_SELECTOR, selector))
            for anchor in driver.find_elements(By.CSS_SELECTOR, selector):
                url = _unwrap(anchor.get_attribute("href") or "")
                if _allowed(url, source):
                    return url
        except WebDriverException:
            continue
    raise ScrapeError("No accessible search result found for this keyword and news source")


def _article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("script, style, nav, footer, header, aside, form, figure"):
        tag.decompose()
    article = soup.select_one("article") or soup.select_one("main") or soup.body
    if article is None:
        raise ScrapeError("Article page has no readable content")
    paragraphs = [p.get_text(" ", strip=True) for p in article.select("p")]
    text = " ".join(p for p in paragraphs if len(p) >= 35)
    if len(text) < 120:
        raise ScrapeError("Article text could not be extracted")
    return text


def fetch_first_article(source: NewsSource, keyword: str) -> tuple[str, str]:
    driver = None
    try:
        driver = _driver()
        url = _first_result(driver, source, keyword)
        driver.get(url)
        if not _allowed(driver.current_url, source):
            raise ScrapeError("Article redirected outside the assigned news source")
        WebDriverWait(driver, 12).until(lambda d: len(d.find_elements(By.TAG_NAME, "p")) >= 2)
        return driver.current_url, _article_text(driver.page_source)
    except WebDriverException as exc:
        raise ScrapeError("Browser could not load the search result or article") from exc
    finally:
        if driver is not None:
            driver.quit()
