import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Marketing 2026", layout="wide")
st.title("📊 Live Dashboard Timeline Program Kerja")

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

        # Fill merged cells (ffill)
        if 'Bagian' in df.columns: df['Bagian'] = df['Bagian'].ffill()
        if 'Program Kerja' in df.columns: df['Program Kerja'] = df['Program Kerja'].ffill()

        # Konversi Tanggal (dayfirst=False agar 6/1 dibaca 1 Juni)
        df['Mulai'] = pd.to_datetime(df['Mulai'], dayfirst=False, errors='coerce')
        df['Selesai'] = pd.to_datetime(df['Selesai'], dayfirst=False, errors='coerce')
        df = df.dropna(subset=['Mulai', 'Selesai'])

        # Kolom pembantu filter
        df['Kuartal'] = df['Mulai'].dt.quarter.map({1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'})
        df['Bulan_Nama'] = df['Mulai'].dt.strftime('%B')
        
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # --- SIDEBAR FILTER ---
    st.sidebar.header("Opsi Tampilan & Filter")
    all_sections = df['Bagian'].unique()
    selected_sections = st.sidebar.multiselect("Pilih Bagian:", all_sections, default=all_sections)
    df_filtered = df[df['Bagian'].isin(selected_sections)]

    time_view = st.sidebar.radio("Lihat Berdasarkan:", ["Semua (Tahunan)", "Per Kuartal", "Per Bulan"])

    if time_view == "Per Kuartal":
        q_options = ['Q1', 'Q2', 'Q3', 'Q4']
        selected_q = st.sidebar.multiselect("Pilih Kuartal:", q_options, default=df_filtered['Kuartal'].unique())
        df_filtered = df_filtered[df_filtered['Kuartal'].isin(selected_q)]
    
    elif time_view == "Per Bulan":
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        available_months = [m for m in month_order if m in df_filtered['Bulan_Nama'].unique()]
        selected_m = st.sidebar.multiselect("Pilih Bulan:", available_months, default=available_months)
        df_filtered = df_filtered[df_filtered['Bulan_Nama'].isin(selected_m)]

    # --- GRAFIK ---
    if not df_filtered.empty:
        chart_height = max(450, len(df_filtered) * 40)

        fig = px.timeline(
            df_filtered, 
            x_start="Mulai", 
            x_end="Selesai", 
            y="Program Kerja", 
            color="Bagian",
            hover_data=["Output / Deliverables"],
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        # Konfigurasi Sumbu Y (Vertikal) & Grid Horizontal
        fig.update_yaxes(
            autorange="reversed", 
            tickfont=dict(size=11),
            showgrid=True, 
            gridcolor='rgba(230, 230, 230, 0.6)', # Abu-abu sangat muda
            gridwidth=1
        )
        
        # Konfigurasi Sumbu X (Horizontal) & Grid Vertikal
        if time_view == "Per Kuartal":
            tick_vals = ['2026-01-01', '2026-04-01', '2026-07-01', '2026-10-01', '2027-01-01']
            tick_text = ['Q1', 'Q2', 'Q3', 'Q4', '']
            
            fig.update_layout(
                xaxis=dict(
                    side='top',
                    tickmode='array',
                    tickvals=tick_vals,
                    ticktext=tick_text,
                    showgrid=True,
                    gridcolor='rgba(220, 220, 220, 0.8)', # Sedikit lebih tegas untuk pembagi kuartal
                    gridwidth=1.5
                )
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    side='top',
                    dtick="M1",
                    tickformat="%b %Y",
                    showgrid=True,
                    gridcolor='rgba(230, 230, 230, 0.6)',
                    gridwidth=1
                )
            )

        # Layout Final
        fig.update_layout(
            height=chart_height,
            margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            dragmode=False
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with st.expander("📄 Detail Tabel"):
            st.dataframe(df_filtered[['Program Kerja', 'Bagian', 'Mulai', 'Selesai']], use_container_width=True)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")
else:
    st.info("💡 Menghubungkan ke Google Sheets...")
