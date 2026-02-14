import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Goethe C1 AI Coach", page_icon="🇩🇪", layout="wide")

st.title("🇩🇪 Goethe C1 Speaking Generator")
st.markdown("Nhập chủ đề và AI sẽ tự soạn bài nói chuẩn C1 (Tự động chọn Model phù hợp).")

# --- HÀM TỰ ĐỘNG TÌM MODEL (CHỐNG LỖI 404) ---
def get_working_model():
    """Tự động tìm model nào đang hoạt động với Key của bạn"""
    try:
        # Lấy danh sách tất cả model mà Key này được phép dùng
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Ưu tiên tìm các model chat thông dụng
                if 'gemini-1.5-flash' in m.name: return m.name
                if 'gemini-1.5-pro' in m.name: return m.name
                if 'gemini-pro' in m.name: return m.name
        
        # Nếu không tìm thấy tên quen thuộc, lấy đại cái đầu tiên
        return 'models/gemini-pro' 
    except:
        return 'gemini-pro' # Fallback cuối cùng

# --- XỬ LÝ API KEY ---
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    with st.sidebar:
        st.header("🔑 Cài đặt")
        api_key = st.text_input("Nhập API Key:", type="password")
        st.caption("Key lấy tại aistudio.google.com")

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Nhập chủ đề")
    topic = st.text_input("Thema:", placeholder="z.B. Digitalisierung, Klimawandel...")
    
    st.markdown("---")
    st.subheader("2. Tùy chọn nội dung")
    check_vocab = st.checkbox("Từ vựng C1 & Paraphrasing", value=True)
    check_grammar = st.checkbox("Ngữ pháp C1", value=True)
    check_structure = st.checkbox("Dàn bài (Gliederung)", value=True)
    check_full_script = st.checkbox("Bài nói hoàn chỉnh", value=True)
    check_transkript = st.checkbox("Transkript (Văn nói)", value=True)

# --- XỬ LÝ AI ---
with col2:
    if st.button("🚀 Tạo bài (Generieren)", type="primary"):
        if not api_key:
            st.error("⚠️ Chưa nhập API Key.")
        elif not topic:
            st.warning("⚠️ Chưa nhập chủ đề.")
        else:
            try:
                # 1. Cấu hình
                genai.configure(api_key=api_key)
                
                # 2. Tự động chọn model
                with st.spinner("Đang kết nối Google và tìm model..."):
                    model_name = get_working_model()
                    model = genai.GenerativeModel(model_name)
                    st.toast(f"Đang dùng model: {model_name}") # Hiển thị tên model đang dùng
                
                # 3. Tạo Prompt
                prompt = f"""
                Du bist ein C1-Prüfer für Deutsch. Thema: '{topic}'.
                Erstelle Lernmaterialien für einen 4-minütigen Vortrag.
                
                WICHTIG: Jedes Argument muss mit 1-2 Sätzen vertieft werden (Erklärung/Beispiel).
                
                Erstelle bitte:
                """
                if check_vocab: prompt += "\n- C1 Wortschatz mit Synonymen."
                if check_grammar: prompt += "\n- C1 Grammatik-Strukturen mit Beispielen."
                if check_structure: prompt += "\n- Gliederung (Einleitung, Pro/Contra, Meinung, Schluss)."
                if check_full_script: prompt += "\n- Vollständigen Vortragstext (Akademisch, mit Vertiefung)."
                if check_transkript: prompt += "\n- Transkript in gesprochener Sprache."

                # 4. Gửi lệnh
                with st.spinner("AI đang viết bài..."):
                    response = model.generate_content(prompt)
                    st.success("Hoàn tất!")
                    st.markdown(response.text)
            
            except Exception as e:
                st.error(f"Lỗi: {e}")
                st.info("Gợi ý: Nếu vẫn lỗi, hãy thử tạo một API Key MỚI TINH ở dự án mới.")
