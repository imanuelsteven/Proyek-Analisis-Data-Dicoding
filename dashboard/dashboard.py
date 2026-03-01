import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Rental Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
BAR_HIGHLIGHT = "#1f77b4"
BAR_DEFAULT   = "#b0b0b0"


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def make_colors(n: int) -> list:
    return [BAR_HIGHLIGHT] + [BAR_DEFAULT] * (n - 1)


# ─── LOAD & CLEAN DATA ───────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv("dashboard/main_data.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("main_data.csv")
        except FileNotFoundError:
            st.error("❌ File `main_data.csv` tidak ditemukan. Pastikan file ada di folder `dashboard/` atau direktori yang sama dengan `dashboard.py`.")
            st.stop()

    df = df.rename(columns={"instant": "id"})
    df["dteday"]     = pd.to_datetime(df["dteday"])
    df["season"]     = df["season"].map({1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"})
    df["yr"]         = df["yr"].map({0: 2011, 1: 2012})
    df["holiday"]    = df["holiday"].map({0: "Tidak Libur", 1: "Libur"})
    df["weekday"]    = df["weekday"].map({
        0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu",
        4: "Kamis",  5: "Jumat", 6: "Sabtu"
    })
    df["weathersit"] = df["weathersit"].map({
        1: "Cerah/Partly Cloudy",
        2: "Berkabut/Berawan",
        3: "Hujan/Salju Ringan",
        4: "Hujan Lebat/Badai",
    })
    df["temp"]      = (df["temp"]      * 41).round(2)
    df["atemp"]     = (df["atemp"]     * 50).round(2)
    df["hum"]       = (df["hum"]       * 100).round(2)
    df["windspeed"] = (df["windspeed"] * 67).round(2)
    df["temp_category"] = df["temp"].apply(
        lambda x: "Dingin" if x < 15 else ("Sedang" if x <= 25 else "Hangat")
    )
    return df


df_clean = load_data()


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚲 Bike Rental")
    st.subheader("Dashboard Analisis")
    st.divider()

    page = st.radio(
        "Navigasi",
        ["📊 Overview", "📈 Tren Bulanan", "🌤️ Analisis Cuaca", "⏰ Waktu Penyewaan"],
    )

    st.divider()
    st.markdown("**Filter Tahun**")
    year_filter = st.multiselect("Pilih Tahun", options=[2011, 2012], default=[2011, 2012])
    st.divider()
    st.caption("📁 Dataset: UCI Bike Sharing\nPeriode: 2011–2012")

df_filtered = df_clean[df_clean["yr"].isin(year_filter)] if year_filter else df_clean.copy()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview():
    st.title("📊 Overview — Penyewaan Sepeda 2011–2012")
    st.markdown("Gambaran umum total transaksi, demografi penyewa, dan pertumbuhan tahunan.")
    st.divider()

    total = df_filtered["cnt"].sum()
    reg   = df_filtered["registered"].sum()
    cas   = df_filtered["casual"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transaksi", f"{total:,}")
    col2.metric("Registered",      f"{reg:,}",  f"{reg/total:.1%} dari total")
    col3.metric("Casual",          f"{cas:,}",  f"{cas/total:.1%} dari total")

    if len(year_filter) == 2:
        yr  = df_clean.groupby("yr")["cnt"].sum()
        yoy = (yr[2012] - yr[2011]) / yr[2011]
        col4.metric("YoY Growth (2011→2012)", f"+{yoy:.1%}")
    else:
        col4.metric("YoY Growth", "—", "Pilih 2 tahun")

    st.markdown("")
    col_left, col_right = st.columns(2)

    # ── Donut Chart ──
    with col_left:
        st.subheader("🍩 Demografi Penyewa")
        fig, ax = plt.subplots(figsize=(7, 5))
        wedges, _, autotexts = ax.pie(
            [reg, cas],
            labels=["Registered", "Casual"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#4472C4", BAR_DEFAULT],
            pctdistance=0.82,
            explode=(0.05, 0),
            textprops={"fontsize": 12, "fontweight": "bold"},
        )
        plt.setp(autotexts, size=12, color="white")
        ax.add_artist(plt.Circle((0, 0), 0.68, fc="white"))
        ax.text(0, 0, f"Total\n{total:,}", ha="center", va="center",
                fontsize=14, fontweight="bold", color="#333")
        ax.set_title("Persebaran Demografi Penyewa", fontsize=13, pad=10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Pengguna *registered* mendominasi ~81% total transaksi. "
                "Segmen *casual* (~19%) berpotensi dikonversi menjadi member terdaftar.")

    # ── Bar Chart per Tahun ──
    with col_right:
        st.subheader("📅 Transaksi per Tahun")
        yr_data = (
            df_filtered.groupby("yr")["cnt"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        yr_data.columns = ["Tahun", "Total"]
        yr_data["Tahun"] = yr_data["Tahun"].astype(str)

        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(yr_data["Tahun"], yr_data["Total"],
                      color=make_colors(len(yr_data)), width=0.5)
        for bar, val in zip(bars, yr_data["Total"]):
            ax.text(bar.get_x() + bar.get_width() / 2, val,
                    f"{val:,}", ha="center", va="bottom", fontsize=12, fontstyle="italic")
        ax.set_title("Total Transaksi per Tahun", fontsize=13, pad=10, fontweight="bold")
        ax.set_xlabel("Tahun", fontsize=11)
        ax.set_ylabel("Total Transaksi", fontsize=11)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, yr_data["Total"].max() * 1.2)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Terjadi pertumbuhan signifikan dari 2011 ke 2012 (~64% YoY), "
                "menunjukkan adopsi layanan yang terus meningkat.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TREN BULANAN
# ══════════════════════════════════════════════════════════════════════════════
def page_tren_bulanan():
    st.title("📈 Tren Penyewaan Sepeda Bulanan")
    st.markdown("Perkembangan total transaksi per bulan selama periode 2011–2012.")
    st.divider()

    df_m = df_filtered.copy()
    df_m["month"] = df_m["dteday"].dt.to_period("M")
    monthly = df_m.groupby("month").agg(cnt=("cnt", "sum")).reset_index()
    monthly["month_dt"] = monthly["month"].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly["month_dt"], monthly["cnt"],
            color=BAR_HIGHLIGHT, linewidth=2.5, marker="o", markersize=5)

    if 2011 in year_filter and 2012 in year_filter:
        ax.axvline(pd.Timestamp("2012-01-01"), color="gray", linestyle="--",
                   linewidth=1.2, alpha=0.7)
        ax.text(pd.Timestamp("2012-01-15"), monthly["cnt"].max() * 1.02,
                "2012 →", fontsize=9, color="gray")

    ax.set_title("Tren Penyewaan Sepeda Bulanan", fontsize=16, pad=15)
    ax.set_xlabel("Bulan", fontsize=12)
    ax.set_ylabel("Total Transaksi", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    peak = monthly.loc[monthly["cnt"].idxmax()]
    low  = monthly.loc[monthly["cnt"].idxmin()]
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"🏆 **Peak Month:** {peak['month_dt'].strftime('%B %Y')} — {peak['cnt']:,} transaksi")
    with c2:
        st.info(f"📉 **Lowest Month:** {low['month_dt'].strftime('%B %Y')} — {low['cnt']:,} transaksi")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALISIS CUACA
# ══════════════════════════════════════════════════════════════════════════════
def page_analisis_cuaca():
    st.title("🌤️ Analisis Cuaca")
    st.markdown("Pengaruh musim, kondisi cuaca, dan suhu terhadap volume penyewaan.")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌸 Per Musim", "🌧️ Kondisi Cuaca", "🌡️ Suhu vs Transaksi", "🌡️ Kategori Suhu"
    ])

    # ── Tab 1: Per Musim ──
    with tab1:
        season_data = (
            df_filtered.groupby("season")
            .agg(cnt=("cnt", "sum"), temp=("temp", "mean"))
            .reset_index()
            .sort_values("cnt", ascending=False)
            .reset_index(drop=True)
        )
        total_s = season_data["cnt"].sum()

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(season_data["season"], season_data["cnt"], color=make_colors(len(season_data)))
        for idx, row in season_data.iterrows():
            label = f"{row['cnt']:,} ({row['cnt']/total_s:.1%})\nMean Suhu: {row['temp']:.1f}°C"
            ax.text(idx, row["cnt"], label, ha="center", va="bottom",
                    fontsize=10, fontstyle="italic", linespacing=1.6)
        ax.set_title("Total Transaksi Penyewaan per Musim", fontsize=16, pad=12, fontweight="bold")
        ax.set_xlabel("Musim", fontsize=12)
        ax.set_ylabel("Total Transaksi", fontsize=12)
        ax.set_ylim(0, season_data["cnt"].max() * 1.22)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Musim Gugur berkontribusi terbesar, diikuti Panas. "
                "Musim Semi mencatat transaksi terendah — peluang untuk promosi *low season*.")

    # ── Tab 2: Kondisi Cuaca ──
    with tab2:
        weather_data = (
            df_filtered.groupby("weathersit")
            .agg(sumcount=("cnt", "sum"))
            .reset_index()
            .sort_values("sumcount", ascending=False)
            .reset_index(drop=True)
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(weather_data["weathersit"], weather_data["sumcount"],
               color=make_colors(len(weather_data)))
        for idx, row in weather_data.iterrows():
            ax.text(idx, row["sumcount"] + weather_data["sumcount"].max() * 0.01,
                    f"{row['sumcount']:,}", ha="center", va="bottom",
                    fontsize=10, fontstyle="italic")
        ax.set_title("Total Penyewaan per Kondisi Cuaca", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Kondisi Cuaca", fontsize=12)
        ax.set_ylabel("Total Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, weather_data["sumcount"].max() * 1.15)
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Kondisi cerah mendominasi transaksi (~67%). "
                "Cuaca hujan dan badai menekan penyewaan secara drastis — "
                "distribusi armada dapat disesuaikan secara *real-time*.")

    # ── Tab 3: Scatter Suhu ──
    with tab3:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(data=df_filtered, x="temp", y="cnt",
                        hue="season", alpha=0.4, ax=ax)
        sns.regplot(data=df_filtered, x="temp", y="cnt",
                    scatter=False, color="black",
                    line_kws={"linewidth": 1.5, "linestyle": "--"}, ax=ax)
        ax.set_title("Hubungan Suhu vs Jumlah Transaksi per Musim",
                     fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Suhu (°C)", fontsize=12)
        ax.set_ylabel("Jumlah Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Tren positif antara suhu dan jumlah transaksi. "
                "Rentang suhu 20–35°C adalah zona penyewaan paling optimal.")

    # ── Tab 4: Kategori Suhu ──
    with tab4:
        temp_cluster = (
            df_filtered.groupby("temp_category")["cnt"]
            .sum()
            .sort_values(ascending=False)
        )
        colors_tc = [BAR_HIGHLIGHT] + ["#d3d3d3"] * (len(temp_cluster) - 1)

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(temp_cluster.index, temp_cluster.values, color=colors_tc)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h,
                    f"{int(h):,}", ha="center", va="bottom", fontsize=11)
        ax.set_title("Transaksi Penyewaan berdasarkan Kategori Suhu",
                     fontsize=16, pad=12, fontweight="bold")
        ax.set_xlabel("Kategori Suhu", fontsize=12)
        ax.set_ylabel("Total Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Kategori **Hangat** (>25°C) menghasilkan hampir 3× lebih banyak "
                "transaksi dibanding **Dingin** (<15°C). Suhu adalah variabel penentu permintaan.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WAKTU PENYEWAAN
# ══════════════════════════════════════════════════════════════════════════════
def page_waktu_penyewaan():
    st.title("⏰ Waktu Penyewaan")
    st.markdown("Analisis rata-rata penyewaan berdasarkan hari dan jam dalam sehari.")
    st.divider()

    tab1, tab2 = st.tabs(["📅 Per Hari", "🕐 Per Jam"])

    # ── Tab 1: Per Hari ──
    with tab1:
        weekday_data = (
            df_filtered.groupby("weekday")
            .agg(mean_cnt=("cnt", "mean"))
            .reset_index()
            .sort_values("mean_cnt", ascending=False)
            .reset_index(drop=True)
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(weekday_data["weekday"], weekday_data["mean_cnt"],
               color=make_colors(len(weekday_data)))
        for idx, row in weekday_data.iterrows():
            ax.text(idx, row["mean_cnt"], f"{row['mean_cnt']:,.0f}",
                    ha="center", va="bottom", fontsize=10, fontstyle="italic")
        ax.set_title("Rata-rata Penyewaan Sepeda per Hari", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Hari", fontsize=12)
        ax.set_ylabel("Rata-rata Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, weekday_data["mean_cnt"].max() * 1.15)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        st.info("**Insight:** Kamis dan Jumat mencatat rata-rata tertinggi, menunjukkan "
                "dominasi penggunaan untuk *commuting* di hari kerja.")

    # ── Tab 2: Per Jam ──
    with tab2:
        hour_data = (
            df_filtered.groupby("hr")
            .agg(mean_cnt=("cnt", "mean"))
            .reset_index()
            .sort_values("mean_cnt", ascending=False)
            .reset_index(drop=True)
        )
        hour_data["hr_label"] = hour_data["hr"].astype(str)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.bar(hour_data["hr_label"], hour_data["mean_cnt"],
               color=make_colors(len(hour_data)))
        for idx, row in hour_data.iterrows():
            ax.text(idx, row["mean_cnt"] + 2, f"{row['mean_cnt']:,.0f}",
                    ha="center", va="bottom", fontsize=8, fontstyle="italic")
        ax.set_title("Rata-rata Penyewaan Sepeda per Jam", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Jam", fontsize=12)
        ax.set_ylabel("Rata-rata Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, hour_data["mean_cnt"].max() * 1.15)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        top5 = hour_data.nlargest(5, "mean_cnt")
        st.success(
            "🏆 **Top 5 Peak Hours:** " +
            ", ".join([f"Jam {int(r['hr'])} ({r['mean_cnt']:,.0f})" for _, r in top5.iterrows()])
        )
        st.info("**Insight:** Dua jam puncak terjadi pukul **08.00** (berangkat kerja) "
                "dan **17.00–18.00** (pulang kerja), menegaskan fungsi utama sebagai moda *commuting*.")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    page_overview()
elif page == "📈 Tren Bulanan":
    page_tren_bulanan()
elif page == "🌤️ Analisis Cuaca":
    page_analisis_cuaca()
elif page == "⏰ Waktu Penyewaan":
    page_waktu_penyewaan()