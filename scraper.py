import json
import os
import re
import urllib.request
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
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(service=Service(os.getenv("CHROMEDRIVER", "/usr/local/bin/chromedriver")), options=options)
    driver.set_page_load_timeout(25)
    return driver


def _wp_search(keyword: str, source: NewsSource) -> tuple[str, int]:
    search_url = f"https://propakistani.pk/wp-json/wp/v2/search?search={quote_plus(keyword)}&per_page=1"
    request = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        results = json.load(response)
    if not results or not _allowed(results[0].get("url", ""), source):
        raise ScrapeError("No ProPakistani search result found")
    return results[0]["url"], results[0]["id"]


def _wp_article(post_id: int) -> str:
    request = urllib.request.Request(
        f"https://propakistani.pk/wp-json/wp/v2/posts/{post_id}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        post = json.load(response)
    return _article_text(f"<article>{post['content']['rendered']}</article>")


def _reader_content(url: str) -> str:
    # Reader service can access an article when the news site blocks cloud IP ranges.
    proxy_url = "https://r.jina.ai/" + url.replace("&", "%26")
    request = urllib.request.Request(proxy_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=35) as response:
        text = response.read().decode("utf-8", "replace")
    if "Markdown Content:\n" not in text:
        raise ScrapeError("Reader service returned no article content")
    return text.split("Markdown Content:\n", 1)[1].strip()


def _reader_search(keyword: str, source: NewsSource) -> str:
    url = f"https://propakistani.pk/wp-json/wp/v2/search?search={quote_plus(keyword)}&per_page=1"
    results = json.loads(_reader_content(url))
    if not results or not _allowed(results[0].get("url", ""), source):
        raise ScrapeError("No ProPakistani search result found")
    return results[0]["url"]


def _reader_article(url: str) -> str:
    text = _reader_content(url)
    text = re.sub(r"!?\[([^]]*)\]\([^)]+\)", r"\1", text)
    if len(text) < 120:
        raise ScrapeError("Reader service returned too little article text")
    return text[:5000]


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
    url = None
    post_id = None
    try:
        if source.name == "ProPakistani":
            try:
                url, post_id = _wp_search(keyword, source)
            except (OSError, ValueError, KeyError, TypeError, ScrapeError):
                pass
        driver = _driver()
        url = url or _first_result(driver, source, keyword)
        driver.get(url)
        if not _allowed(driver.current_url, source):
            raise ScrapeError("Article redirected outside the assigned news source")
        WebDriverWait(driver, 12).until(lambda d: len(d.find_elements(By.TAG_NAME, "p")) >= 2)
        return driver.current_url, _article_text(driver.page_source)
    except (WebDriverException, ScrapeError) as exc:
        if post_id is not None and url is not None:
            try:
                return url, _wp_article(post_id)
            except (OSError, ValueError, KeyError, TypeError, ScrapeError):
                pass
        if source.name == "ProPakistani":
            try:
                url = url or _reader_search(keyword, source)
                return url, _reader_article(url)
            except (OSError, ValueError, KeyError, TypeError, ScrapeError):
                pass
        raise ScrapeError("Browser could not load the search result or article") from exc
    finally:
        if driver is not None:
            driver.quit()
