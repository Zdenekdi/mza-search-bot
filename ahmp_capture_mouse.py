import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1920x1080 viewport
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
        
        print("5. Klikám na obrázek knihy pomocí souřadnic (x=1100, y=500)...")
        # Souřadnice získány ze screenshotu (obrázek knihy je velký obdélník zhruba zde)
        await page.mouse.click(1100, 500)
        await page.wait_for_timeout(6000)
        
        await page.screenshot(path="ahmp_step6_mouse_viewer.png")
        print("Snímek po kliknutí uložen.")
        
        # Uděláme screenshoty
        for i in range(1, 4):
            await page.screenshot(path=f"ahmp_mouse_stranka_{i}.png", full_page=False)
            await page.keyboard.press("ArrowRight")
            await page.wait_for_timeout(3000)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
