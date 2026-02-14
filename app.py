import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Goethe C1 Coach",
    page_icon="🇩🇪",
    layout="wide"
)

# --- TIÊU ĐỀ VÀ GIỚI THIỆU ---
st.title("🇩🇪 Goethe C1 Speaking Generator")
st.markdown("""
> **Công cụ hỗ trợ soạn bài nói chuẩn C1 Goethe.** > *Đặc điểm nổi bật:* Tự động thêm câu "Vertiefung" (đào sâu/giải thích) sau mỗi luận điểm để đạt điểm tối đa tiêu chí Phát triển ý (Inhaltliche Entwicklung).
""")

# --- XỬ LÝ API KEY (TỰ ĐỘNG HOẶC NHẬP TAY) ---
api_key = None

# Kiểm tra xem có Key trong Secrets của Streamlit Cloud không
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Nếu không có, hiện ô nhập ở Sidebar
    with st.sidebar:
        st.header("Cài đặt")
        api_key = st.text_input("Nhập Gemini API Key", type="password")
        st.caption("Nếu deploy lên Streamlit Cloud, hãy thêm key vào phần Secrets để không phải nhập lại.")
        st.markdown("[Lấy API Key miễn phí tại đây](https://aistudio.google.com/app/apikey)")

# --- GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Nhập chủ đề")
    topic = st.text_input("Chủ đề (Thema)", placeholder="z.B. Digitalisierung in der Schule")
    
    st.subheader("2. Chọn nội dung cần tạo")
    st.info("Chọn các phần bạn muốn AI soạn thảo:")
    
    check_vocab = st.checkbox("Từ vựng & Paraphrasing (3 biến thể)", value=True)
    check_grammar = st.checkbox("Ngữ pháp C1 (Nominalisierung...)", value=True)
    check_redemittel = st.checkbox("Mẫu câu dẫn dắt (Redemittel)", value=True)
    check_structure = st.checkbox("Dàn bài chi tiết (Gliederung)", value=True)
    check_full_script = st.checkbox("Bài nói hoàn chỉnh (Vortrag)", value=True)
    check_transkript = st.checkbox("Transkript (Văn phong nói tự nhiên)")

# --- HÀM TẠO PROMPT (CHỈ LỆNH CHO AI) ---
def generate_c1_prompt(topic):
    # Prompt khởi tạo vai trò
    prompt = f"""
    Du bist ein strenger und erfahrener Prüfer für das Goethe-Zertifikat C1.
    Deine Aufgabe ist es, Lernmaterialien für das Thema: '{topic}' zu erstellen.
    
    ---
    ### WICHTIGSTE REGEL (ARGUMENTATIONSTIEFE):
    Jedes Mal, wenn du im "Vollständigen Vortrag" oder in der "Gliederung" eine Meinung, ein Argument oder einen Vor-/Nachteil nennst, musst du **ZWINGEND 1-2 Sätze hinzufügen**, um diesen Punkt zu vertiefen.
    
    *Beispiel für Vertiefung:* - Nicht nur: "Das spart Zeit."
    - Sondern: "Das spart Zeit. **Dies bedeutet konkret, dass Mitarbeiter diese gewonnene Zeit effektiver für komplexe Aufgaben nutzen können, was die Gesamtproduktivität des Unternehmens steigert.**"
    ---

    Bitte erstelle nun folgende Inhalte basierend auf den Anforderungen:
    """

    if check_vocab:
        prompt += """
        \n### 1. WORTSCHATZ & PARAPHRASING (C1-Niveau)
        - Wähle 5-7 anspruchsvolle Begriffe/Nomen-Verb-Verbindungen zum Thema.
        - Gib zu jedem Begriff 3 Synonyme oder Umschreibungen an.
        - Format: **Begriff** -> *Option 1 / Option 2 / Option 3*.
        """
    
    if check_grammar:
        prompt += """
        \n### 2. GRAMMATIK-HIGHLIGHTS
        - Nenne 3 spezifische grammatikalische Strukturen (z.B. Passiversatz, Partizipialattribute, Konjunktiv I), die man bei diesem Thema gut einbauen kann.
        - Gib je ein konkretes Beispielsatz dazu.
        """

    if check_redemittel:
        prompt += """
        \n### 3. REDEMITTEL (STRUKTURIERUNG)
        - Einleitung (Thema vorstellen & Gliederung nennen).
        - Überleitung (zu den Alternativen/Vor-Nachteilen).
        - Abwägen (Einerseits/Andererseits).
        - Eigene Meinung äußern.
        - Schlussfolgerung.
        """

    if check_structure:
        prompt += """
        \n### 4. DETAILLIERTE GLIEDERUNG
        - Erstelle eine Struktur: Einleitung -> Alternativen -> Vor/Nachteile -> Eigene Meinung -> Schluss.
        - Notiere in Stichpunkten die Argumente UND die geplante Vertiefung dazu.
        """

    if check_full_script:
        prompt += """
        \n### 5. VOLLSTÄNDIGER VORTRAG (MUSTERLÖSUNG - SCHRIFTSPRACHE)
        - Schreibe einen flüssigen, akademischen Text (ca. 4 Minuten Sprechzeit).
        - Nutze Nominalstil.
        - **Achte penibel auf die Vertiefungs-Regel (1-2 Erläuterungssätze pro Argument).**
        """

    if check_transkript:
        prompt += """
        \n### 6. TRANSKRIPT (GESPROCHENE SPRACHE)
        - Formuliere den Inhalt von Teil 5 so um, wie man ihn tatsächlich spricht.
        - Nutze Diskurspartikel (z.B. "Nun ja", "Lassen Sie mich überlegen", "Ein wichtiger Punkt ist sicherlich...").
        - Es soll natürlich und authentisch klingen.
        """

    return prompt

# --- XỬ LÝ KHI BẤM NÚT ---
with col2:
    if st.button("🚀 Tạo bài giải C1 (Generieren)", type="primary"):
        if not api_key:
            st.error("⚠️ Vui lòng nhập API Key ở thanh bên trái hoặc cài đặt trong Secrets.")
        elif not topic:
            st.warning("⚠️ Vui lòng nhập chủ đề trước.")
        else:
            try:
                # Cấu hình Gemini
                genai.configure(api_key=api_key)
                
                # Chọn model (Gemini 1.5 Pro hoặc Flash đều tốt cho việc này)
                model = genai.GenerativeModel('gemini-1.5-flash') 
                
                with st.spinner('Đang phân tích chủ đề, tìm từ vựng và xây dựng lập luận...'):
                    # Gọi hàm tạo prompt
                    final_prompt = generate_c1_prompt(topic)
                    
                    # Gửi request lên Google
                    response = model.generate_content(final_prompt)
                    
                    # Hiển thị kết quả
                    st.success("Đã tạo xong! Dưới đây là bài giải của bạn:")
                    st.markdown("---")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
                st.info("Gợi ý: Kiểm tra lại API Key hoặc đường truyền mạng.")
