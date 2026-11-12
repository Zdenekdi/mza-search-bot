import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Uděláme větší okno, abychom měli co nejlepší rozlišení pro matriku
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
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
        # Zkusíme kliknout na ikonku obrázku v tabulce výsledků
        img_icons = await page.locator(".x-grid3-cell-inner img").all()
        if len(img_icons) > 0:
            await img_icons[-1].click()
        else:
            await page.get_by_text("BBČ N1O1Z1").first.click()
            
        await page.wait_for_timeout(4000)
        
        print("5. Otevírám prohlížeč kliknutím na obálku knihy...")
        # Klikneme na obrázek obálky knihy (nebo na text pod ním)
        try:
            # Obvykle má obrázek v detailu specifickou třídu nebo je to prostě obrázek v pravém panelu
            # Klikneme na text s počtem obrázků
            img_texts = await page.locator("text=/obrázků Zobrazeno/").all()
            if img_texts:
                await img_texts[0].click()
            else:
                # Najdeme všechny obrázky a klikneme na ten největší/poslední
                all_imgs = await page.locator("img").all()
                await all_imgs[-1].click()
                
            await page.wait_for_timeout(6000)
            await page.screenshot(path="ahmp_step6_viewer.png")
            print("Prohlížeč by měl být otevřený!")
            
            # Zkusíme přepnout na celou obrazovku, pokud tam je tlačítko,
            # a udělat pár screenshotů.
            for i in range(1, 4):
                # Skryjeme UI prvky, pokud to jde (v ExtJS často panely s class .x-panel)
                # nebo prostě uděláme screenshot.
                await page.screenshot(path=f"ahmp_stranka_{i}.png", full_page=False)
                print(f"Stránka {i} vyfocena.")
                # Kliknutí na další stránku - často to jde klávesou PageDown nebo šipkou
                await page.keyboard.press("ArrowRight")
                await page.wait_for_timeout(3000)
                
        except Exception as e:
            print("Chyba při otevírání prohlížeče:", e)
            await page.screenshot(path="ahmp_error_viewer.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
