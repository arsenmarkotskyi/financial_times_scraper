import ssl
import certifi
import aiohttp

from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright

from financial_times_scraper.app.database import AsyncSessionLocal
from financial_times_scraper.app.models import Article
from sqlalchemy.future import select

BASE_URL = "https://www.ft.com/world"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    """
        Завантажує HTML сторінки за вказаною URL.

        Args:
            session (aiohttp.ClientSession): активна HTTP сесія.
            url (str): адреса сторінки для завантаження.

        Returns:
            str: HTML-код сторінки.

        Raises:
            Exception: якщо статус відповіді не 200.
        """
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch {url}, status: {response.status}")
        return await response.text()

async def parse_article_links(html: str):
    """
        Парсить HTML головної сторінки та витягує унікальні посилання на статті.

        Args:
            html (str): HTML-код головної сторінки.

        Returns:
            list[str]: список URL статей.
        """
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for a in soup.select("a.js-teaser-heading-link"):
        href = a.get("href")
        if href:
            if href.startswith("/content/"):
                href = "https://www.ft.com" + href
            if href.startswith("https://www.ft.com/content/"):
                articles.append(href)
    return list(set(articles))

async def fetch_article(url: str):
    """
        Завантажує та парсить HTML статті, витягує інформацію про статтю.

        Args:
            url (str): URL статті.

        Returns:
            dict: дані статті (url, title, content, author, published_at, тощо).
        """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle')
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")

    meta_authors = soup.select("meta[property='article:author']")
    authors = [tag["content"] for tag in meta_authors if tag.get("content")]
    author_text = ", ".join(authors) if authors else None

    title = soup.select_one("h1").text.strip() if soup.select_one("h1") else ""

    content_parts = soup.select("div.article-body p")
    content = "\n".join(p.text.strip() for p in content_parts) if content_parts else ""

    time_tag = soup.select_one("time")
    published_at_str = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else None
    published_at = datetime.fromisoformat(published_at_str) if published_at_str else None

    print(f"""
--- Parsed article ---
Title: {title}
Author(s): {author_text}
Published at: {published_at}
URL: {url}
Content snippet: {content[:100]}...
""")

    return {
        "url": url,
        "title": title,
        "content": content,
        "author": author_text,
        "published_at": published_at,
        "scraped_at": datetime.now(timezone.utc),
        "subtitle": None,
        "tags": [],
        "image_url": None,
        "word_count": len(content.split()),
        "reading_time": None,
        "related_articles": []
    }



async def save_article(data: dict):
    """
        Зберігає статтю в базу даних, якщо її там ще немає.

        Args:
            data (dict): дані статті.

        Returns:
            bool: True якщо статтю збережено, False якщо вона вже є.
        """
    async with AsyncSessionLocal() as session:
        q = await session.execute(select(Article).where(Article.url == data["url"]))
        exists = q.scalars().first()
        if exists:
            return False  # Уже є
        article = Article(**data)
        session.add(article)
        await session.commit()
        return True

async def scrape_ft():
    """
        Основна функція скрапінгу: завантажує головну сторінку, парсить посилання,
        обробляє кожну статтю, зберігає нові статті, які опубліковані за останню годину.
        """
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context), headers=headers) as session:
        print("Fetching main page HTML...")
        html = await fetch_html(session, BASE_URL)
        print("Parsing article links...")
        links = await parse_article_links(html)
        print(f"Found {len(links)} article links")

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        for url in links:
            try:

                print(f"Processing: {url}")
                article_data = await fetch_article(url)

                if article_data and article_data["published_at"]:
                    if article_data["published_at"] > one_hour_ago:
                        saved = await save_article(article_data)
                        if saved:
                            print(f"Saved article: {article_data['title']}")
                        else:
                            print(f"Article already exists: {article_data['url']}")
                    else:
                        print(f"Skipped article published before last hour: {url}")
                else:
                    print(f"Skipped article with no published date or empty content: {url}")
            except Exception as e:
                print(f"Error processing article {url}: {e}")


if __name__ == "__main__":
    import asyncio


    async def periodic_scrape():
        """
        Запускає нескінченний цикл скрапінгу з інтервалом в 1 годину.
        """
        while True:
            print("Starting scrape cycle...")
            await scrape_ft()
            print("Scrape cycle done. Sleeping 1 hour...")
            await asyncio.sleep(3600)


    asyncio.run(periodic_scrape())
