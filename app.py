import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Program Kerja 2026", layout="wide")

st.title("📊 Live Dashboard Timeline Program Kerja")
st.write("Data ditarik langsung dari Google Sheets")

# 1. Identitas Spreadsheet (Sudah diperbaiki)
SHEET_ID = '17PUXVz1fWFAQlAnNt02BkFPuQFbiBI5uFAOEtZUMluU'
SHEET_NAME = 'Master Marketing Card 6'

# 2. Mengubah spasi menjadi format URL yang benar (URL Encoding)
encoded_sheet_name = urllib.parse.quote(SHEET_NAME)
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}'

# Load Data
@st.cache_data(ttl=60) # Refresh data setiap 60 detik
def load_data():
    # Menambahkan error handling agar lebih informatif
    try:
        df = pd.read_csv(url)
        # Pastikan nama kolom di GSheet Anda sama dengan di bawah ini:
        df['Mulai'] = pd.to_datetime(df['Mulai'])
        df['Selesai'] = pd.to_datetime(df['Selesai'])
        return df
    except Exception as e:
        st.error(f"Gagal membaca data. Pastikan kolom 'Mulai' dan 'Selesai' di GSheet sudah berformat tanggal. Error: {e}")
        return None

df = load_data()

if df is not None:
    try:
        # Sidebar untuk Filter
        st.sidebar.header("Filter Dashboard")
        
        # Pastikan kolom 'Bagian' ada di GSheet Anda
        kolom_bagian = "Bagian" 
        if kolom_bagian in df.columns:
            bagian = st.sidebar.multiselect(
                "Pilih Bagian:", 
                options=df[kolom_bagian].unique(), 
                default=df[kolom_bagian].unique()
            )
            df_filtered = df[df[kolom_bagian].isin(bagian)]
        else:
            df_filtered = df

        # Membuat Gantt Chart
        fig = px.timeline(
            df_filtered, 
            x_start="Mulai", 
            x_end="Selesai", 
            y="Program Kerja", 
            color=kolom_bagian if kolom_bagian in df.columns else None,
            hover_data=["Output / Deliverables"],
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            xaxis_title="Timeline 2026",
            yaxis_title="",
            height=600,
            margin=dict(l=0, r=0, t=30, b=0)
        )

        # Menampilkan Grafik
        st.plotly_chart(fig, use_container_width=True)

        # Menampilkan Tabel Data
        with st.expander("Lihat Tabel Data Mentah"):
            st.dataframe(df_filtered, use_container_width=True)

    except Exception as e:
        st.warning(f"Terjadi kesalahan saat merender grafik: {e}")
