"""
Ekstraksi Data BP2MI dari PDF BNP2TKI/BP2MI
=============================================
Mengekstrak data penempatan PMI per kabupaten/kota
dari laporan tahunan BP2MI/BNP2TKI (format PDF).

Requirements:
    pip install pdfplumber pandas

Cara pakai:
    python pipelines/bp2mi/ekstrak_bp2mi_pdf.py

Letakkan file PDF di: data/raw/bp2mi_pdf/
Output: data/processed/bp2mi_jatim_extracted.csv
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

PDF_DIR = Path("data/raw/bp2mi_pdf")
OUTPUT  = Path("data/processed/bp2mi_jatim_extracted.csv")

# Nama-nama kabupaten Jawa Timur yang dicari di teks PDF
KAB_JATIM = [
    'Pacitan','Ponorogo','Trenggalek','Tulungagung','Blitar','Kediri',
    'Malang','Lumajang','Jember','Banyuwangi','Bondowoso','Situbondo',
    'Probolinggo','Pasuruan','Sidoarjo','Mojokerto','Jombang','Nganjuk',
    'Madiun','Magetan','Ngawi','Bojonegoro','Tuban','Lamongan','Gresik',
    'Bangkalan','Sampang','Pamekasan','Sumenep',
    'Kota Kediri','Kota Blitar','Kota Malang','Kota Probolinggo',
    'Kota Pasuruan','Kota Mojokerto','Kota Madiun','Kota Surabaya','Kota Batu'
]

def extract_from_pdf(pdf_path: Path) -> pd.DataFrame:
    """Ekstrak tabel penempatan PMI dari satu file PDF."""
    print(f"\n📄 Memproses: {pdf_path.name}")
    results = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""

            # Cari baris yang mengandung nama kab Jawa Timur + angka
            for kab in KAB_JATIM:
                pattern = rf"{re.escape(kab)}\s+[\d,\.]+\s+([\d,\.]+)"
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        jumlah = int(match.replace(',', '').replace('.', ''))
                        results.append({
                            'nama_resmi': kab,
                            'jumlah_pmi': jumlah,
                            'source_file': pdf_path.name,
                            'page': page_num
                        })
                    except ValueError:
                        pass

            # Coba ekstrak tabel terstruktur
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                for row in table:
                    if not row:
                        continue
                    row_text = ' '.join([str(c) for c in row if c])
                    for kab in KAB_JATIM:
                        if kab.lower() in row_text.lower():
                            # Ekstrak semua angka dari baris
                            nums = [int(n.replace(',','').replace('.',''))
                                    for n in re.findall(r'[\d,\.]{2,}', row_text)
                                    if n.replace(',','').replace('.','').isdigit()]
                            if nums:
                                results.append({
                                    'nama_resmi': kab,
                                    'jumlah_pmi': max(nums),
                                    'source_file': pdf_path.name,
                                    'page': page_num
                                })

    df = pd.DataFrame(results).drop_duplicates()
    print(f"   → Ditemukan {len(df)} baris data")
    return df

def main():
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ Tidak ada file PDF di {PDF_DIR}")
        print("   Letakkan file PDF laporan tahunan BP2MI di folder tersebut.")
        return

    print(f"📁 Ditemukan {len(pdf_files)} file PDF")
    all_dfs = [extract_from_pdf(f) for f in pdf_files]
    combined = pd.concat(all_dfs, ignore_index=True)

    # Ambil nilai tertinggi per kab (kemungkinan angka terbesar = total tahunan)
    summary = (combined
               .groupby(['nama_resmi', 'source_file'])['jumlah_pmi']
               .max()
               .reset_index())

    summary.to_csv(OUTPUT, index=False)
    print(f"\n✅ Tersimpan: {OUTPUT}")
    print(f"   {len(summary)} baris data")
    print("\nContoh hasil:")
    print(summary.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
