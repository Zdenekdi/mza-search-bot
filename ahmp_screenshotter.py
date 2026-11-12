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
        
        print("3. Vyplňuji přesně políčko Signatura...")
        await page.fill("input[name='sign.not_analyzed']", "BBČ N1 O1 Z1")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)
        
        await page.screenshot(path="ahmp_step3_results.png")
        print("Výsledky uloženy. Jdu kliknout na první výsledek...")
        
        # Obvykle je výsledek v nějakém spanu s textem BBČ N1 O1 Z1 nebo "Sbírka matrik"
        # Nebo jen klikneme na první odkaz v tabulce výsledků.
        # ExtJS tree node často vypadá jako .x-tree-node-anchor nebo jen text.
        try:
            await page.get_by_text("BBČ N1 O1 Z1").first.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path="ahmp_step4_detail.png")
            print("Detail otevřen. Hledám ikonku fotoaparátu...")
            
            # Ikonka kamery má obvykle tooltip nebo třídu
            # Klikneme na obrázek nebo ikonku, která otevírá prohlížeč
            # Nebo prostě zkusíme kliknout na všechny elementy s třídou icon-camera nebo podobně.
            
            camera_icons = await page.locator(".icon-camera, .fa-camera, img[src*='camera']").all()
            if not camera_icons:
                 # sometimes it's text "Digitalizát"
                 camera_icons = await page.locator("text='Digitalizát'").all()
                 
            if camera_icons:
                await camera_icons[0].click()
                await page.wait_for_timeout(5000)
                await page.screenshot(path="ahmp_step5_viewer.png")
                print("Prohlížeč otevřen!")
                
                # Zkusíme rovnou udělat 5 screenshotů a klikat dál
                for i in range(1, 6):
                    await page.screenshot(path=f"ahmp_stranka_{i}.png", full_page=True)
                    print(f"Stránka {i} uložena.")
                    # Zkusíme poslat šipku doprava pro další stránku
                    await page.keyboard.press("ArrowRight")
                    await page.wait_for_timeout(3000)
            else:
                print("Nenašel jsem ikonku kamery.")
            
        except Exception as e:
            print("Chyba při proklikávání výsledku:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
