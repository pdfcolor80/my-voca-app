import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 레이아웃
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 탭 위치 고정 및 모바일 최적화 스타일
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* 전체 컨테이너 여백 조정 */
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }

    /* 카드 컨테이너: 높이를 일정하게 고정하여 버튼 밀림 방지 */
    .study-card {
        background-color: #ffffff;
        padding: 30px 20px;
        border-radius: 25px;
        border: 1px solid #dee2e6;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 320px; /* 카드 높이 고정 */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .eng-text { color: #D32F2F; font-size: 2.4rem; font-weight: bold; line-height: 1.2; }
    .sound-text { color: #2E7D32; font-size: 1.2rem; margin-top: 8px; font-weight: 500; }
    
    /* 뜻 영역: 공간은 차지하되 안 보일 때는 투명하게 처리하여 위치 유지 */
    .mean-box { 
        padding: 15px; 
        border-radius: 15px; 
        margin-top: 15px;
        min-height: 100px; /* 뜻 상자 높이 고정 */
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
    
    /* 버튼 스타일: 화면 하단에 항상 같은 크기로 고정 */
    .stButton>button { 
        width: 100%; 
        height: 4.5rem; /* 버튼 높이 충분히 확보 */
        font-size: 1.4rem !important; 
        border-radius: 20px; 
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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

    # 카드 섹션 (뜻이 없을 때도 공간을 차지하게 함)
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
        
        # [뜻 확인하기] 버튼
        if st.button("💡 뜻 확인하기", type="secondary"):
            st.session_state.show_answer = True
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
        
        # [다음 문장으로] 버튼 (위 버튼과 동일한 위치)
        if st.button("다음 문장으로 👉", type="primary"):
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