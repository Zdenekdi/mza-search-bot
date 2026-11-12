import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Otevírám hlavní katalog AHMP...")
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        
        # We need to wait for the page to load
        await page.wait_for_timeout(2000)
        print("Titulní strana načtena.")
        
        # Try to find the search input
        # Pragapublica usually has a simple search bar on the homepage or requires clicking "Vyhledávání"
        # Let's take a screenshot to see what it looks like if we fail
        try:
            print("Klikám na 'Procházet a hledat'...")
            # Locate by text
            await page.get_by_text("Procházet a hledat").click()
            await page.wait_for_timeout(3000)
            
            # Now take a screenshot of the search tab
            await page.screenshot(path="ahmp_search.png")
            print("Snímek obrazovky vyhledávání uložen.")
            
            # Now let's try to fill the search box (placeholder or text)
            # ExtJS often uses input[type='text'] with specific classes, but get_by_role is better
            inputs = await page.locator("input[type='text']").all()
            if inputs:
                # fill the first one which is usually the search bar
                await inputs[0].fill("BBČ N1 O1 Z1")
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(5000)
                await page.screenshot(path="ahmp_results.png")
                print("Snímek obrazovky výsledků uložen.")
            
        except Exception as e:
            print("Chyba při hledání:", e)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
