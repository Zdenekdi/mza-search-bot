import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://mza.cz/aron/apu/b6aceb8c-8283-473d-8373-4d2b5306e8f9/dao/b6aceb8c-8283-473d-8373-4d2b5306e8f9/file/9a8d4a96-4e90-47b4-a616-1a8ec474b1b4', timeout=60000)
        await page.wait_for_timeout(5000)
        content = await page.content()
        with open("aron_page.html", "w") as f:
            f.write(content)
        await browser.close()

asyncio.run(main())
