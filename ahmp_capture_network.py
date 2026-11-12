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
        
        content = await page.content()
        match = re.search(r'href="([^"]*Zoomify\.action[^"]*)"', content)
        
        if match:
            raw_url = match.group(1).replace("&amp;", "&")
            url = "http://katalog.ahmp.cz" + raw_url
            print("Nalezeno URL prohlížeče:", url)
            
            # Odposloucháváme síťové požadavky pro získání adres dlaždic nebo zdrojového obrázku
            page.on("response", lambda response: print("JPG URL:", response.url) if ".jpg" in response.url else None)
            
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # Najdeme input s číslem stránky a skočíme na 5
            try:
                inputs = await page.locator("input[type='text']").all()
                for inp in inputs:
                    val = await inp.input_value()
                    if val == "1" or val == "0":
                        await inp.fill("5")
                        await page.keyboard.press("Enter")
                        break
            except Exception as e:
                print("Přeskok na 5. stranu selhal:", e)
                
            await page.wait_for_timeout(5000)
            
            # Uložíme i zdroják prohlížeče
            viewer_html = await page.content()
            with open("ahmp_viewer.html", "w") as f:
                f.write(viewer_html)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
