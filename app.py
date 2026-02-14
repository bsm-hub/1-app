import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Goethe C1 Library", page_icon="📚", layout="wide")
DB_FOLDER = "knowledge_base"

# Tạo thư mục database nếu chưa có
if not os.path.exists(DB_FOLDER):
    try:
        os.makedirs(DB_FOLDER)
    except:
        pass

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

def save_to_db(filename, text):
    try:
        clean_name = filename.rsplit('.', 1)[0]
        file_path = os.path.join(DB_FOLDER, f"{clean_name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        return clean_name
    except:
        return filename

def load_from_db(filename):
    try:
        file_path = os.path.join(DB_FOLDER, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def get_saved_books():
    try:
        return [f for f in os.listdir(DB_FOLDER) if f.endswith(".txt")]
    except:
        return []

# --- 3. XỬ LÝ API KEY ---
# Tự động ưu tiên lấy Key từ Secrets hoặc nhập tay
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

# --- 4. GIAO DIỆN CHÍNH ---
st.title("📚 Goethe C1 Coach (Fixed Version)")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# === CỘT TRÁI: DỮ LIỆU ===
with col1:
    st.subheader("📂 Tài liệu")
    mode = st.radio("Nguồn:", ["Dùng sách đã lưu", "Upload sách mới"])
    current_text = ""
    current_book_name = ""

    if mode == "Upload sách mới":
        uploaded_file = st.file_uploader("Upload PDF:", type=["pdf"])
        if uploaded_file:
            with st.spinner("Đang xử lý..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                if raw_text:
                    saved_name = save_to_db(uploaded_file.name, raw_text)
                    st.success(f"Đã lưu: {saved_name}")
                    current_text = raw_text
                    current_book_name = saved_name
    else:
        saved_books = get_saved_books()
        if saved_books:
            selected_file = st.selectbox("Chọn sách:", saved_books)
            if selected_file:
                current_text = load_from_db(selected_file)
                current_book_name = selected_file.replace(".txt", "")
                st.info(f"Đang dùng: {current_book_name}")
        else:
            st.warning("Chưa có sách nào.")

    st.markdown("---")
    st.subheader("⚙️ Cấu hình")
    topic = st.text_input("Chủ đề", placeholder="z.B. Umweltschutz")
    check_vocab = st.checkbox("Từ vựng", value=True)
    check_full_script = st.checkbox("Bài hoàn chỉnh", value=True)
    check_transkript = st.checkbox("Transkript", value=True)

# === CỘT PHẢI: XỬ LÝ AI ===
with col2:
    if st.button("🚀 Tạo bài (Generieren)", type="primary"):
        if not api_key:
            st.error("⚠️ Thiếu API Key!")
        elif not current_text:
            st.warning("⚠️ Chưa chọn sách!")
        elif not topic:
            st.warning("⚠️ Chưa nhập chủ đề!")
        else:
            try:
                # CẤU HÌNH AI
                genai.configure(api_key=api_key)
                
                # SỬ DỤNG MODEL CHUẨN NHẤT: gemini-1.5-flash
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Du bist ein C1-Prüfer. Thema: '{topic}'.
                QUELLE: {current_text[:40000]}
                AUFGABE: Erstelle Lernmaterialien basierend auf der Quelle.
                """
                if check_vocab: prompt += "\n1. Wortschatz (C1) mit Erklärungen."
                if check_full_script: prompt += "\n2. Vortrag (mit Vertiefung der Argumente)."
                if check_transkript: prompt += "\n3. Natürliches Transkript."

                with st.spinner("AI đang viết bài..."):
                    response = model.generate_content(prompt)
                    st.success("Hoàn tất!")
                    st.markdown(response.text)
                    
            except Exception as e:
                # Bắt lỗi 404 và hướng dẫn cụ thể
                if "404" in str(e):
                    st.error("❌ LỖI API KEY KHÔNG HỢP LỆ (404)")
                    st.error("Nguyên nhân: Bạn đang dùng Key cũ hoặc Key của Google Cloud.")
                    st.info("👉 Cách sửa: Hãy vào aistudio.google.com tạo Key mới và nhập lại.")
                else:
                    st.error(f"Lỗi khác: {e}")
