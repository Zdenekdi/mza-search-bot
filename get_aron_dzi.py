import asyncio
from playwright.async_api import async_playwright
import re

dzi_links = []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Zapneme zachytávání requestů
        def handle_response(response):
            if ".dzi" in response.url:
                dzi_links.append(response.url)
                print(f"Found DZI: {response.url}")
        
        page.on('response', handle_response)
        
        print("Navigating to Lánové rejstříky...")
        await page.goto('https://mza.cz/aron/apu/b6aceb8c-8283-473d-8373-4d2b5306e8f9/dao/b6aceb8c-8283-473d-8373-4d2b5306e8f9/file/9a8d4a96-4e90-47b4-a616-1a8ec474b1b4', timeout=60000)
        await page.wait_for_timeout(10000)
        
        print(f"Total DZI found so far: {len(dzi_links)}")
        
        # Let's see if we can extract all images from the JS object or HTML
        # In Aron, usually there is a window.__INITIAL_STATE__ or similar
        content = await page.content()
        matches = re.findall(r'/srv/[A-Za-z0-9\-/_]+.jp2.dzi', content)
        if matches:
            print(f"Found {len(matches)} DZI in content!")
            for m in matches:
                url = "https://www.mza.cz/iipsrv/iipsrv.fcgi?Deepzoom=" + m
                if url not in dzi_links:
                    dzi_links.append(url)
                    
        with open("lanove_dzi_links.txt", "w") as f:
            for link in dzi_links:
                f.write(link + "\n")
        
        await browser.close()

asyncio.run(main())
