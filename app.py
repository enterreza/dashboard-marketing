import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Program Kerja 2026", layout="wide")

st.title("📊 Live Dashboard Timeline Program Kerja")
st.write("Data ditarik langsung dari Google Sheets")

# 1. Masukkan ID Spreadsheet Anda di sini
SHEET_ID = '17PUXVz1fWFAQlAnNt02BkFPuQFbiBI5uFAOEtZUMluU'
SHEET_NAME = 'Master_Marketing_Card_6'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

# Load Data
@st.cache_data(ttl=600) # Data di-refresh setiap 10 menit
def load_data():
    df = pd.read_csv(url)
    df['Mulai'] = pd.to_datetime(df['Mulai'])
    df['Selesai'] = pd.to_datetime(df['Selesai'])
    return df

try:
    df = load_data()

    # Sidebar untuk Filter
    st.sidebar.header("Filter Data")
    bagian = st.sidebar.multiselect("Pilih Bagian:", options=df["Bagian"].unique(), default=df["Bagian"].unique())
    
    df_filtered = df[df["Bagian"].isin(bagian)]

    # Membuat Gantt Chart
    fig = px.timeline(
        df_filtered, 
        x_start="Mulai", 
        x_end="Selesai", 
        y="Program Kerja", 
        color="Bagian",
        hover_data=["Output / Deliverables"],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Timeline Bulan",
        yaxis_title="",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Menampilkan Grafik
    st.plotly_chart(fig, use_container_width=True)

    # Menampilkan Tabel Data di bawahnya
    with st.expander("Lihat Detail Tabel"):
        st.write(df_filtered)

except Exception as e:

    st.error(f"Gagal memuat data. Pastikan Link Google Sheets sudah benar dan diatur 'Anyone with the link'. Error: {e}")
