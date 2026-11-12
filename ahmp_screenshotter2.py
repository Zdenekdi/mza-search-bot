import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("1. Otevírám hlavní katalog AHMP...")
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        
        print("2. Jdu na vyhledávání...")
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(3000)
        
        print("3. Vyplňuji hlavní vyhledávací políčko...")
        await page.fill("input[name='patternFulltext']", "BBČ N1 O1 Z1")
        # Klikneme na tlačítko lupy (searchFulltext)
        await page.click("input[name='searchFulltext']")
        
        await page.wait_for_timeout(4000)
        
        await page.screenshot(path="ahmp_step3_results_fulltext.png")
        print("Výsledky uloženy. Jdu se podívat...")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
