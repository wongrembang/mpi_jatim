"""
Agregasi ILKD Mingguan → Rata-rata Robust
==========================================
Gabungkan semua file ilkd_YYYY-MM-DD.csv menjadi satu
rata-rata yang lebih stabil (mengurangi volatilitas mingguan).

Cara pakai:
    python pipelines/linkedin/gabung_ilkd_weekly.py

Output:
    data/processed/ilkd_robust_jatim.csv
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/ilkd_weekly")
OUTPUT   = Path("data/processed/ilkd_robust_jatim.csv")

def main():
    files = sorted(RAW_DIR.glob("ilkd_*.csv"))
    if not files:
        print(f"❌ Tidak ada file di {RAW_DIR}")
        print("   Jalankan dulu: python pipelines/linkedin/scraper_linkedin_weekly.py")
        return

    print(f"📂 Ditemukan {len(files)} file mingguan:")
    for f in files:
        print(f"   - {f.name}")

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        df['minggu'] = f.stem.replace('ilkd_', '')
        dfs.append(df)

    all_data = pd.concat(dfs, ignore_index=True)

    # Rata-rata per kab/kota
    robust = (all_data
              .groupby('kab_kota')
              .agg(
                  total_loker_mean=('total_loker', 'mean'),
                  total_loker_median=('total_loker', 'median'),
                  total_loker_max=('total_loker', 'max'),
                  n_minggu=('total_loker', 'count')
              )
              .reset_index()
              .rename(columns={'total_loker_mean': 'total_loker_linkedin'})
              .round(1))

    robust['total_loker_linkedin'] = robust['total_loker_linkedin'].round(0).astype(int)

    robust.to_csv(OUTPUT, index=False)

    print(f"\n✅ Tersimpan: {OUTPUT}")
    print(f"   {len(robust)} kab/kota, rata-rata dari {robust['n_minggu'].mean():.1f} minggu")
    print(f"\nTop 10 kab/kota berdasarkan rata-rata loker:")
    print(robust.nlargest(10, 'total_loker_linkedin')
                [['kab_kota','total_loker_linkedin','n_minggu']].to_string(index=False))

if __name__ == "__main__":
    main()
