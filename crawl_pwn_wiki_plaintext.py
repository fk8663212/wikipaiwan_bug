import os
import time
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://pwn.wikipedia.org"
START_INDEX_URL = (
    "https://pwn.wikipedia.org/w/index.php"
    "?title=pinakisumaljiyan:%E6%89%80%E6%9C%89%E9%A0%81%E9%9D%A2&from=1984"
)

HEADERS = {
    "User-Agent": "PaiwanCorpusCrawler/1.0 (contact: your_email@example.com)"
}


def sanitize_filename(name: str) -> str:
    """
    將條目名稱轉成可以安全當作檔名的字串
    """
    # 去掉 Windows / Linux 不允許的字元
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    # 避免檔名過長
    return name[:180]


def fetch_html(session: requests.Session, url: str) -> str:
    resp = session.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_allpages_index(html: str):
    soup = BeautifulSoup(html, "html.parser")

    article_links = []
    content_div = soup.find("div", id="mw-content-text")
    if not content_div:
        return article_links, None

    for li in content_div.find_all("li"):
        a = li.find("a")
        if not a:
            continue
        href = a.get("href", "")
        if not href.startswith("/wiki/"):
            continue

        title = a.get_text(strip=True)
        full_url = urljoin(BASE_URL, href)
        article_links.append((title, full_url))

    next_link = soup.find("a", string=lambda s: s and "下一頁" in s)
    next_url = urljoin(BASE_URL, next_link.get("href")) if next_link else None
    return article_links, next_url


def extract_article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    texts = []

    # 主標題
    title_tag = soup.find("h1", id="firstHeading")
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        if title_text:
            texts.append(title_text)

    # 內容區塊
    content_div = soup.find("div", id="mw-content-text")
    if not content_div:
        return "\n".join(texts)

    for node in content_div.find_all(["h2", "h3", "h4", "p", "li"]):
        text = node.get_text(" ", strip=True)
        if text:
            texts.append(text)

    return "\n".join(texts)


def crawl_all_article_urls() -> dict:
    session = requests.Session()
    all_articles = {}
    visited = set()

    next_url = START_INDEX_URL
    page_count = 0

    while next_url and next_url not in visited:
        page_count += 1
        print(f"[Index {page_count}] 爬目錄頁: {next_url}")
        visited.add(next_url)

        html = fetch_html(session, next_url)
        article_links, next_url = parse_allpages_index(html)

        print(f"  找到 {len(article_links)} 條目")
        for title, url in article_links:
            all_articles[url] = title

        time.sleep(1)

    print(f"總共收集到 {len(all_articles)} 筆條目 URL\n")
    return all_articles


def crawl_articles_to_files(article_dict: dict, output_dir: str):
    """
    每個條目寫成 outputs/文章名.txt
    """
    session = requests.Session()
    os.makedirs(output_dir, exist_ok=True)

    total = len(article_dict)
    for idx, (url, title) in enumerate(article_dict.items(), start=1):
        safe_title = sanitize_filename(title)
        output_path = os.path.join(output_dir, f"{safe_title}.txt")

        print(f"[{idx}/{total}] 爬 {title} -> {output_path}")

        try:
            html = fetch_html(session, url)
            text = extract_article_text(html)
        except Exception as e:
            print(f"  失敗: {e}")
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        time.sleep(1)


def main():
    print("== 收集全部條目 URL ==")
    articles = crawl_all_article_urls()

    print("== 下載所有條目並分檔 ==")
    crawl_articles_to_files(articles, "outputs")

    print("\n全部完成！輸出在 /outputs/ 資料夾內")


if __name__ == "__main__":
    main()
