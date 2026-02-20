import streamlit as st
import os
import time

# 파일 경로 설정
DATA_FILE = "sentences.txt"
SAVE_FILE = "progress.txt"

# 모바일 최적화 설정
st.set_page_config(page_title="영어 패턴 1000", layout="centered")

# CSS: 모바일 전용 스타일 (영어를 가장 크고 위로)
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .stProgress { height: 10px; }
    
    /* 학습 카드 디자인 */
    .mobile-card {
        background-color: #ffffff;
        padding: 20px 15px;
        border-radius: 20px;
        border: 2px solid #f0f2f6;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    
    /* 영어를 가장 크게, 최상단에 배치 */
    .eng-text { color: #E53935; font-size: 2.2rem; font-weight: bold; line-height: 1.2; margin-bottom: 5px; }
    .sound-text { color: #43A047; font-size: 1.2rem; margin-bottom: 20px; }
    
    /* 뜻은 가독성 좋게 중간 크기로 */
    .mean-box { background-color: #E3F2FD; padding: 12px; border-radius: 12px; margin-top: 10px; }
    .mean-text { color: #1565C0; font-size: 1.6rem; font-weight: bold; }
    
    .label { color: #bdbdbd; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }
    
    /* 버튼 크기 키우기 */
    .stButton>button { height: 3em; font-size: 1.1rem !important; border-radius: 12px; }
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
if "count" not in st.session_state:
    st.session_state.count = 0

# --- 메인 학습 화면 ---
if st.session_state.current_idx < len(sentences):
    kind, eng, sound, mean = sentences[st.session_state.current_idx]
    
    # 상단 정보
    st.progress(st.session_state.current_idx / len(sentences))
    
    # 1. 텍스트 카드 (영어 -> 발음 -> 뜻)
    st.markdown(f"""
    <div class="mobile-card">
        <div class="label">English</div>
        <div class="eng-text">{eng}</div>
        <div class="sound-text">[{sound}]</div>
        <div class="mean-box">
            <div class="label">Meaning</div>
            <div class="mean-text">{mean}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 이미지 영역 (연결 거부 없는 안정적인 이미지 소스)
    # 문장의 핵심 단어를 추출하여 이미지를 가져옵니다.
    search_term = eng.replace("(", "").replace(")", "").split()[-1] 
    image_url = f"https://loremflickr.com/g/600/400/{search_term},people/all?lock={st.session_state.current_idx}"
    st.image(image_url, use_column_width=True, caption="상황 연상 이미지")

    st.write("")

    # 3. 제어 버튼
    auto_mode = st.sidebar.toggle("🤖 자동 넘김")
    if not auto_mode:
        if st.button("다음 문장으로 👉", use_container_width=True):
            st.session_state.current_idx += 1
            st.session_state.count += 1
            save_progress(st.session_state.current_idx)
            st.rerun()
    else:
        delay = st.sidebar.slider("간격(초)", 3, 15, 5)
        st.caption(f"⏱ {delay}초 후 자동으로 다음 문장으로 넘어갑니다.")
        time.sleep(delay)
        st.session_state.current_idx += 1
        st.session_state.count += 1
        save_progress(st.session_state.current_idx)
        st.rerun()

    # 하단 상태창
    st.sidebar.write(f"오늘 학습: {st.session_state.count}")
    if st.sidebar.button("🔄 처음부터 다시하기"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()

else:
    st.balloons()
    st.success("1,000문장 학습 완료!")
    if st.button("처음부터 다시 시작"):
        st.session_state.current_idx = 0
        save_progress(0)
        st.rerun()