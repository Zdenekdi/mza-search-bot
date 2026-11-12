import asyncio
import os
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        print("1. Otevírám katalog...")
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(3000)
        
        await page.fill("input[name='patternFulltext']", "BBČ N1 O1 Z1")
        await page.click("input[name='searchFulltext']")
        await page.wait_for_timeout(5000)
        
        await page.get_by_text("BBČ N1O1Z1").first.click()
        await page.wait_for_timeout(4000)
        
        print("5. Hledám odkaz na prohlížeč z HTML...")
        content = await page.content()
        match = re.search(r'href="([^"]*Zoomify\.action[^"]*)"', content)
        
        if match:
            # Oprava entit v URL
            raw_url = match.group(1).replace("&amp;", "&")
            url = "http://katalog.ahmp.cz" + raw_url
            print("Nalezeno URL prohlížeče:", url)
            
            print("6. Přecházím přímo na URL prohlížeče...")
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(6000)
            
            print("Fotím první stránky...")
            # V prohlížeči zkusíme klikat na ikonu "Další" nebo mačkat šipku
            for i in range(1, 11):
                await page.screenshot(path=f"ahmp_stranka_{i}.png", full_page=False)
                print(f"Stránka {i} vyfocena.")
                
                # Zkusíme poslat šipku doprava.
                await page.keyboard.press("ArrowRight")
                await page.wait_for_timeout(3500)
        else:
            print("Odkaz na prohlížeč nebyl nalezen v HTML.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
