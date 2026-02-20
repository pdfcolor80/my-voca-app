import streamlit as st
import os

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 가독성 및 디자인 최적화
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .study-card {
        background-color: #ffffff;
        padding: 30px 20px;
        border-radius: 25px;
        border: 1px solid #dee2e6;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .eng-text { color: #D32F2F; font-size: 2.4rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #2E7D32; font-size: 1.2rem; margin-top: 8px; font-weight: 500; }
    
    .mean-box { 
        padding: 15px; 
        border-radius: 15px; 
        margin-top: 20px;
        background-color: #E3F2FD; 
        border: 2px solid #2196F3;
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 2rem; font-weight: bold; }
    .label { color: #adb5bd; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; 
        height: 4.5rem; 
        font-size: 1.5rem !important; 
        border-radius: 20px; 
        font-weight: bold;
        background-color: #212121;
        color: white;
    }
    
    /* 안내 메시지 스타일 */
    .info-text { color: #FF9800; font-weight: bold; margin-top: 10px; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    valid_sentences = []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 4: valid_sentences.append(parts[:4])
    return valid_sentences

def save_progress(index):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except: return 0
    return 0

sentences = load_sentences()

if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()

# --- 메인 학습 화면 ---
if sentences and st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    st.progress(st.session_state.current_idx / len(sentences))
    st.caption(f"Progress: {st.session_state.current_idx}/1000")

    # 카드 표시
    st.markdown(f"""
    <div class="study-card">
        <div class="label">{kind}</div>
        <div class="eng-text">{eng}</div>
        <div class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div class="info-text">🔊 원어민 소리 후 따라 읽으세요 (5회)</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 쉐도잉 학습용 자바스크립트
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function shadowSpeaking() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_eng}");
            msg.lang = 'en-US';
            msg.rate = 0.85; // 따라하기 편하게 살짝 천천히
            
            var count = 0;
            msg.onend = function() {{
                count++;
                if (count < 5) {{
                    // 1.5초(1500ms) 대기 후 다음 소리 재생 (내가 말할 시간)
                    setTimeout(function() {{
                        window.speechSynthesis.speak(msg);
                    }}, 1500);
                }}
            }};
            window.speechSynthesis.speak(msg);
        }}
        shadowSpeaking();
        </script>
    """, height=0)

    # 다음 문장 버튼
    if st.button("다음 문장으로 👉"):
        st.session_state.current_idx += 1
        save_progress(st.session_state.current_idx)
        st.rerun()

else:
    st.balloons()
    st.success("🎉 모든 문장을 완료했습니다!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()

with st.sidebar:
    if st.button("🔄 기록 초기화"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()