import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

async def main():
    hashes = {}
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
            
            # Start on page 1
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # Budeme procházet stránky 5 až 60 (pokrývá to zhruba roky 1667 až 1680)
            for i in range(5, 61):
                try:
                    # Zadáme číslo stránky
                    inputs = await page.locator("input[type='text']").all()
                    for inp in inputs:
                        val = await inp.input_value()
                        if val.isdigit():
                            await inp.fill(str(i))
                            await page.keyboard.press("Enter")
                            break
                    
                    await page.wait_for_timeout(3000)
                    
                    # Extrahujeme hash z HTML DOMu
                    content2 = await page.content()
                    m2 = re.search(r'zoomifyImgPath\s*=\s*"([^"]+)"', content2)
                    if m2:
                        hashes[i] = m2.group(1)
                        print(f"Strana {i}: {hashes[i]}")
                    else:
                        print(f"Strana {i}: Hash nenalezen")
                        
                except Exception as e:
                    print(f"Chyba na straně {i}: {e}")
            
        await browser.close()
        
    with open("ahmp_hashes.json", "w") as f:
        json.dump(hashes, f, indent=4)
    print("Uloženo do ahmp_hashes.json")

if __name__ == "__main__":
    asyncio.run(main())
