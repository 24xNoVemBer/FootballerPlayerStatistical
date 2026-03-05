import asyncio, re, random
from pathlib import Path
from playwright.async_api import async_playwright

CACHE_DIR = Path("E:\Project\FootballerPlayerStatistical\data\html_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

urls = [
    "https://fbref.com/en/squads/822bd0ba/Liverpool-Stats",
    "https://fbref.com/en/squads/18bb7c10/2024-2025/Arsenal-Stats",
    "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats",
    "https://fbref.com/en/squads/cff3d9bb/2024-2025/Chelsea-Stats",
    "https://fbref.com/en/squads/b2b47a98/2024-2025/Newcastle-United-Stats",
    "https://fbref.com/en/squads/8602292d/2024-2025/Aston-Villa-Stats",
    "https://fbref.com/en/squads/e4a775cb/2024-2025/Nottingham-Forest-Stats",
    "https://fbref.com/en/squads/d07537b9/2024-2025/Brighton-and-Hove-Albion-Stats",
    "https://fbref.com/en/squads/4ba7cbea/2024-2025/Bournemouth-Stats",
    "https://fbref.com/en/squads/cd051869/2024-2025/Brentford-Stats",
    "https://fbref.com/en/squads/fd962109/2024-2025/Fulham-Stats",
    "https://fbref.com/en/squads/47c64c55/2024-2025/Crystal-Palace-Stats",
    "https://fbref.com/en/squads/d3fd31cc/2024-2025/Everton-Stats",
    "https://fbref.com/en/squads/7c21e445/2024-2025/West-Ham-United-Stats",
    "https://fbref.com/en/squads/19538871/2024-2025/Manchester-United-Stats",
    "https://fbref.com/en/squads/8cec06e1/2024-2025/Wolverhampton-Wanderers-Stats",
    "https://fbref.com/en/squads/361ca564/2024-2025/Tottenham-Hotspur-Stats",
    "https://fbref.com/en/squads/a2d435b3/2024-2025/Leicester-City-Stats",
    "https://fbref.com/en/squads/b74092de/2024-2025/Ipswich-Town-Stats",
    "https://fbref.com/en/squads/33c895d4/2024-2025/Southampton-Stats"
]

def slugify(url):
    return re.sub(r"[^a-zA-Z0-9\-]+", "_", url.rstrip("/").split("/")[-1])

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for i, url in enumerate(urls, 1):
            out = CACHE_DIR / f"{slugify(url)}.html"
            print(f"[{i}/{len(urls)}] {url}")

            # retry goto (domcontentloaded)
            for attempt in range(1, 4):
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    await page.wait_for_timeout(5000)
                    break
                except Exception as e:
                    print(f"  attempt {attempt} failed: {e}")
                    if attempt == 3:
                        raise
                    await page.wait_for_timeout(4000)

            html = await page.content()
            out.write_text(html, encoding="utf-8")

            size = out.stat().st_size
            print(f"   saved {out.name} size={size} bytes")

            # nếu file nhỏ quá -> chụp screenshot debug
            if size < 50_000:
                shot = CACHE_DIR / f"{slugify(url)}.png"
                await page.screenshot(path=str(shot), full_page=True)
                print(f"   WARNING small html, screenshot saved: {shot.name}")

            await asyncio.sleep(3 + random.random()*2)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())