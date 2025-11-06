import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import io
import os

# Konfigurasi halaman
st.set_page_config(page_title="Exchange Rate Dashboard", layout="wide")

st.title("💱 Real-Time Exchange Rate Dashboard")
st.write("Visualisasi nilai tukar mata uang menggunakan ExchangeRatesAPI.io")

# Ganti dengan API key kamu
API_KEY = "db6add528a6d6d7d48707b1420df8e1a"

# Pilihan base currency
base_currency = st.selectbox("Pilih Base Currency:", ["USD", "EUR", "IDR", "JPY", "GBP", "AUD"])

if st.button("Ambil Data"):
    with st.spinner("Mengambil data dari API..."):
        url = f"http://api.exchangeratesapi.io/v1/latest?access_key=db6add528a6d6d7d48707b1420df8e1a"
        response = requests.get(url)
        data = response.json()

    if "rates" in data:
        rates = data["rates"]
        df = pd.DataFrame(list(rates.items()), columns=["currency", "rate"])
        df["date"] = data["date"]
        df.loc[len(df)] = [data["base"], 1.0, data["date"]]  # tambahkan EUR = 1.0

        # Jika base_currency bukan EUR, lakukan konversi manual
        if base_currency != "EUR":
            if base_currency in df["currency"].values:
                base_rate = df.loc[df["currency"] == base_currency, "rate"].values[0]
                df["rate"] = df["rate"] / base_rate
                df["base"] = base_currency
            else:
                st.error(f"Base currency {base_currency} tidak tersedia di data.")
                st.stop()
        else:
            df["base"] = "EUR"

        st.success(f"Data berhasil diambil ({data['date']})")
        st.dataframe(df, use_container_width=True)

        # Pilih berapa mata uang yang mau ditampilkan
        top_df = df.sort_values("rate", ascending=False).head(10)

        # Visualisasi
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(top_df["currency"], top_df["rate"], color="steelblue")
        ax.set_title(f"Top 10 Exchange Rates terhadap {base_currency} ({data['date']})")
        ax.set_xlabel("Currency")
        ax.set_ylabel("Rate")
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Tombol unduh
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Data sebagai CSV",
            data=csv_data,
            file_name=f"exchange_rates_{date.today()}.csv",
            mime="text/csv"
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.download_button(
            label="Unduh Grafik sebagai PNG",
            data=buf.getvalue(),
            file_name="exchange_rate_chart.png",
            mime="image/png"
        )
    else:
        st.error("Gagal mengambil data. Periksa kembali API key.")