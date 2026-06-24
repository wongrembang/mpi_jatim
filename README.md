# Migration Proxy Index (MPI) Jawa Timur

> **"Bukan yang Termiskin yang Merantau: Bukti Empiris Mobilitas Tenaga Kerja dan Ketimpangan Spasial di 38 Kabupaten/Kota Jawa Timur"**

**Tim Peneliti:**
- Dr. Nanang Widaryoko, S.ST, M.Si
- Tita Rosy, S.ST, M.E
- Miyan Andi Irawan, S.ST, M.S.E

**Instansi:** BPS Kabupaten Rembang  
**Topik:** Dinamika Mobilitas Tenaga Kerja dan Ketimpangan Spasial

---

## 🚀 Dashboard

**[👉 Lihat Dashboard Online](https://wongrembang.github.io/mpi_jatim)**

Dashboard interaktif dengan 9 halaman:
- 🏠 Beranda — temuan utama & validasi MPI
- 🗺️ Peta Spasial — LISA cluster map (Leaflet + OpenStreetMap)
- 📊 Ranking MPI — dumbbell chart + tabel sortable/filter/export CSV
- ⚖️ Ketimpangan — Williamson Index, Theil, Gini, CV trend
- ⬡ Tipologi Klassen — scatter plot interaktif
- 📈 Regresi Spasial — koefisien SEM + diagnostik model
- 📅 Tren BP2MI — data 2011–2024
- ⚖️ Bandingkan — side-by-side 2 kab/kota
- 📚 Metodologi — penjelasan 10 metode + AI Q&A

---

## 📊 Temuan Utama

| Temuan | Detail |
|--------|--------|
| **Bukan yang termiskin yang merantau** | Kemiskinan tidak berkorelasi dengan intensitas PMI (ρ=+0,037, n.s.). Hanya pertumbuhan PDRB yang signifikan (β=56.916, p=0,017**) |
| **Kluster spasial kuat** | Global Moran's I = 0,327*** — Gerbangkertosusila = penerima (HH); Koridor Mataraman = pengirim (LL) |
| **Paradoks Madura** | 4 kab termiskin (>14% kemiskinan) justru intensitas PMI terendah (<0,4/1000) |
| **Ketimpangan ekstrem** | Williamson Index Vw = 0,9883; Theil T = 0,3303; CV divergen (1,56→1,63) |
| **Validasi MPI** | MPI v2 (BP2MI per kapita): ρ=−0,616***; MPI v1 (Meta): ρ=−0,065 n.s. |

---

## 📁 Struktur Folder

```
mpi_jatim/
├── index.html                          # Dashboard (GitHub Pages)
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/                            # Data mentah (tidak di-commit jika besar)
│   │   ├── bp2mi_pdf/                  # PDF laporan tahunan BP2MI
│   │   └── ilkd_weekly/               # CSV hasil scraping LinkedIn mingguan
│   │
│   └── processed/                      # Data yang sudah diolah
│       ├── master_final.csv            # Dataset utama 38 kab/kota
│       ├── master_enriched.csv         # + region, klassen, bp2mi_rate
│       ├── bp2mi_jatim_2011_2025_final.csv
│       ├── mpi_comparison_v1_v2.csv
│       ├── gwr_final.csv
│       └── inequality_stats.json
│
├── pipelines/
│   ├── bp2mi/
│   │   └── ekstrak_bp2mi_pdf.py        # Ekstrak data dari PDF BP2MI
│   ├── linkedin/
│   │   ├── scraper_linkedin_weekly.py  # Scraper mingguan LinkedIn Jobs
│   │   └── gabung_ilkd_weekly.py       # Agregasi CSV mingguan → rata-rata
│   └── mpi/
│       └── hitung_mpi.py               # Hitung MPI dari komponen
│
└── paper/
    └── EJAVEC_MPI_JawaTimur_2025.docx  # Paper final (tidak di-commit)
```

---

## ⚙️ Setup & Penggunaan

### 1. Clone repo

```bash
git clone https://github.com/wongrembang/mpi_jatim.git
cd mpi_jatim
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Scraping LinkedIn (mingguan, 4-6 minggu)

```bash
# Jalankan sekali seminggu
python pipelines/linkedin/scraper_linkedin_weekly.py

# Setelah 4+ minggu, agregasi
python pipelines/linkedin/gabung_ilkd_weekly.py
```

### 4. Ekstrak data BP2MI dari PDF

```bash
# Letakkan file PDF di data/raw/bp2mi_pdf/
python pipelines/bp2mi/ekstrak_bp2mi_pdf.py
```

### 5. Hitung MPI

```bash
python pipelines/mpi/hitung_mpi.py
```

### 6. Buka dashboard lokal

```bash
python -m http.server 8080
# Buka: http://localhost:8080
```

---

## 📦 Data Sources

| Sumber | Indikator | Periode |
|--------|-----------|---------|
| BP2MI / BNP2TKI | PMI ditempatkan per kab/kota | 2011–2024 |
| Meta (HDX) | Migration Connectivity Index (MMI) | 2023 |
| LinkedIn Jobs | Jumlah lowongan lokal (ILKD) | 2024 |
| BPS SP2020 Long Form | Net migrasi seumur hidup & risen | 2020 |
| BPS Jawa Timur | IPM, Gini, TPT, Kemiskinan, PDRB | 2021–2023 |

---

## 🔬 Metode Analisis

- **Migration Proxy Index (MPI)** — composite index 6 sub-indikator
- **Williamson Index & Theil T-Index** — ketimpangan regional
- **Global Moran's I** — autokorelasi spasial
- **LISA** — kluster lokal (HH/LL/LH/HL)
- **Spatial Error Model (SEM)** — regresi spasial
- **GWR** — regresi berbobot geografis
- **Tipologi Klassen** — klasifikasi 4 kuadran
- **Sigma-Konvergensi** — CV trend PDRB per kapita

---

## 📄 Lisensi

Penelitian ini dibuat untuk keperluan akademis (EJAVEC Bank Indonesia 2025).  
Data sumber mengikuti lisensi masing-masing penyedia (BP2MI, BPS, Meta, LinkedIn).
