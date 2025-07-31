from fastapi import FastAPI

from financial_times_scraper.app.scraper import scrape_ft

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, Financial Times!"}



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