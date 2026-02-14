import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Goethe C1 AI Coach", page_icon="🇩🇪", layout="wide")

st.title("🇩🇪 Goethe C1 Speaking Generator (AI Version)")
st.markdown("Nhập chủ đề và AI sẽ tự soạn bài nói chuẩn C1 cho bạn.")

# --- CẤU HÌNH API KEY ---
# Tự động lấy từ Secrets hoặc hiện ô nhập
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    with st.sidebar:
        st.header("🔑 Cài đặt Key")
        api_key = st.text_input("Dán Gemini API Key vào đây:", type="password")
        st.info("Lấy Key tại: aistudio.google.com/app/apikey")

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Nhập chủ đề")
    topic = st.text_input("Thema:", placeholder="z.B. Künstliche Intelligenz, Klimawandel...")
    
    st.markdown("---")
    st.subheader("2. Chọn nội dung")
    check_vocab = st.checkbox("Từ vựng C1 & Paraphrasing", value=True)
    check_grammar = st.checkbox("Cấu trúc Ngữ pháp C1", value=True)
    check_structure = st.checkbox("Dàn bài (Gliederung)", value=True)
    check_full_script = st.checkbox("Bài nói hoàn chỉnh (Vortrag)", value=True)
    check_transkript = st.checkbox("Transkript (Văn nói tự nhiên)", value=True)

# --- XỬ LÝ AI ---
with col2:
    if st.button("🚀 Tạo bài ngay (Generieren)", type="primary"):
        if not api_key:
            st.error("⚠️ Vui lòng nhập API Key trước.")
        elif not topic:
            st.warning("⚠️ Vui lòng nhập chủ đề.")
        else:
            try:
                # Cấu hình AI
                genai.configure(api_key=api_key)
                
                # SỬ DỤNG MODEL 1.5 FLASH (Nhanh và ổn định)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Tạo Prompt (Câu lệnh cho AI)
                prompt = f"""
                Du bist ein strenger Prüfer für das Goethe-Zertifikat C1.
                Thema: '{topic}'.
                
                AUFGABE: Erstelle Lernmaterialien für einen Vortrag (3-4 Min).
                
                WICHTIGSTE REGEL (ARGUMENTATIONSTIEFE):
                Immer wenn du ein Argument nennst, musst du es ZWINGEND mit 1-2 Sätzen vertiefen (Erklärung, Folge oder Beispiel). Das ist der Schlüssel für C1.
                
                Bitte erstelle:
                """
                
                if check_vocab:
                    prompt += "\n1. WORTSCHATZ: 7-10 C1-Begriffe mit Synonymen."
                if check_grammar:
                    prompt += "\n2. GRAMMATIK: 3 passende C1-Strukturen mit Beispielen."
                if check_structure:
                    prompt += "\n3. GLIEDERUNG: Einleitung -> Pro/Contra -> Meinung -> Schluss."
                if check_full_script:
                    prompt += "\n4. VOLLSTÄNDIGER VORTRAG: Akademischer Stil. Achte auf die Vertiefung der Argumente!"
                if check_transkript:
                    prompt += "\n5. TRANSKRIPT: Formuliere Teil 4 um in natürliche gesprochene Sprache (mit Füllwörtern)."

                # Gửi lệnh đi
                with st.spinner("AI đang suy nghĩ và viết bài..."):
                    response = model.generate_content(prompt)
                    st.success("Hoàn tất!")
                    st.markdown(response.text)
            
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
                if "404" in str(e):
                    st.markdown("""
                    ### 🛑 CÁCH SỬA LỖI 404 (QUAN TRỌNG):
                    Lỗi này nghĩa là **API Key của bạn sai loại**.
                    1. Bạn đang dùng Key của **Google Cloud** (Vertex AI) -> Cái này KHÔNG chạy được code này.
                    2. Bạn CẦN Key của **Google AI Studio**.
                    
                    👉 **Hãy vào đây lấy Key mới:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
                    """)
