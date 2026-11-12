import asyncio
from playwright.async_api import async_playwright
import json
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Intercept and log all network requests that return JSON
        def handle_response(response):
            if "api/aron" in response.url:
                print(f"API Request: {response.url} - Status: {response.status}")
        
        page.on('response', handle_response)
        
        print("Navigating to the main view URL...")
        await page.goto('https://mza.cz/aron/apu/b6aceb8c-8283-473d-8373-4d2b5306e8f9/dao/b6aceb8c-8283-473d-8373-4d2b5306e8f9/file/9a8d4a96-4e90-47b4-a616-1a8ec474b1b4', timeout=60000)
        await page.wait_for_timeout(10000)
        
        print("Finding apu/daos in localStorage or window state...")
        # Check window state for the APU DAOs
        state = await page.evaluate("window.localStorage.getItem('aron-state') || ''")
        with open("aron_state.txt", "w") as f:
            f.write(state)
            
        await browser.close()

asyncio.run(main())
