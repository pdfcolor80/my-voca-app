import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 레이아웃
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 모바일 탭 학습을 위한 고급 스타일
st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    
    /* 카드 컨테이너 */
    .study-card {
        background-color: #ffffff;
        padding: 50px 20px;
        border-radius: 30px;
        border: 2px solid #e0e0e0;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: 0.3s;
    }
    
    /* 영어를 최상단에 가장 크게 */
    .eng-text { color: #D32F2F; font-size: 2.8rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #388E3C; font-size: 1.4rem; margin-top: 10px; margin-bottom: 20px; }
    
    /* 뜻 영역: 탭하기 전에는 숨겨진 느낌 부여 */
    .mean-box { 
        background-color: #E3F2FD; 
        padding: 25px; 
        border-radius: 20px; 
        border: 2px solid #2196F3;
        margin-top: 20px;
    }
    .mean-text { color: #1565C0; font-size: 2.2rem; font-weight: bold; }
    
    .label { color: #bbb; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
    
    /* 하단 버튼 스타일 */
    .stButton>button { 
        width: 100%; 
        height: 4rem; 
        font-size: 1.3rem !important; 
        border-radius: 20px; 
        font-weight: bold;
        background-color: #212121;
        color: white;
    }
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

# 세션 상태 관리
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
    st.progress(st.session_state.current_idx / len(sentences))
    st.caption(f"진도: {st.session_state.current_idx}/1000 | 오늘 학습: {st.session_state.count}")

    # 1. 메인 카드 (이 영역을 클릭하면 뜻이 나옴)
    # Streamlit의 button은 클릭 시 페이지를 새로고침하므로 이를 활용
    if not st.session_state.show_answer:
        # 뜻 숨김 모드
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English Pattern</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div style="color: #ddd; margin-top: 20px;">👇 아래 버튼을 눌러 뜻 확인</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💡 뜻 확인하기"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # 뜻 표시 모드
        st.markdown(f"""
        <div class="study-card">
            <div class="label">English Pattern</div>
            <div class="eng-text">{eng}</div>
            <div class="sound-text">[{sound}]</div>
            <div class="mean-box">
                <div class="label">Meaning</div>
                <div class="mean-text">{mean}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("다음 문장으로 👉"):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            st.session_state.show_answer = False # 다음 문장은 다시 숨김 상태로
            save_progress(st.session_state.current_idx)
            st.rerun()

    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 옵션")
        if st.button("🔄 처음부터 다시하기"):
            st.session_state.current_idx = 0
            st.session_state.count = 0
            st.session_state.show_answer = False
            save_progress(0)
            st.rerun()

else:
    st.balloons()
    st.success("🎉 1,000문장 정복 완료!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()