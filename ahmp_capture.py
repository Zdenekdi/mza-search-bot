import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Otevírám hlavní katalog AHMP...")
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        
        print("Klikám na 'Procházet a hledat'...")
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(3000)
        
        print("Hledám pole Signatura...")
        # V ExtJS je popisek většinou div nebo label. Najdeme prvek s textem "Signatura:" a pak input hned pod ním.
        # Nebo jednoduše najdeme input podle jména nebo ID, jestli nějaké má. 
        # Zkusíme kliknout na to hlavní hledací pole nahoře (vedle lupy).
        # To pole má obvykle jméno "query" nebo něco podobného, ale minule to selhalo.
        
        # Pojďme najít všechny inputy a vypsat je
        # Můžeme použít XPath: Najdi input, který má nad sebou text Signatura:
        # ExtJS grid často vypadá složitě. Můžeme použít bounding box.
        
        try:
            # Zkusme vyplnit horní políčko s lupou. Obvykle je to div s třídou 'search-field' nebo podobně.
            # Nejjednodušší: zmáčkneme Tab a napíšeme to? Ne.
            
            # Najdi první label "Signatura:"
            sig_label = page.locator("text=Signatura:")
            # Pak najdeme input, který je nejblíže
            # v ExtJS je struktura: <div class="x-form-item"><label>Signatura:</label><div class="x-form-element"><input></div></div>
            await page.locator("xpath=//label[text()='Signatura:']/../..//input").fill("BBČ N1 O1 Z1")
            await page.keyboard.press("Enter")
            
            await page.wait_for_timeout(5000)
            await page.screenshot(path="ahmp_results2.png")
            print("Snímek výsledků uložen!")
            
        except Exception as e:
            print("Chyba:", e)
            await page.screenshot(path="ahmp_error.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
