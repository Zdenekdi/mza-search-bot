import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(3000)
        
        await page.fill("input[name='patternFulltext']", "BBČ N1 O1 Z1")
        await page.click("input[name='searchFulltext']")
        await page.wait_for_timeout(5000)
        
        await page.get_by_text("BBČ N1O1Z1").first.click()
        await page.wait_for_timeout(4000)
        
        # Dump entire page content
        content = await page.content()
        with open("ahmp_detail.html", "w") as f:
            f.write(content)
            
        print("Uložil jsem ahmp_detail.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
