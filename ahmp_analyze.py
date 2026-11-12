import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("http://katalog.ahmp.cz/pragapublica/")
        await page.wait_for_timeout(3000)
        
        await page.get_by_text("Procházet a hledat").click()
        await page.wait_for_timeout(3000)
        
        # Získáme informace o všech input polích na stránce
        inputs = await page.evaluate('''() => {
            const elements = document.querySelectorAll('input');
            const data = [];
            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                data.push({
                    type: el.type,
                    id: el.id,
                    name: el.name,
                    className: el.className,
                    placeholder: el.placeholder,
                    value: el.value,
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    isVisible: rect.width > 0 && rect.height > 0
                });
            });
            return data;
        }''')
        
        with open('inputs.json', 'w') as f:
            json.dump(inputs, f, indent=2)
            
        print("Uložil jsem strukturu inputů do inputs.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
