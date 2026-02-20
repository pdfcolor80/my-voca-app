import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 레이아웃
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 모바일 탭 학습을 위한 최적화 스타일
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    
    /* 카드 컨테이너 */
    .study-card {
        background-color: #ffffff;
        padding: 40px 20px;
        border-radius: 25px;
        border: 1px solid #dee2e6;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 영어를 최상단에 가장 크게 */
    .eng-text { color: #D32F2F; font-size: 2.5rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #2E7D32; font-size: 1.3rem; margin-top: 8px; margin-bottom: 20px; font-weight: 500; }
    
    /* 뜻 영역 */
    .mean-box { 
        background-color: #E3F2FD; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #2196F3;
        margin-top: 15px;
    }
    .mean-text { color: #1565C0; font-size: 2.0rem; font-weight: bold; }
    
    .label { color: #adb5bd; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; 
        height: 3.8rem; 
        font-size: 1.2rem !important; 
        border-radius: 15px; 
        font-weight: bold;
        transition: 0.2s;
    }
    .stButton>button:active { transform: scale(0.98); }
    </style>
    """, unsafe_allow_html=True)

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
    
    # 상단 진행바
    progress_val = st.session_state.current_idx / len(sentences)
    st.progress(progress_val)
    st.caption(f"진도: {st.session_state.current_idx}/1000 | 오늘 학습: {st.session_state.count}")

    # 메인 카드 영역
    if not st.session_state.show_answer:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div style="color: #ced4da; margin-top: 15px; font-size: 0.9rem;">탭하여 뜻 확인</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💡 뜻 확인하기 (Tab)", type="secondary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box">
                <div class="label">Meaning</div>
                <div class="mean-text">{mean}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("다음 문장으로 👉 (Next)", type="primary"):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            st.session_state.show_answer = False
            save_progress(st.session_state.current_idx)
            st.rerun()

    # 사이드바
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
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()