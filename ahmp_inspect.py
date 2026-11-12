import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(2000)
        
        # main search bar is often the first input with type text inside a specific class,
        # but let's find the input next to the search button (magnifying glass)
        # or fill the top search bar
        search_inputs = await page.locator(".x-form-text").all()
        for i, inp in enumerate(search_inputs):
            try:
                print(f"Input {i}: id={await inp.get_attribute('id')}, name={await inp.get_attribute('name')}")
            except:
                pass
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
