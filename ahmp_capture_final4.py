import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Uděláme větší okno
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
        
        print("5. Hledám odkaz na prohlížeč a otevírám ho...")
        # Klikneme a počkáme na nový tab (popup)
        try:
            async with page.expect_popup(timeout=15000) as popup_info:
                await page.locator("[title='Zobrazit v plné kvalitě']").first.click()
            
            viewer_page = await popup_info.value
            await viewer_page.wait_for_load_state("domcontentloaded")
            await viewer_page.wait_for_timeout(6000)
            
            print("Prohlížeč otevřen. Fotím první stránky...")
            # V prohlížeči zkusíme klikat na ikonu "Další" nebo mačkat šipku
            for i in range(1, 11):
                await viewer_page.screenshot(path=f"ahmp_stranka_{i}.png", full_page=False)
                print(f"Stránka {i} vyfocena.")
                
                # Zkusíme poslat šipku doprava. Zoomify v ExtJS často reaguje na šipky, nebo můžeme zkusit najít tlačítko "Další snímek"
                await viewer_page.keyboard.press("ArrowRight")
                
                # Pro jistotu zkusíme kliknout na případné tlačítko doprava (class=z-btn-next atd)
                try:
                    await viewer_page.locator(".fa-arrow-right").first.click(timeout=1000)
                except:
                    pass
                
                await viewer_page.wait_for_timeout(3500)
        except Exception as e:
            print("Chyba při práci s prohlížečem:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
