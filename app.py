import streamlit as st
import pandas as pd
from datetime import datetime

# STYLING & TITLE
st.set_page_config(page_title="CBS Mini Lab Kampus", layout="wide")
st.title("🏦 Core Banking System (CBS) - Lab Perbankan Kampus")
st.caption("Berbasis SEOJK No. 34/SEOJK.03/2021 (BPAK)")

# DATABASE SEDERHANA (IN-MEMORY / SESSION STATE)
if 'saldo_kas' not in st.session_state:
    st.session_state.saldo_kas = 100000000 # Kas Awal Teller Rp 100 Juta
if 'rekening_nasabah' not in st.session_state:
    st.session_state.rekening_nasabah = {"123456": {"nama": "Budi Santoso", "saldo": 5000000}}
if 'jurnal_umum' not in st.session_state:
    st.session_state.jurnal_umum = []

# SIDEBAR NAVIGATION
menu = st.sidebar.selectbox("Pilih Menu Operasional", ["Dashboard / Ledger", "Teller (Setor Tunai)", "Customer Service"])

# MENU 1: TELLER (SETOR TUNAI & AUTO-JOURNAL)
if menu == "Teller (Setor Tunai)":
    st.header("🏧 Transaksi Teller - Setor Tunai")
    
    no_rek = st.text_input("Masukkan Nomor Rekening Nasabah", "123456")
    
    if no_rek in st.session_state.rekening_nasabah:
        nasabah = st.session_state.rekening_nasabah[no_rek]
        st.info(f"Nama Nasabah: **{nasabah['nama']}** | Saldo Saat Ini: **Rp {nasabah['saldo']:,}**")
        
        jumlah_setor = st.number_input("Jumlah Setoran (Rp)", min_value=10000, step=50000)
        
        if st.button("Proses Setoran"):
            # 1. Update Saldo Nasabah & Kas Teller
            st.session_state.rekening_nasabah[no_rek]['saldo'] += jumlah_setor
            st.session_state.saldo_kas += jumlah_setor
            
            # 2. MESIN JURNAL OTOMATIS (BPAK)
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Entry Debit: Kas Teller (101)
            st.session_state.jurnal_umum.append({"Waktu": waktu, "No Rek": no_rek, "Kode Akun": "101 - Kas Teller", "Debit": jumlah_setor, "Kredit": 0})
            # Entry Kredit: Tabungan Nasabah (201)
            st.session_state.jurnal_umum.append({"Waktu": waktu, "No Rek": no_rek, "Kode Akun": "201 - Tabungan Nasabah", "Debit": 0, "Kredit": jumlah_setor})
            
            st.success(f"Berhasil! Setoran Rp {jumlah_setor:,} telah masuk & Jurnal Otomatis terbentuk.")
    else:
        st.error("Nomor Rekening Tidak Ditemukan!")

# MENU 2: DASHBOARD & JURNAL (GENERAL LEDGER)
elif menu == "Dashboard / Ledger":
    st.header("📊 Laporan General Ledger & Kas Teller")
    
    col1, col2 = st.columns(2)
    col1.metric("Total Kas Teller (Akun 101)", f"Rp {st.session_state.saldo_kas:,}")
    col2.metric("Status Sistem", "ONLINE (Real-Time Batch)")
    
    st.subheader("📜 Buku Jurnal Otomatis (Sesuai BPAK)")
    if st.session_state.jurnal_umum:
        df_jurnal = pd.DataFrame(st.session_state.jurnal_umum)
        st.dataframe(df_jurnal, use_container_width=True)
    else:
        st.write("Belum ada transaksi hari ini.")

# MENU 3: CUSTOMER SERVICE (BUKA REKENING)
elif menu == "Customer Service":
    st.header("🧑‍💼 Customer Service - Buka Rekening Baru")

    nama = st.text_input("Nama Lengkap Nasabah")
    setoran_awal = st.number_input("Setoran Awal (Rp)", min_value=50000, step=50000)

    if st.button("Buka Rekening"):
        if nama.strip() == "":
            st.error("Nama tidak boleh kosong!")
        else:
            no_baru = str(123456 + len(st.session_state.rekening_nasabah))
            st.session_state.rekening_nasabah[no_baru] = {"nama": nama.strip(), "saldo": setoran_awal}
            st.session_state.saldo_kas += setoran_awal

            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.jurnal_umum.append({"Waktu": waktu, "No Rek": no_baru, "Kode Akun": "101 - Kas Teller", "Debit": setoran_awal, "Kredit": 0})
            st.session_state.jurnal_umum.append({"Waktu": waktu, "No Rek": no_baru, "Kode Akun": "201 - Tabungan Nasabah", "Debit": 0, "Kredit": setoran_awal})

            st.success(f"Rekening {no_baru} atas nama {nama.strip()} berhasil dibuka!")

    st.subheader("📋 Daftar Rekening Nasabah")
    data = [{"No Rek": k, "Nama": v["nama"], "Saldo": v["saldo"]} for k, v in st.session_state.rekening_nasabah.items()]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
