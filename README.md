Berikut adalah draf `README.md` yang komprehensif untuk menjelaskan keseluruhan proyek analisis data penyewaan sepeda Anda. File ini disusun berdasarkan informasi yang terdapat dalam notebook dan dashboard yang telah kita bahas.

---

# 🚲 Proyek Analisis Data: Bike Sharing Analysis

Proyek ini bertujuan untuk menganalisis tren penyewaan sepeda pada dataset **UCI Bike Sharing**. Melalui proses *Data Wrangling*, *Exploratory Data Analysis (EDA)*, hingga *Data Visualization*, proyek ini menggali wawasan mendalam mengenai perilaku pengguna, pengaruh cuaca, dan pola waktu penyewaan untuk memberikan rekomendasi strategi bisnis yang efektif.

## 👤 Informasi Penulis

* **Nama:** Steven Graciano Immanuel Cahyono
* **Email:** tugasstevengraciano@gmail.com
* **ID Dicoding:** Steven Graciano Immanuel Cahyono

## 🎯 Pertanyaan Bisnis

1. Bagaimana proporsi antara pengguna *casual* dan *registered* terhadap total transaksi, dan segmen mana yang mendominasi?
2. Bagaimana tingkat pertumbuhan penyewaan dari tahun 2011 ke 2012 serta pola fluktuasi bulanannya?
3. Musim mana yang memberikan kontribusi transaksi terbesar?
4. Bagaimana pola penyewaan berdasarkan jam dan hari untuk optimasi alokasi armada?
5. Sejauh mana pengaruh suhu dan kondisi cuaca terhadap volume penyewaan?
6. Bagaimana segmentasi kondisi cuaca menggunakan teknik *Clustering (K-Means)*?

## 🛠️ Teknologi yang Digunakan

* **Bahasa Pemrograman:** Python 3.9+
* **Library Analisis:** Pandas, Numpy, Scikit-learn
* **Library Visualisasi:** Matplotlib, Seaborn
* **Framework Dashboard:** Streamlit

## 📂 Struktur Direktori

```text
.
├── dashboard/
│   ├── dashboard.py       # File utama aplikasi Streamlit
│   └── main_data.csv      # Dataset yang telah dibersihkan (opsional)
├── dataset/
│   ├── day.csv            # Dataset harian original
│   └── hour.csv           # Dataset per jam original
├── notebook.ipynb         # Analisis data lengkap (Wrangling, EDA, Clustering)
├── requirements.txt       # Daftar library yang dibutuhkan
└── README.md              # Dokumentasi proyek
└── README.md              # Dokumentasi proyek

```

## 🚀 Cara Menjalankan

### 1. Persiapan Lingkungan (Environment)

Pastikan Anda memiliki Python terinstal. Sangat disarankan untuk menggunakan *virtual environment*.

```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan venv (Windows)
venv\Scripts\activate

# Mengaktifkan venv (Mac/Linux)
source venv/bin/activate

```

### 2. Instalasi Library

Instal semua dependensi yang diperlukan melalui `requirements.txt`:

```bash
pip install -r requirements.txt

```

### 3. Menjalankan Dashboard

Jalankan perintah berikut untuk membuka dashboard interaktif di browser Anda:

```bash
streamlit run dashboard/dashboard.py

```

## 💡 Insight Utama

* **Dominasi Pengguna:** Pengguna *Registered* memberikan kontribusi jauh lebih besar dibandingkan pengguna *Casual*, menunjukkan loyalitas pelanggan yang tinggi.
* **Tren Pertumbuhan:** Terjadi pertumbuhan transaksi yang signifikan dari tahun 2011 ke 2012 (YoY Growth positif).
* **Pola Waktu:** Puncak penyewaan terjadi pada jam berangkat kerja (pagi) dan pulang kerja (sore), serta cenderung stabil pada hari kerja dibandingkan akhir pekan.
* **Faktor Cuaca:** Suhu hangat berkorelasi positif dengan jumlah transaksi. Musim Gugur (*Fall*) dan Musim Panas (*Summer*) adalah periode tersibuk.
* **Segmentasi (Clustering):** Melalui algoritma K-Means, teridentifikasi bahwa cluster cuaca "Panas & Kering" adalah kondisi paling ideal yang menghasilkan volume penyewaan tertinggi.

---

*Dibuat sebagai bagian dari submission Dicoding - Analisis Data dengan Python.*