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
        await page.click("input[name='searchFulltext']")
        
        await page.wait_for_timeout(5000)
        
        print("4. Klikám na nalezený záznam...")
        # Text ve výsledcích je "BBČ N1O1Z1 • 1667-1737" (bez mezer v signatuře)
        try:
            # Zkusíme kliknout rovnou na ikonu obrázku úplně vpravo, jestli je to tlačítko na prohlížeč.
            # Bývá to <img src="...ico_digital.gif"> nebo podobně. Můžeme hledat jakýkoliv obrázek v row
            img_icons = await page.locator(".x-grid3-cell-inner img").all()
            if len(img_icons) > 0:
                await img_icons[-1].click() # Poslední ikonka vpravo
            else:
                # Pokud ne, klikneme na text
                await page.get_by_text("BBČ N1O1Z1").first.click()
            
            await page.wait_for_timeout(5000)
            await page.screenshot(path="ahmp_step4_detail_or_viewer.png")
            
        except Exception as e:
            print("Chyba při klikání na detail:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
