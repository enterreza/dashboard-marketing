import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Program Kerja 2026", layout="wide")
st.title("📊 Live Dashboard Timeline Program Kerja")

# 2. Identitas Spreadsheet (Sudah diperbarui ke 'Master')
SHEET_ID = '17PUXVz1fWFAQlAnNt02BkFPuQFbiBI5uFAOEtZUMluU'
SHEET_NAME = 'Master' 

# Encode URL (Meskipun 'Master' tidak ada spasi, ini tetap praktik yang aman)
encoded_name = urllib.parse.quote(SHEET_NAME)
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_name}'

@st.cache_data(ttl=60)
def load_data():
    try:
        # Membaca data CSV dari Google Sheets
        df = pd.read_csv(url)
        
        # Bersihkan spasi di nama kolom
        df.columns = df.columns.str.strip()

        # Mengisi sel kosong jika ada 'Merged Cells' pada kolom utama
        if 'Bagian' in df.columns:
            df['Bagian'] = df['Bagian'].ffill()
        if 'Program Kerja' in df.columns:
            df['Program Kerja'] = df['Program Kerja'].ffill()

        # Konversi kolom Mulai & Selesai ke format Tanggal
        # Menggunakan dayfirst=True karena format di gambar Anda adalah DD/MM/YYYY
        df['Mulai'] = pd.to_datetime(df['Mulai'], dayfirst=True, errors='coerce')
        df['Selesai'] = pd.to_datetime(df['Selesai'], dayfirst=True, errors='coerce')

        # Hapus baris yang tidak memiliki tanggal valid
        df = df.dropna(subset=['Mulai', 'Selesai'])
        
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari sheet '{SHEET_NAME}': {e}")
        return None

# 3. Jalankan Pengambilan Data
df = load_data()

if df is not None and not df.empty:
    # Sidebar Filter
    st.sidebar.header("Filter Dashboard")
    
    # Filter berdasarkan Bagian
    if 'Bagian' in df.columns:
        all_sections = df['Bagian'].unique()
        selected_sections = st.sidebar.multiselect("Pilih Bagian:", all_sections, default=all_sections)
        df_filtered = df[df['Bagian'].isin(selected_sections)]
    else:
        df_filtered = df

    # 4. Membuat Grafik Timeline (Gantt Chart)
    fig = px.timeline(
        df_filtered, 
        x_start="Mulai", 
        x_end="Selesai", 
        y="Program Kerja", 
        color="Bagian" if 'Bagian' in df.columns else None,
        hover_data=["Output / Deliverables"] if "Output / Deliverables" in df.columns else None,
        color_discrete_sequence=px.colors.qualitative.Prism,
        template="plotly_white"
    )

    # Mempercantik Tampilan Grafik
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Timeline 2026",
        yaxis_title="",
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(
            dtick="M1", 
            tickformat="%b %Y"
        )
    )

    # Menampilkan Grafik di Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # 5. Tampilkan Tabel Data Mentah
    with st.expander("Lihat Detail Tabel Data"):
        st.dataframe(df_filtered, use_container_width=True)

else:
    st.info("💡 Menunggu data... Pastikan di Google Sheets kolom 'Mulai' dan 'Selesai' sudah terisi dengan format tanggal yang benar (contoh: 01/01/2026).")
