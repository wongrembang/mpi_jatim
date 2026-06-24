"""
Scraper LinkedIn Jobs - Jawa Timur (Weekly Run)
================================================
Jalankan sekali seminggu selama 4-6 minggu sebelum deadline.
Output: data/raw/ilkd_weekly/ilkd_YYYY-MM-DD.csv

Requirements:
    pip install playwright pandas
    playwright install chromium

Cara pakai:
    python pipelines/linkedin/scraper_linkedin_weekly.py
"""

import asyncio
import pandas as pd
from datetime import date
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Install dulu: pip install playwright && playwright install chromium")
    exit(1)

# Daftar kab/kota Jawa Timur untuk query LinkedIn
KAB_KOTA = [
    "Surabaya", "Malang", "Sidoarjo", "Gresik", "Mojokerto",
    "Pasuruan", "Probolinggo", "Jember", "Banyuwangi", "Madiun",
    "Kediri", "Blitar", "Tulungagung", "Ponorogo", "Ngawi",
    "Magetan", "Trenggalek", "Pacitan", "Wonogiri", "Bojonegoro",
    "Tuban", "Lamongan", "Jombang", "Nganjuk", "Madiun Kota",
    "Kediri Kota", "Blitar Kota", "Malang Kota", "Probolinggo Kota",
    "Pasuruan Kota", "Mojokerto Kota", "Madiun Kota", "Batu",
    "Lumajang", "Bondowoso", "Situbondo", "Bangkalan", "Sampang",
    "Pamekasan", "Sumenep"
]

OUTPUT_DIR = Path("data/raw/ilkd_weekly")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def scrape_loker(kab: str, page) -> int:
    """Ambil jumlah lowongan LinkedIn untuk satu kab/kota."""
    try:
        url = f"https://www.linkedin.com/jobs/search/?keywords=&location={kab}%2C+Jawa+Timur%2C+Indonesia&f_TPR=r2592000"
        await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # Cari elemen hasil
        selectors = [
            ".results-context-header__job-count",
            ".jobs-search-results-list__subtitle",
            'span[data-tracking-control-name="public_jobs_jobs-search-bar_search-submit"]',
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    txt = await el.inner_text()
                    # Ekstrak angka
                    import re
                    nums = re.findall(r'[\d,]+', txt.replace('.', '').replace(',', ''))
                    if nums:
                        count = int(nums[0])
                        return min(count, 1000)  # cap di 1000
            except:
                pass

        # Fallback: hitung item list
        items = await page.query_selector_all(".job-search-card")
        return min(len(items), 1000)

    except Exception as e:
        print(f"  ⚠️  {kab}: {e}")
        return 0

async def main():
    today = date.today().isoformat()
    output_file = OUTPUT_DIR / f"ilkd_{today}.csv"

    print(f"🔍 LinkedIn Scraper — Jawa Timur")
    print(f"📅 Tanggal: {today}")
    print(f"📁 Output: {output_file}")
    print(f"{'='*50}")

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        for i, kab in enumerate(KAB_KOTA, 1):
            print(f"[{i:02d}/{len(KAB_KOTA)}] Scraping: {kab}...")
            count = await scrape_loker(kab, page)
            results.append({"kab_kota": kab, "total_loker": count, "tanggal": today})
            print(f"         → {count:,} loker")
            await asyncio.sleep(1.5)  # jeda antar request

        await browser.close()

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)

    print(f"\n{'='*50}")
    print(f"✅ Selesai! {len(df)} kab/kota tersimpan.")
    print(f"📊 Total loker: {df['total_loker'].sum():,}")
    print(f"📁 File: {output_file}")
    print(f"\nTop 10 kab/kota:")
    print(df.nlargest(10, 'total_loker')[['kab_kota','total_loker']].to_string(index=False))

if __name__ == "__main__":
    asyncio.run(main())
