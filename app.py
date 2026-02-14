import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Goethe C1 Library", page_icon="📚", layout="wide")

# --- 2. CÁC HÀM XỬ LÝ FILE ---
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return None

# Lưu ý: Trên GitHub/Streamlit Cloud, ta không lưu file vĩnh viễn được 
# nên dùng Session State để lưu tạm trong phiên làm việc này
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = {}

def save_to_session(filename, text):
    clean_name = filename.rsplit('.', 1)[0]
    st.session_state.knowledge_base[clean_name] = text
    return clean_name

# --- 3. XỬ LÝ API KEY ---
# Tự động lấy Key từ Secrets (nếu đã cài) hoặc hiện ô nhập
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

if not api_key:
    with st.sidebar:
        st.header("🔑 Cài đặt")
        api_key = st.text_input("Nhập Gemini API Key", type="password")
        st.caption("Lấy Key tại: aistudio.google.com/app/apikey")
        if not api_key:
            st.warning("⚠️ Hãy nhập Key để bắt đầu!")

# --- 4. GIAO DIỆN CHÍNH ---
st.title("📚 Goethe C1 Coach (Cloud Version)")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# === CỘT TRÁI: DỮ LIỆU ===
with col1:
    st.subheader("📂 Tài liệu")
    
    # Upload file mới
    uploaded_file = st.file_uploader("Upload PDF:", type=["pdf"])
    if uploaded_file:
        with st.spinner("Đang đọc file..."):
            if uploaded_file.name not in st.session_state.knowledge_base:
                raw_text = extract_text_from_pdf(uploaded_file)
                if raw_text:
                    save_to_session(uploaded_file.name, raw_text)
                    st.success(f"Đã tải: {uploaded_file.name}")
    
    # Chọn sách đã tải
    saved_books = list(st.session_state.knowledge_base.keys())
    current_text = ""
    current_book_name = ""
    
    if saved_books:
        selected_book = st.selectbox("Chọn sách đang dùng:", saved_books)
        current_text = st.session_state.knowledge_base[selected_book]
        current_book_name = selected_book
        st.info(f"Đang dùng: {current_book_name}")
    else:
        st.warning("Chưa có sách. Hãy upload file PDF.")

    st.markdown("---")
    st.subheader("⚙️ Cấu hình")
    topic = st.text_input("Chủ đề", placeholder="z.B. Umweltschutz")
    
    check_vocab = st.checkbox("Từ vựng (C1)", value=True)
    check_full_script = st.checkbox("Bài nói hoàn chỉnh", value=True)
    check_transkript = st.checkbox("Transkript", value=True)

# === CỘT PHẢI: XỬ LÝ AI ===
with col2:
    if st.button("🚀 Tạo bài (Generieren)", type="primary"):
        if not api_key:
            st.error("⚠️ Chưa nhập API Key!")
        elif not current_text:
            st.warning("⚠️ Chưa có tài liệu tham khảo!")
        elif not topic:
            st.warning("⚠️ Chưa nhập chủ đề!")
        else:
            try:
                # CẤU HÌNH AI
                genai.configure(api_key=api_key)
                # Dùng model chuẩn: gemini-1.5-flash
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Du bist ein C1-Prüfer. Thema: '{topic}'.
                QUELLE: {current_text[:40000]}
                AUFGABE: Erstelle Lernmaterialien basierend auf der Quelle.
                """
                if check_vocab: prompt += "\n1. Wortschatz (C1) mit Erklärungen."
                if check_full_script: prompt += "\n2. Vortrag (mit Vertiefung der Argumente)."
                if check_transkript: prompt += "\n3. Natürliches Transkript."

                with st.spinner("AI đang soạn bài..."):
                    response = model.generate_content(prompt)
                    st.success("Xong!")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Lỗi: {e}")
                if "404" in str(e):
                    st.info("💡 Mẹo: Kiểm tra lại API Key xem đã đúng chưa.")
