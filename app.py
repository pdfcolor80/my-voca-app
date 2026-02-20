import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 레이아웃
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS 및 JavaScript (음성 출력을 위한 스크립트 포함)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }

    .study-card {
        background-color: #ffffff;
        padding: 30px 20px;
        border-radius: 25px;
        border: 1px solid #dee2e6;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .eng-text { color: #D32F2F; font-size: 2.4rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #2E7D32; font-size: 1.2rem; margin-top: 8px; font-weight: 500; }
    
    .mean-box { 
        padding: 15px; 
        border-radius: 15px; 
        margin-top: 15px;
        min-height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .mean-visible { 
        background-color: #E3F2FD; 
        border: 2px solid #2196F3;
        width: 100%;
    }
    .mean-text { color: #1565C0; font-size: 1.8rem; font-weight: bold; }
    .label { color: #adb5bd; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    
    .stButton>button { 
        width: 100%; 
        height: 4.5rem; 
        font-size: 1.4rem !important; 
        border-radius: 20px; 
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 음성 출력을 위한 자바스크립트 함수
def speak(text):
    js_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "{text}";
        msg.lang = "en-US";
        msg.rate = 0.9;
        window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if "|" in line]

def save_progress(index):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except: return 0
    return 0

sentences = load_sentences()

if "current_idx" not in st.session_state:
    st.session_state.current_idx = load_progress()
if "show_answer" not in st.session_state:
    st.session_state.show_answer = False
if "count" not in st.session_state:
    st.session_state.count = 0

# --- 학습 화면 ---
if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    st.progress(st.session_state.current_idx / len(sentences))
    st.caption(f"진도: {st.session_state.current_idx}/1000 | 오늘 학습: {st.session_state.count}")

    if not st.session_state.show_answer:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English Pattern</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box" style="border: 2px dashed #eee;">
                <span style="color: #eee;">탭하여 확인</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💡 뜻 확인 (소리 재생)", type="secondary"):
            st.session_state.show_answer = True
            speak(eng) # 영어 읽어주기
            st.rerun()
    else:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English Pattern</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box mean-visible">
                <div class="mean-text">{mean}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("다음 문장으로 👉", type="primary"):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            st.session_state.show_answer = False
            save_progress(st.session_state.current_idx)
            st.rerun()

    with st.sidebar:
        st.header("⚙️ 관리")
        if st.button("🔄 학습 기록 초기화"):
            st.session_state.current_idx = 0
            st.session_state.count = 0
            st.session_state.show_answer = False
            save_progress(0)
            st.rerun()
else:
    st.balloons()
    st.success("🎉 모든 문장을 완료했습니다!")