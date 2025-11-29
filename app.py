import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import firestore
import datetime
import json
import os
from dotenv import load_dotenv

# ==========================================
# 1. CONFIGURATION & ENVIRONMENT SETUP
# ==========================================

# Load environment variables dari file .env (Untuk Local Testing)
load_dotenv()

# Ambil konfigurasi dari Environment Variables
# Ini memungkinkan kita ganti Project ID/DB Name tanpa ubah kodingan
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_REGION", "us-central1")
DB_NAME = os.getenv("GCP_DB_NAME", "(default)") # Default jika tidak diset

# Setup Halaman Streamlit (Wajib ditaruh paling atas)
st.set_page_config(
    page_title="NGSR: Next-Gen Smart Refrigerator",
    page_icon="❄️",
    layout="wide"
)

# Safety Check: Pastikan Project ID ada
if not PROJECT_ID:
    st.error("❌ ERROR CRITICAL: Environment Variable 'GCP_PROJECT_ID' belum diset!")
    st.info("Tips: Jika di local, cek file .env. Jika di Cloud Run, cek konfigurasi --set-env-vars.")
    st.stop()

# ==========================================
# 2. INITIALIZE GCP SERVICES (Gemini & Firestore)
# ==========================================
db = None
model = None

try:
    # A. Init Vertex AI (Gemini)
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel("gemini-2.5-flash-lite") # Menggunakan model Flash (Cepat & Efisien)
    
    # B. Init Firestore dengan Database Name spesifik
    # Jika DB_NAME='fs-ngsr', dia akan konek ke sana.
    db = firestore.Client(project=PROJECT_ID, database=DB_NAME)
    
    # Indikator Sukses (Toast kecil di pojok kanan)
    st.toast(f"Connected to DB: {DB_NAME}", icon="🗄️")

except Exception as e:
    st.error(f"⚠️ Gagal Terkoneksi ke Google Cloud: {e}")
    st.caption("Pastikan API Vertex AI & Firestore sudah enable di console.")

# ==========================================
# 3. USER INTERFACE (Frontend)
# ==========================================

# Header Aplikasi
st.title("❄️ NGSR: Next-Gen Smart Refrigerator")
st.markdown(f"**Engine:** gemini-2.5-flash-lite | **Database:** `{DB_NAME}`")
st.divider()

# --- SIDEBAR: PROFIL KESEHATAN USER ---
with st.sidebar:
    st.header("👤 User Health Profile")
    st.caption("Profil ini menjadi 'Rules' bagi Gemini untuk menyaring resep.")
    
    user_id = st.text_input("User ID", "user_hackathon_01")
    
    # Input Kondisi Kesehatan
    health_conditions = st.multiselect(
        "Kondisi Kesehatan / Diet",
        [
            "Asam Urat (Gout)", 
            "Kolesterol Tinggi", 
            "Diabetes Tipe 2", 
            "Hipertensi", 
            "Alergi Kacang", 
            "Alergi Seafood", 
            "Alergi Telur",
            "Diet Keto", 
            "Vegetarian",
            "Normal"
        ],
        default=["Asam Urat (Gout)"]
    )
    
    # Tombol Simpan Profil ke Firestore
    if st.button("💾 Simpan Profil", use_container_width=True):
        if db:
            try:
                doc_ref = db.collection("users").document(user_id)
                doc_ref.set({
                    "conditions": health_conditions,
                    "last_updated": datetime.datetime.now()
                })
                st.success(f"Profil {user_id} berhasil disimpan!")
            except Exception as e:
                st.error(f"Error Database: {e}")
        else:
            st.error("Database belum siap.")

# --- MAIN AREA: IMAGE ANALYSIS ---

col_upload, col_preview = st.columns([1, 2])

with col_upload:
    st.subheader("📸 Scan Isi Kulkas")
    st.caption("Upload foto bahan makanan di dalam kulkas.")
    uploaded_file = st.file_uploader("Pilih Gambar...", type=["jpg", "png", "jpeg"])

