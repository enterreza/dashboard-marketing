import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Dashboard Program Kerja 2026", layout="wide")
st.title("📊 Live Dashboard Timeline Program Kerja")

# 2. Pengaturan Google Sheets
# ID diambil dari link yang Anda berikan
SHEET_ID = '17PUXVz1fWFAQlAnNt02BkFPuQFbiBI5uFAOEtZUMluU'
SHEET_NAME = 'Master'



# 3. Fungsi Load Data
@st.cache_data(ttl=60)
def load_and_fix_data():
    try:
        # Membaca CSV dari Google Sheets
        df = pd.read_csv(url)
        
        # Kamus untuk mengubah nama bulan Indonesia ke angka (agar bisa dibaca timeline)
        month_map = {
            'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04',
            'Mei': '05', 'Juni': '06', 'Juli': '07', 'Agustus': '08',
            'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'
        }

        # Membersihkan data (Pastikan nama kolom di Sheet sama persis)
        # Kami asumsikan kolom di Sheet Anda bernama: "Program Kerja", "Bagian", "Mulai", "Selesai"
        if 'Mulai' in df.columns and 'Selesai' in df.columns:
            df['start_date'] = df['Mulai'].map(month_map).apply(lambda x: f'2026-{x}-01')
            df['end_date'] = df['Selesai'].map(month_map).apply(lambda x: f'2026-{x}-28') # Akhir bulan estimasi
            
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            return df
        else:
            st.error("Kolom 'Mulai' atau 'Selesai' tidak ditemukan di Google Sheets.")
            return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# 4. Menampilkan Dashboard
data = load_and_fix_data()

if data is not None:
    # Sidebar Filter
    st.sidebar.header("Filter")
    if 'Bagian' in data.columns:
        selected_dept = st.sidebar.multiselect("Pilih Bagian:", data['Bagian'].unique(), default=data['Bagian'].unique())
        data = data[data['Bagian'].isin(selected_dept)]

    # Membuat Grafik Timeline
    fig = px.timeline(
        data, 
        x_start="start_date", 
        x_end="end_date", 
        y="Program Kerja", 
        color="Bagian" if "Bagian" in data.columns else None,
        hover_data=["Output / Deliverables"] if "Output / Deliverables" in data.columns else None,
        title="Timeline Program Kerja 2026"
    )

    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_title="Bulan", yaxis_title="")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan Tabel
    with st.expander("Lihat Data Detail"):
        st.write(data)


