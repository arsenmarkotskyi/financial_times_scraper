import pytest
import asyncio
from financial_times_scraper.app.scraper.ft_scraper import scrape_ft


@pytest.mark.asyncio
async def test_scrape():
    await scrape_ft()

if __name__ == "__main__":
    asyncio.run(test_scrape())
