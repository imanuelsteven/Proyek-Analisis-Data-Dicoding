import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Rental Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── LOAD & CLEAN DATA ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/main_data.csv")
    except FileNotFoundError:
        try:
            df = pd.read_csv("main_data.csv")
        except FileNotFoundError:
            st.error("❌ File `main_data.csv` tidak ditemukan. Pastikan file ada di folder `dashboard/` atau direktori yang sama dengan `dashboard.py`.")
            st.stop()

    df_clean = df.copy()
    df_clean = df_clean.rename(columns={"instant": "id"})
    df_clean["dteday"] = pd.to_datetime(df_clean["dteday"])
    df_clean["season"] = df_clean["season"].map({1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"})
    df_clean["yr"] = df_clean["yr"].map({0: 2011, 1: 2012})
    df_clean["holiday"] = df_clean["holiday"].map({0: "Tidak Libur", 1: "Libur"})
    df_clean["weekday"] = df_clean["weekday"].map({
        0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 4: "Kamis", 5: "Jumat", 6: "Sabtu"
    })
    df_clean["weathersit"] = df_clean["weathersit"].map({
        1: "Cerah/Partly Cloudy",
        2: "Berkabut/Berawan",
        3: "Hujan/Salju Ringan",
        4: "Hujan Lebat/Badai"
    })
    df_clean["temp"] = (df_clean["temp"] * 41).round(2)
    df_clean["atemp"] = (df_clean["atemp"] * 50).round(2)
    df_clean["hum"] = (df_clean["hum"] * 100).round(2)
    df_clean["windspeed"] = (df_clean["windspeed"] * 67).round(2)
    return df_clean

df_clean = load_data()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
BAR_HIGHLIGHT = "#1f77b4"
BAR_DEFAULT   = "#b0b0b0"

def make_colors(n):
    return [BAR_HIGHLIGHT] + [BAR_DEFAULT] * (n - 1)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚲 Bike Rental")
    st.subheader("Dashboard Analisis")
    st.divider()

    page = st.radio(
        "Navigasi",
        ["📊 Overview", "📈 Tren Bulanan", "🌤️ Analisis Cuaca", "⏰ Waktu Penyewaan", "🔬 Clustering"],
    )

    st.divider()
    st.markdown("**Filter Tahun**")
    year_filter = st.multiselect("Pilih Tahun", options=[2011, 2012], default=[2011, 2012])

    if year_filter:
        df_filtered = df_clean[df_clean["yr"].isin(year_filter)]
    else:
        df_filtered = df_clean.copy()

    st.divider()
    st.caption("📁 Dataset: UCI Bike Sharing\n\nPeriode: 2011–2012")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("📊 Overview — Penyewaan Sepeda 2011–2012")
    st.markdown("Gambaran umum total transaksi, demografi penyewa, dan pertumbuhan tahunan.")
    st.divider()

    total = df_filtered["cnt"].sum()
    reg   = df_filtered["registered"].sum()
    cas   = df_filtered["casual"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transaksi", f"{total:,}")
    col2.metric("Registered", f"{reg:,}", f"{reg/total:.1%} dari total")
    col3.metric("Casual", f"{cas:,}", f"{cas/total:.1%} dari total")

    if len(year_filter) == 2:
        yr = df_clean.groupby("yr")["cnt"].sum()
        yoy = (yr[2012] - yr[2011]) / yr[2011]
        col4.metric("YoY Growth (2011→2012)", f"+{yoy:.1%}")
    else:
        col4.metric("YoY Growth", "—", "Pilih 2 tahun")

    st.markdown("")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🍩 Demografi Penyewa")
        fig, ax = plt.subplots(figsize=(7, 5))
        sizes  = [reg, cas]
        colors = ["#4472C4", "#b0b0b0"]
        labels = ["Registered", "Casual"]
        wedges, _, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            startangle=90, colors=colors, pctdistance=0.82,
            explode=(0.05, 0), textprops={"fontsize": 12, "fontweight": "bold"}
        )
        plt.setp(autotexts, size=12, color="white")
        ax.add_artist(plt.Circle((0, 0), 0.68, fc="white"))
        ax.text(0, 0, f"Total\n{total:,}", ha="center", va="center",
                fontsize=14, fontweight="bold", color="#333")
        ax.set_title("Persebaran Demografi Penyewa", fontsize=13, pad=10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.subheader("📅 Transaksi per Tahun")
        yr_data = df_filtered.groupby("yr")["cnt"].sum().sort_values(ascending=False).reset_index()
        yr_data.columns = ["Tahun", "Total"]
        yr_data["Tahun"] = yr_data["Tahun"].astype(str)

        fig, ax = plt.subplots(figsize=(7, 5))
        colors_yr = make_colors(len(yr_data))
        bars = ax.bar(yr_data["Tahun"], yr_data["Total"], color=colors_yr, width=0.5)
        for bar, val in zip(bars, yr_data["Total"]):
            ax.text(bar.get_x() + bar.get_width()/2, val,
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


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TREN BULANAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Tren Bulanan":
    st.title("📈 Tren Penyewaan Sepeda Bulanan")
    st.markdown("Perkembangan total transaksi per bulan selama periode 2011–2012.")
    st.divider()

    df_filtered = df_filtered.copy()
    df_filtered["month"] = df_filtered["dteday"].dt.to_period("M")
    monthly = (
        df_filtered.groupby("month")
        .agg(cnt=("cnt", "sum"))
        .reset_index()
    )
    monthly["month_dt"] = monthly["month"].dt.to_timestamp()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(monthly["month_dt"], monthly["cnt"], color="#1f77b4", linewidth=2.5, marker="o", markersize=5)

    if 2011 in year_filter and 2012 in year_filter:
        ax.axvline(pd.Timestamp("2012-01-01"), color="gray", linestyle="--", linewidth=1.2, alpha=0.7)
        ax.text(pd.Timestamp("2012-01-15"), monthly["cnt"].max() * 1.02, "2012 →",
                fontsize=9, color="gray")

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

    peak_month = monthly.loc[monthly["cnt"].idxmax()]
    low_month  = monthly.loc[monthly["cnt"].idxmin()]
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"🏆 **Peak Month:** {peak_month['month_dt'].strftime('%B %Y')} — {peak_month['cnt']:,} transaksi")
    with c2:
        st.info(f"📉 **Lowest Month:** {low_month['month_dt'].strftime('%B %Y')} — {low_month['cnt']:,} transaksi")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALISIS CUACA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌤️ Analisis Cuaca":
    st.title("🌤️ Analisis Cuaca")
    st.markdown("Pengaruh musim, kondisi cuaca, dan suhu terhadap volume penyewaan.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["🌸 Per Musim", "🌧️ Kondisi Cuaca", "🌡️ Suhu vs Transaksi"])

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
        colors_s = make_colors(len(season_data))
        ax.bar(season_data["season"], season_data["cnt"], color=colors_s)
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

    with tab2:
        weather_data = (
            df_filtered.groupby("weathersit")
            .agg(sumcount=("cnt", "sum"))
            .reset_index()
            .sort_values("sumcount", ascending=False)
            .reset_index(drop=True)
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        colors_w = make_colors(len(weather_data))
        sns.barplot(data=weather_data, x="weathersit", y="sumcount",
                    palette=colors_w, ax=ax)
        for idx, row in weather_data.iterrows():
            ax.text(idx, row["sumcount"] + weather_data["sumcount"].max()*0.01,
                    f"{row['sumcount']:,}", ha="center", va="bottom", fontsize=10, fontstyle="italic")
        ax.set_title("Total Penyewaan per Kondisi Cuaca", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Kondisi Cuaca", fontsize=12)
        ax.set_ylabel("Total Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, weather_data["sumcount"].max() * 1.15)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with tab3:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(data=df_filtered, x="temp", y="cnt",
                        hue="season", alpha=0.4, ax=ax)
        sns.regplot(data=df_filtered, x="temp", y="cnt",
                    scatter=False, color="black",
                    line_kws={"linewidth": 1.5, "linestyle": "--"}, ax=ax)
        ax.set_title("Hubungan Suhu vs Jumlah Transaksi per Musim", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Suhu (°C)", fontsize=12)
        ax.set_ylabel("Jumlah Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WAKTU PENYEWAAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⏰ Waktu Penyewaan":
    st.title("⏰ Waktu Penyewaan")
    st.markdown("Analisis rata-rata penyewaan berdasarkan hari dan jam dalam sehari.")
    st.divider()

    tab1, tab2 = st.tabs(["📅 Per Hari", "🕐 Per Jam"])

    with tab1:
        weekday_data = (
            df_filtered.groupby("weekday")
            .agg(mean_cnt=("cnt", "mean"))
            .reset_index()
            .sort_values("mean_cnt", ascending=False)
            .reset_index(drop=True)
        )
        weekday_data["color"] = make_colors(len(weekday_data))

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=weekday_data, x="weekday", y="mean_cnt",
                    palette=weekday_data["color"].tolist(), ax=ax,
                    hue="weekday", dodge=False, legend=False)
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

    with tab2:
        hour_data = (
            df_filtered.groupby("hr")
            .agg(mean_cnt=("cnt", "mean"))
            .reset_index()
            .sort_values("mean_cnt", ascending=False)
            .reset_index(drop=True)
        )
        hour_data["hr_label"] = hour_data["hr"].astype(str)
        hour_data["color"] = make_colors(len(hour_data))

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.barplot(data=hour_data, x="hr_label", y="mean_cnt",
                    palette=hour_data["color"].tolist(), ax=ax)
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
        st.info(f"🏆 **Top 5 Peak Hours:** " +
                ", ".join([f"Jam {int(r['hr'])} ({r['mean_cnt']:,.0f})" for _, r in top5.iterrows()]))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CLUSTERING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔬 Clustering":
    st.title("🔬 Clustering Kondisi Cuaca")
    st.markdown("Segmentasi cuaca menggunakan K-Means berdasarkan suhu, kelembaban, dan kecepatan angin.")
    st.divider()

    features = ["temp", "hum", "windspeed"]
    X = df_clean[features].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    tab1, tab2 = st.tabs(["📐 Elbow Method", "🔵 Hasil Clustering"])

    with tab1:
        st.subheader("Menentukan Jumlah Cluster Optimal")
        inertia = []
        k_range = range(1, 10)
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertia.append(km.inertia_)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(list(k_range), inertia, marker="o", color="#1f77b4", linewidth=2.5)
        ax.axvline(4, color="red", linestyle="--", alpha=0.5, linewidth=1.2)
        ax.text(4.1, max(inertia)*0.9, "k=4 (optimal)", color="red", fontsize=10)
        ax.set_title("Elbow Method — Jumlah Cluster Optimal", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Jumlah Cluster (k)", fontsize=12)
        ax.set_ylabel("Inertia", fontsize=12)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with tab2:
        n_clusters = st.slider("Jumlah Cluster", min_value=2, max_value=8, value=4, step=1)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_clean = df_clean.copy()
        df_clean["cluster"] = kmeans.fit_predict(X_scaled)

        cluster_insight = (
            df_clean.groupby("cluster")
            .agg(temp=("temp", "mean"), hum=("hum", "mean"),
                 windspeed=("windspeed", "mean"), cnt=("cnt", "sum"))
            .reset_index()
        )
        cluster_insight.rename(columns={
            "temp": "Rata-rata Suhu (°C)",
            "hum": "Rata-rata Kelembaban (%)",
            "windspeed": "Rata-rata Kecepatan Angin (km/h)",
            "cnt": "Total Penyewaan"
        }, inplace=True)
        cluster_insight = cluster_insight.sort_values("Total Penyewaan", ascending=False).reset_index(drop=True)
        cluster_insight["Total Penyewaan"] = cluster_insight["Total Penyewaan"].apply(lambda x: f"{x:,}")

        st.subheader("Karakteristik per Cluster")
        st.dataframe(cluster_insight.round(2), use_container_width=True)

        st.subheader("Scatter Plot: Suhu vs Transaksi")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df_clean, x="temp", y="cnt",
                        hue="cluster", palette="Set2", alpha=0.4, ax=ax)
        ax.set_title("Clustering Kondisi Cuaca vs Jumlah Transaksi", fontsize=16, pad=15, fontweight="bold")
        ax.set_xlabel("Suhu (°C)", fontsize=12)
        ax.set_ylabel("Jumlah Transaksi", fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.legend(title="Cluster", fontsize=10)
        ax.grid(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.divider()
        st.info("""
💡 **Insight Clustering:**
- **Cluster terpanas & kering** → volume penyewaan tertinggi, ideal untuk ekspansi armada
- **Cluster kelembaban tinggi** → volume moderat, diskon dapat meningkatkan demand
- **Cluster dingin & berangin** → volume terendah, alihkan resource ke maintenance
        """)