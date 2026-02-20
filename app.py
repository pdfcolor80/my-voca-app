import streamlit as st
import os

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 영어 한 줄 출력 및 디자인 최적화
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .study-card {
        background-color: #ffffff;
        padding: 40px 15px;
        border-radius: 30px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden; /* 영역 밖으로 나가는 것 방지 */
    }
    
    /* 영어 한 줄 유지 및 크기 최적화 */
    .eng-text { 
        color: #D32F2F; 
        font-size: 2.1rem; /* 한 줄에 최대한 들어가도록 크기 소폭 조정 */
        font-weight: bold; 
        line-height: 1.1; 
        margin-bottom: 10px;
        white-space: nowrap; /* 줄바꿈 방지 */
        overflow: hidden;
        text-overflow: ellipsis; /* 너무 길면 끝에 ... 표시 */
    }
    
    .sound-text { color: #388E3C; font-size: 1.3rem; margin-top: 5px; font-weight: 500; opacity: 0.8; }
    
    .mean-box { 
        padding: 20px; 
        border-radius: 20px; 
        margin-top: 25px;
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB;
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 2.0rem; font-weight: bold; }
    
    .label { color: #adb5bd; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    
    .stButton>button { 
        width: 100%; 
        height: 4.8rem; 
        font-size: 1.5rem !important; 
        border-radius: 25px; 
        font-weight: bold;
        background: linear-gradient(135deg, #424242 0%, #212121 100%);
        color: white;
        border: none;
    }
    
    .shadow-info { 
        color: #FF6D00; 
        font-weight: bold; 
        margin-top: 15px; 
        font-size: 1.0rem;
        background-color: #FFF3E0;
        padding: 8px;
        border-radius: 10px;
    }
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
    
    st.markdown(f"""
    <div class="study-card">
        <div class="label">{kind}</div>
        <div class="eng-text">{eng}</div>
        <div class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="mean-text">{mean}</div>
        </div>
        <div class="shadow-info">📢 0.7배속 연음 듣고 5회 따라하기</div>
    </div>
    """, unsafe_allow_html=True)

    # 🔊 0.7배속 + 5회 반복 + 2초 대기 JavaScript
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function shadowSpeaking() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_eng}");
            msg.lang = 'en-US';
            msg.rate = 0.7; 
            
            var count = 0;
            msg.onend = function() {{
                count++;
                if (count < 5) {{
                    setTimeout(function() {{
                        window.speechSynthesis.speak(msg);
                    }}, 2000);
                }}
            }};
            window.speechSynthesis.speak(msg);
        }}
        shadowSpeaking();
        </script>
    """, height=0)

    if st.button("다음 문장으로 👉"):
        st.session_state.current_idx += 1
        save_progress(st.session_state.current_idx)
        st.rerun()

else:
    st.balloons()
    st.success("🎉 1,000문장 정복 완료!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()

with st.sidebar:
    st.write(f"진행도: {st.session_state.current_idx + 1} / {len(sentences)}")
    if st.button("🔄 기록 초기화"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()