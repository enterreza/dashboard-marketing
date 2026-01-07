import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime

# 1. Konfigurasi Halaman & CSS Khusus Mobile
st.set_page_config(page_title="Dashboard Marketing 2026", layout="wide")

# Mengurangi padding atas agar layar HP yang sempit bisa langsung menampilkan konten
st.markdown("""
    <style>
    .main .block-container {padding-top: 1.5rem; padding-bottom: 1rem; padding-left: 1rem; padding-right: 1rem;}
    h1 {font-size: 1.8rem !important; margin-bottom: 0.5rem !important;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Timeline Program Kerja 2026")

# 2. Identitas Spreadsheet
SHEET_ID = '17PUXVz1fWFAQlAnNt02BkFPuQFbiBI5uFAOEtZUMluU'
SHEET_NAME = 'Master' 
encoded_name = urllib.parse.quote(SHEET_NAME)
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_name}'

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if 'Bagian' in df.columns: df['Bagian'] = df['Bagian'].ffill()
        if 'Program Kerja' in df.columns: df['Program Kerja'] = df['Program Kerja'].ffill()
        df['Mulai'] = pd.to_datetime(df['Mulai'], dayfirst=False, errors='coerce')
        df['Selesai'] = pd.to_datetime(df['Selesai'], dayfirst=False, errors='coerce')
        df = df.dropna(subset=['Mulai', 'Selesai']).sort_values(by=['Bagian', 'Mulai'])
        df['Kuartal'] = df['Mulai'].dt.quarter.map({1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})
        df['Bulan_Nama'] = df['Mulai'].dt.strftime('%B')
        return df
    except:
        return None

df = load_data()

if df is not None and not df.empty:
    # --- SIDEBAR FILTER ---
    st.sidebar.header("Filter")
    all_sections = df['Bagian'].unique()
    selected_sections = st.sidebar.multiselect("Pilih Bagian:", all_sections, default=all_sections)
    df_filtered = df[df['Bagian'].isin(selected_sections)]

    time_view = st.sidebar.radio("Opsi Tampilan:", ["Semua", "Per Kuartal", "Per Bulan"])

    if time_view == "Per Kuartal":
        q_options = ['Q1', 'Q2', 'Q3', 'Q4']
        selected_q = st.sidebar.multiselect("Kuartal:", q_options, default=df_filtered['Kuartal'].unique())
        df_filtered = df_filtered[df_filtered['Kuartal'].isin(selected_q)]
    elif time_view == "Per Bulan":
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        available_months = [m for m in month_order if m in df_filtered['Bulan_Nama'].unique()]
        selected_m = st.sidebar.multiselect("Bulan:", available_months, default=available_months)
        df_filtered = df_filtered[df_filtered['Bulan_Nama'].isin(selected_m)]

    if not df_filtered.empty:
        # OPTIMASI MOBILE: Tinggi dinamis per baris agar tidak bertumpuk
        # Menggunakan 50px per baris agar teks label di sebelah kiri tetap terbaca
        chart_height = max(400, len(df_filtered) * 55)

        fig = px.timeline(
            df_filtered, 
            x_start="Mulai", x_end="Selesai", y="Program Kerja", 
            color="Bagian", text="Bagian",
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        # Rounded Corners & Font Label Mobile
        fig.update_traces(
            textposition='inside',
            insidetextanchor='middle',
            marker_cornerradius=15,
            textfont=dict(size=9, color="white") # Font sedikit diperkecil untuk bar HP
        )

        # Indikator Hari Ini (Timestamp fix)
        today_ts = datetime.now().timestamp() * 1000
        fig.add_vline(x=today_ts, line_dash="dash", line_color="#FF4B4B", line_width=2,
                      annotation_text="Hari Ini", annotation_position="top", layer="above")

        # Sumbu Y (Label Program Kerja)
        fig.update_yaxes(
            autorange="reversed", 
            tickfont=dict(size=10), # Font label kiri diperkecil agar tidak memotong layar HP
            showgrid=True, gridcolor='rgba(240, 240, 240, 0.5)', layer="below traces"
        )
        
        # Garis Pemisah Antar Bagian
        current_sections = df_filtered['Bagian'].tolist()
        for i in range(len(current_sections) - 1):
            if current_sections[i] != current_sections[i+1]:
                fig.add_hline(y=i + 0.5, line_dash="solid", line_color="rgba(150, 150, 150, 0.4)", line_width=1.5, layer="below")

        # Sumbu X (Top Axis)
        xaxis_config = dict(side='top', showgrid=True, gridcolor='rgba(230, 230, 230, 0.6)', layer="below traces", tickfont=dict(size=10))
        if time_view == "Per Kuartal":
            tick_vals = ['2026-01-01', '2026-04-01', '2026-07-01', '2026-10-01', '2027-01-01']
            tick_text = ['Q1', 'Q2', 'Q3', 'Q4', '']
            xaxis_config.update(dict(tickmode='array', tickvals=tick_vals, ticktext=tick_text))
        else:
            xaxis_config.update(dict(dtick="M1", tickformat="%b")) # Format bulan singkat (Jan, Feb) agar muat di HP
            
        fig.update_layout(xaxis=xaxis_config)

        # OPTIMASI LAYOUT MOBILE FINAL
        fig.update_layout(
            height=chart_height,
            margin=dict(l=5, r=5, t=70, b=10), # Margin sangat tipis untuk memaksimalkan lebar HP
            showlegend=True,
            legend=dict(
                orientation="h",       # Legend diletakkan secara horizontal
                yanchor="bottom",
                y=-0.05,               # Di bawah grafik
                xanchor="center",
                x=0.5,
                font=dict(size=9)      # Font legend kecil
            ),
            dragmode=False # PENTING: Mematikan drag agar user HP bisa scroll halaman dengan lancar
        )

        # Tampilkan Grafik tanpa Toolbar Plotly yang berat di HP
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        
        with st.expander("📄 Data Detail"):
            st.dataframe(df_filtered[['Program Kerja', 'Bagian', 'Mulai', 'Selesai']], use_container_width=True)
    else:
        st.warning("Pilih bagian untuk melihat timeline.")
else:
    st.info("💡 Memuat data...")
