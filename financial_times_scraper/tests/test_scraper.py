from financial_times_scraper.app.scraper.ft_scraper import parse_article_links, fetch_article, scrape_ft, save_article
import pytest



@pytest.mark.asyncio
async def test_parse_article_links():
    """
    Тест перевіряє, що parse_article_links коректно витягує
    унікальні посилання на статті з HTML.
    Входить:
        html (str) - HTML код з кількома посиланнями.
    Вихід:
        list[str] - список правильних URL з ft.com.
    """
    html = """
    <html><body>
    <a class="js-teaser-heading-link" href="/content/abc123">Article 1</a>
    <a class="js-teaser-heading-link" href="https://www.ft.com/content/def456">Article 2</a>
    <a class="js-teaser-heading-link" href="https://external.com/page">Ignore me</a>
    </body></html>
    """
    links = await parse_article_links(html)
    assert "https://www.ft.com/content/abc123" in links
    assert "https://www.ft.com/content/def456" in links
    assert all(link.startswith("https://www.ft.com/content/") for link in links)
    assert len(links) == 2


@pytest.mark.asyncio
async def test_fetch_article_structure():
    """
    Тест перевіряє, що fetch_article повертає словник із
    усіма ключами та правильними типами даних.
    Входить:
        url (str) - URL статті.
    Вихід:
        dict - з інформацією про статтю.
    """
    url = "https://www.ft.com/content/09ae581b-fe38-49f5-89b2-7c8c6dccd9a3"
    article_data = await fetch_article(url)

    assert isinstance(article_data, dict)
    assert article_data.get("url") == url
    assert "title" in article_data and isinstance(article_data["title"], str)
    assert "content" in article_data and isinstance(article_data["content"], str)
    assert "author" in article_data
    assert "published_at" in article_data
    assert "scraped_at" in article_data
    assert isinstance(article_data["word_count"], int)


@pytest.mark.asyncio
async def test_scrape_ft_handles_exceptions(monkeypatch):
    """
    Тестує, що scrape_ft не падає при помилках парсингу статті,
    а коректно їх обробляє і продовжує роботу.
    """
    async def fake_fetch_html(session, url):
        return """
        <html><body>
        <a class="js-teaser-heading-link" href="/content/abc123">Article 1</a>
        </body></html>
        """

    async def fake_parse_article_links(html):
        return ["https://www.ft.com/content/abc123"]

    async def fake_fetch_article(url):
        raise Exception("Simulated fetch error")

    monkeypatch.setattr("financial_times_scraper.app.scraper.fetch_html", fake_fetch_html)
    monkeypatch.setattr("financial_times_scraper.app.scraper.parse_article_links", fake_parse_article_links)
    monkeypatch.setattr("financial_times_scraper.app.scraper.fetch_article", fake_fetch_article)

    # Запуск має не викидати, а лише логувати помилку
    await scrape_ft()