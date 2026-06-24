"""
Hitung Migration Proxy Index (MPI)
====================================
Membangun MPI dari komponen yang tersedia:
- BP2MI per kapita (MPI-OUT backbone)
- MMI Meta (MPI-IN)
- ILKD LinkedIn (MPI-IN)

Requirements:
    pip install pandas numpy scipy

Cara pakai:
    python pipelines/mpi/hitung_mpi.py

Output:
    data/processed/mpi_final.csv
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# ── File input ────────────────────────────────────────────────────────────────
MASTER  = Path("data/processed/master_enriched.csv")
ILKD    = Path("data/processed/ilkd_robust_jatim.csv")
BP2MI   = Path("data/processed/bp2mi_jatim_2011_2025_final.csv")
OUTPUT  = Path("data/processed/mpi_final.csv")

# Mapping BP2MI nama → kode BPS
BP2MI_TO_KODE = {
    'Pacitan':3501,'Ponorogo':3502,'Trenggalek':3503,'Tulungagung':3504,
    'Blitar':3505,'Kediri':3506,'Malang':3507,'Lumajang':3508,'Jember':3509,
    'Banyuwangi':3510,'Bondowoso':3511,'Situbondo':3512,'Probolinggo':3513,
    'Pasuruan':3514,'Sidoarjo':3515,'Mojokerto':3516,'Jombang':3517,
    'Nganjuk':3518,'Madiun':3519,'Magetan':3520,'Ngawi':3521,'Bojonegoro':3522,
    'Tuban':3523,'Lamongan':3524,'Gresik':3525,'Bangkalan':3526,'Sampang':3527,
    'Pamekasan':3528,'Sumenep':3529,'Kota Kediri':3571,'Kota Blitar':3572,
    'Kota Malang':3573,'Kota Probolinggo':3574,'Kota Pasuruan':3575,
    'Kota Mojokerto':3576,'Kota Madiun':3577,'Kota Surabaya':3578,'Kota Batu':3579,
}

def minmax(series):
    """Normalisasi min-max ke 0-100."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - mn) / (mx - mn) * 100

def main():
    # ── Load data ─────────────────────────────────────────────────────────────
    master = pd.read_csv(MASTER)
    bp2mi  = pd.read_csv(BP2MI)
    bp2mi['kode_kab'] = bp2mi['nama_resmi'].map(BP2MI_TO_KODE)
    bp_avg = dict(zip(bp2mi['kode_kab'], bp2mi['avg_2016_2020']))
    master['bp2mi_avg']  = master['kode_kab'].map(bp_avg)
    master['bp2mi_rate'] = master['bp2mi_avg'] / master['pop_sp2020'] * 1000

    # Coba load ILKD (opsional)
    if ILKD.exists():
        ilkd = pd.read_csv(ILKD)
        ilkd_map = dict(zip(ilkd['kab_kota'], ilkd['total_loker_linkedin']))
        # Match nama (simplified)
        master['ilkd_raw'] = master['kode_kab'].map(
            {k: v for k, v in ilkd_map.items()}
        ).fillna(0)
        master['ilkd_rate'] = master['ilkd_raw'] / master['pop_sp2020'] * 1000
        print("✅ ILKD LinkedIn loaded")
    else:
        master['ilkd_rate'] = 0
        print("⚠️  ILKD tidak ditemukan, diset 0")

    # ── Normalisasi komponen ───────────────────────────────────────────────────
    master['BP2MI_norm'] = minmax(master['bp2mi_rate'])
    master['MMI_norm']   = minmax(master['mean_fraction'])   if 'mean_fraction' in master.columns else 0
    master['ILKD_norm']  = minmax(master['ilkd_rate'])

    # ── MPI-OUT = BP2MI(50%) + IPTD(30%=0) + IMMG(20%=0) ────────────────────
    master['MPI_OUT'] = minmax(0.5 * master['BP2MI_norm'])

    # ── MPI-IN = MMI(40%) + ILKD(35%) + ITKJ(25%=0) ─────────────────────────
    master['MPI_IN'] = minmax(
        0.40 * master['MMI_norm'] + 0.35 * master['ILKD_norm']
    )

    # ── MPI-NET ───────────────────────────────────────────────────────────────
    master['MPI_NET'] = minmax(master['MPI_OUT'] - master['MPI_IN'])
    master['rank_MPI'] = master['MPI_NET'].rank(ascending=False).astype(int)

    # ── Validasi Spearman vs SP2020 ───────────────────────────────────────────
    if 'net_rate_permil' in master.columns:
        rho, pval = stats.spearmanr(
            master['MPI_NET'], master['net_rate_permil'], nan_policy='omit'
        )
        print(f"\n📊 Validasi Spearman (MPI_NET vs SP2020 net rate):")
        print(f"   ρ = {rho:.3f}, p = {pval:.4f}")
        sig = '***' if pval<0.001 else '**' if pval<0.01 else '*' if pval<0.05 else 'n.s.'
        print(f"   Signifikansi: {sig}")

    # ── Output ────────────────────────────────────────────────────────────────
    cols_out = ['kode_kab','nama_resmi','pop_sp2020','bp2mi_rate',
                'BP2MI_norm','MMI_norm','ILKD_norm',
                'MPI_OUT','MPI_IN','MPI_NET','rank_MPI']
    result = master[[c for c in cols_out if c in master.columns]]
    result.to_csv(OUTPUT, index=False)

    print(f"\n✅ MPI tersimpan: {OUTPUT}")
    print(f"\nTop 10 sender (MPI_NET tinggi):")
    print(result.nsmallest(10,'rank_MPI')[['nama_resmi','bp2mi_rate','MPI_OUT','MPI_IN','MPI_NET','rank_MPI']].to_string(index=False))

if __name__ == "__main__":
    main()
