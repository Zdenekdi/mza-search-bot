import asyncio
import os
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
        
        # Klik na první záznam
        await page.get_by_text("BBČ N1O1Z1").first.click()
        await page.wait_for_timeout(4000)
        
        print("5. Klikám na obrázek knihy pomocí titulku 'Zobrazit v plné kvalitě'...")
        # Zkusíme najít element s tímto titulkem (což je to, co se ukázalo na posledním screenshotu)
        try:
            await page.locator("[title='Zobrazit v plné kvalitě']").first.click()
        except:
            # Fallback na double click souřadnicemi
            await page.mouse.dblclick(1100, 450)
            
        await page.wait_for_timeout(8000)
        
        await page.screenshot(path="ahmp_step6_final_viewer.png")
        print("Snímek prohlížeče uložen.")
        
        # Uděláme 10 screenshotů a posuneme stránku dál
        for i in range(1, 11):
            await page.screenshot(path=f"ahmp_stranka_{i}.png", full_page=False)
            print(f"Stránka {i} vyfocena.")
            # V ExtJS/Zoomify vieweru funguje šipka doprava na další stránku, nebo kliknutí na ikonu
            await page.keyboard.press("ArrowRight")
            await page.wait_for_timeout(3500)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
