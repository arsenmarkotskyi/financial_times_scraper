import ssl
import certifi
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from financial_times_scraper.app.database import AsyncSessionLocal
from financial_times_scraper.app.models import Article
import asyncio
from sqlalchemy.future import select

BASE_URL = "https://www.ft.com/world"

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch {url}, status: {response.status}")
        return await response.text()

async def parse_article_links(html: str):
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for a in soup.select("a.js-teaser-heading-link"):
        href = a.get("href")
        if href and href.startswith("https://www.ft.com/content/"):
            articles.append(href)
    return list(set(articles))

async def fetch_article(session: aiohttp.ClientSession, url: str):
    html = await fetch_html(session, url)
    soup = BeautifulSoup(html, "html.parser")

    paywall = soup.select_one(".paywall")
    if paywall:
        return None

    title = soup.select_one("h1").text.strip() if soup.select_one("h1") else ""
    content_parts = soup.select("div.article-body p")
    content = "\n".join(p.text.strip() for p in content_parts) if content_parts else ""
    author = soup.select_one(".author-name")
    author_text = author.text.strip() if author else None
    published_at_str = soup.select_one("time")["datetime"] if soup.select_one("time") else None
    published_at = datetime.fromisoformat(published_at_str) if published_at_str else None

    subtitle = None
    tags = []
    image_url = None
    word_count = len(content.split())
    reading_time = None
    related_articles = []

    return {
        "url": url,
        "title": title,
        "content": content,
        "author": author_text,
        "published_at": published_at,
        "scraped_at": datetime.utcnow(),
        "subtitle": subtitle,
        "tags": tags,
        "image_url": image_url,
        "word_count": word_count,
        "reading_time": reading_time,
        "related_articles": related_articles
    }

async def save_article(data: dict):
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
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        html = await fetch_html(session, BASE_URL)
        links = await parse_article_links(html)
        for url in links:
            article_data = await fetch_article(session, url)
            if article_data:
                saved = await save_article(article_data)
                if saved:
                    print(f"Saved article: {article_data['title']}")
                else:
                    print(f"Article already exists: {article_data['url']}")

