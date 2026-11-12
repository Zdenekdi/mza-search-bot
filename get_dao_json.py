import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the DAO api url directly
        response = await page.goto('https://mza.cz/aron/api/aron/dao/b6aceb8c-8283-473d-8373-4d2b5306e8f9')
        if response.status == 200:
            content = await response.text()
            with open("dao.json", "w") as f:
                f.write(content)
            print("Successfully saved dao.json")
        else:
            print(f"Failed to fetch DAO, status: {response.status}")
        
        await browser.close()

asyncio.run(main())