# Logika Utama berjalan jika ada file upload
if uploaded_file is not None:
    with col_preview:
        st.image(uploaded_file, caption="Preview Visual Kulkas", width=400)
    
    st.divider()
    
    # Tombol Eksekusi AI
    if st.button("🚀 Analyze with NGSR Brain", type="primary"):
        
        if not model:
            st.error("Model AI belum terinisialisasi. Cek koneksi internet/GCP.")
            st.stop()

        # UI Loading State
        with st.spinner('🤖 Gemini sedang berpikir: Menganalisa visual, mengecek kesegaran, dan mencari resep sehat...'):
            try:
                # 1. Persiapkan Image untuk Gemini
                image_bytes = uploaded_file.getvalue()
                image_part = Part.from_data(data=image_bytes, mime_type=uploaded_file.type)
                
                # 2. PROMPT ENGINEERING (The "Brain" Logic)
                # Kita minta Gemini bertindak sebagai ADK yang outputnya JSON murni.
                prompt = f"""
                Peran: Anda adalah NGSR (Next-Gen Smart Refrigerator).
                
                KONTEKS PENGGUNA:
                - ID: {user_id}
                - Profil Kesehatan/Pantangan: {', '.join(health_conditions)}
                
                TUGAS MULTIMODAL:
                1. DETEKSI VISUAL: List semua bahan makanan yang terlihat di foto.
                2. FRESHNESS CHECK: Estimasi mana yang 'Fresh' dan mana yang 'Expiring' (layu/busuk).
                3. HEALTH-COMPLIANT RECIPE: Buat 1 resep yang AMAN untuk profil kesehatan di atas.
                   (Contoh: Jika Asam Urat, hindari jeroan/kacang/bayam berlebih).
                4. CALCULATE: Estimasi total kalori resep.
                5. REASONING: Jelaskan kenapa resep ini dipilih berdasarkan profil kesehatan user.
                
                OUTPUT FORMAT (WAJIB JSON MURNI):
                {{
                    "inventory": [
                        {{"item": "Nama Bahan", "status": "Fresh/Expiring", "qty": "Estimasi"}}
                    ],
                    "recipe": {{
                        "name": "Nama Resep Kreatif",
                        "difficulty": "Easy/Medium/Hard",
                        "calories": 000,
                        "steps_short": "Ringkasan cara masak (1 kalimat)"
                    }},
                    "health_reasoning": "Penjelasan medis kenapa resep ini aman untuk {', '.join(health_conditions)}",
                    "expiry_alert": "Yes/No (Isi Yes jika ada bahan status Expiring)"
                }}
                """
                
                # 3. Generate Content
                response = model.generate_content([image_part, prompt])
                
                # 4. Parsing JSON (Cleaning Markdown)
                json_str = response.text.replace("```json", "").replace("```", "").strip()
                result = json.loads(json_str)
                
                # ==========================================
                # 4. DISPLAY RESULT (Visualisasi Data)
                # ==========================================
                
                # Layout Kolom Hasil
                res_col1, res_col2 = st.columns(2)
                
                # Kiri: Inventory Status
                with res_col1:
                    st.info("📋 **Inventory Kulkas**")
                    inv_list = result.get('inventory', [])
                    if inv_list:
                        for item in inv_list:
                            # Icon status
                            icon = "🟢" if item['status'] == 'Fresh' else "🔴"
                            st.write(f"{icon} **{item['item']}** ({item['qty']}) — *{item['status']}*")
                    else:
                        st.warning("Tidak ada bahan makanan terdeteksi.")

                    # Logic Alert System
                    if result.get("expiry_alert") == "Yes":
                        st.error("🚨 **EXPIRY ALERT:** Sistem mendeteksi bahan hampir busuk! Webhook dikirim.")
                        # [TODO for Hackathon]: Tambahkan code requests.post(WEBHOOK_URL) disini
                
                # Kanan: Rekomendasi Resep
                with res_col2:
                    recipe = result.get('recipe', {})
                    st.success(f"🍲 **Saran Masak: {recipe.get('name')}**")
                    st.metric("Estimasi Kalori", f"{recipe.get('calories')} kkal")
                    st.write(f"**Tingkat:** {recipe.get('difficulty')}")
                    st.caption(f"📝 {recipe.get('steps_short')}")
                
                # Bawah: Reasoning (Nilai Jual Utama/Analytical)
                st.warning(f"🩺 **NGSR Health Logic:**\n\n{result.get('health_reasoning')}")
                
                # 5. Simpan History ke Firestore
                if db:
                    db.collection("history").add({
                        "user_id": user_id,
                        "input_conditions": health_conditions,
                        "ai_analysis": result,
                        "timestamp": datetime.datetime.now()
                    })
                    st.toast("Analisis tersimpan di database history.", icon="💾")

            except json.JSONDecodeError:
                st.error("Gagal memproses respon JSON dari Gemini.")
                with st.expander("Debug Raw Response"):
                    st.text(response.text)
            except Exception as e:
                st.error(f"Terjadi kesalahan sistem: {e}")